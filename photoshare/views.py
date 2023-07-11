import re
from datetime import timedelta
from django.forms import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Category, Photo, PasswordResetToken
from django.contrib import messages
from .forms import PhotoForm, EditPhotoForm, CreateUserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from likes.models import Like
from likes.forms import CommentCreateForm
from django.core.paginator import Paginator
from friends.models import FriendshipNotification, Conversation, ConversationMessage
from django.db.models import Q 
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
# Create your views here.
# define a namespace for the app 
app_name = 'photoshare'

# view that handles logging in a user 
def loginUser(request) :
    # check if the user is authenticated 
    if request.user.is_authenticated : 
        return redirect('gallery')
    else : 
        # check if the form is submitted 
        if request.method == "GET" :
            return render(request, 'photoshare/login.html')
        elif request.method == "POST" :
            username = request.POST.get('username')
            password = request.POST.get('password')
            if not username or not password :
                error_message = 'both fields are required'
                return render(request, 'photoshare/login.html',{'error_message' : error_message})
            # validate username 
            if len(username) >= 20 :
                error_message = "Username can't exceed 20 characters"
                return render(request, 'photoshare/login.html',{'error_message' : error_message})
            # authenticate the user 
            user = authenticate(request, username=username, password=password)
            if user is None : 
                error_message = "Please check your credentials"
                return render(request, 'photoshare/login.html',{'error_message' : error_message})
            login(request, user)
            messages.success(request, f"Glad to see you again {request.user.username}")
            return redirect('gallery')

# view that handles logging out a user 
@login_required
def logoutUser(request):
    logout(request)
    return redirect('login')

# view that handles registering a user 
def registerUser(request) :
    # check if user is authenticated 
    if request.user.is_authenticated :
        return redirect('gallery')
    else :
        #check if the form has been submitted 
        if request.method == "POST" :
            form = CreateUserForm(request.POST)
            if form.is_valid() :
                user = form.save()
                # associate the permissions to the newly created user 

                login(request, user)
                messages.success(request, f"Glad to have you {request.user.username}, Enjoy our plateform")
                return redirect('gallery')
            
        elif request.method == "GET" :
            form = CreateUserForm()
        
        return render(request, 'photoshare/register.html', {'form' : form})


# the view rendering the gallery page where all photos are displayed 
@login_required
def gellery(request) :
    categories = Category.objects.all()
    # get unseen notifications for user's photos
    user_notifications = []
    user_photos = request.user.photos.all()
    for photo in user_photos :
        if photo.notifications.filter(is_seen=False).exists() :
            photo_notifications = photo.notifications.filter(is_seen=False)
            for notification in photo_notifications :
                user_notifications.append(notification)
    # get notifications for freindship 
    friendship_notifications = FriendshipNotification.objects.filter(intended_to=request.user, is_seen=False)
    # check for user conversations , the user is member of , either member_one or member_two
    user_conversations = Conversation.objects.filter(Q(member_one=request.user) | Q(member_two=request.user))
    conversations_with_unreaad_messages = []
    total_unread = 0
    if user_conversations.exists():
        # see if there are any unread messages 
        for conversation in user_conversations :
            unread_messages_in_conversation = {'conversation' : conversation, 'unread_messages' : 0}
            for message in conversation.messages.all() :
                if message.is_seen == False and message.sent_by != request.user :
                    unread_messages_in_conversation['unread_messages'] +=1 
            conversations_with_unreaad_messages.append(unread_messages_in_conversation)
            total_unread += unread_messages_in_conversation['unread_messages']

    # create a paginator instance
    p = Paginator(Photo.objects.all(), 6)
    page = request.GET.get('page')
    photos = p.get_page(page)
    # verify if there'a a category set 
    if request.GET.get('category') != '' and request.GET.get('category') is not None :
        selected_category = Category.objects.filter(name= request.GET.get('category'))[0]
        p = Paginator(Photo.objects.filter(category=selected_category), 6)
        page = request.GET.get('page')
        photos = p.get_page(page)
        context = {'categories' : categories, 'photos' : photos, 'category' : selected_category,
                   'notifications' : user_notifications, 'friendship_notifications' : friendship_notifications,
                    'unread_messages' : total_unread, 'conversations_with_number_of_unread_messages' : conversations_with_unreaad_messages }
        return render(request, 'photoshare/gallery.html', context)
   
    context = {'categories' : categories, 'photos' : photos, 'notifications' : user_notifications, 
               'friendship_notifications' : friendship_notifications, 'unread_messages' : total_unread, 'conversations_with_number_of_unread_messages' : conversations_with_unreaad_messages}
    return render(request, 'photoshare/gallery.html', context)


# the view handling returning a form to add a new photo
@login_required
def addNew(request):
    # ckeck if the form is submitted 
    if request.method == "POST" :
        form = PhotoForm(request.POST,request.FILES)
        if form.is_valid() :
            photo = form.save(commit=False)
            photo.created_by = request.user
            photo.save()
            messages.success(request, "Photo added with success ")
            #redirect the user back 
            return redirect('gallery')
    else :
        form = PhotoForm()
    return render(request, 'photoshare/new.html', {'form' : form})
            


# the view handling showing a single photo detail 
@login_required
def viewPhoto(request, pk) :
    photo = get_object_or_404(Photo, pk=pk)
    # get the comments form 
    comment_create_form = CommentCreateForm()
    # get also the likes for the photo to pass it to the form displaying it 
    likes_for_photo = Like.objects.filter(photo=photo, created_by = request.user)
    user_likes_photo = False 
    if likes_for_photo.exists() :
        user_likes_photo = True

    return render(request, 'photoshare/photo.html', {'photo' : photo, 'is_user_likes' : user_likes_photo, 'form' : comment_create_form })


# view that handles updating a photo in storage 
@login_required
def editPhoto(request, pk) :
    # grab the photo to edit 
    photo_to_edit = get_object_or_404(Photo, pk=pk)
    # check if the user can edit the given photo or not 
    if request.user == photo_to_edit.created_by or request.user.is_superuser :
        # check to see the request method 
        if request.method == "POST" :
            form = EditPhotoForm(request.POST, instance=photo_to_edit)
            if form.is_valid() :
                form.save()
                messages.success(request, "Photo Modified with success !")
                return redirect('detail_photo', pk=photo_to_edit.id)
                
        elif request.method == "GET" :
            form = EditPhotoForm(instance=photo_to_edit)
            
        return render(request, 'photoshare/edit.html', {'photo' : photo_to_edit, 'form' : form})
    else : 
        return redirect(reverse('detail_photo',args=(photo_to_edit.id,)))
    

# view that handles deleting a given photo resource
@login_required

def deletePhoto(request, pk) :
    photo_to_delete = get_object_or_404(Photo, pk=pk)
    # check if the user owns the photo 
    if request.user == photo_to_delete.created_by or request.user.is_superuser :
        if request.method == "POST" :
            photo_to_delete.delete()
            messages.success(request, "Photo deleted with success !")
            return redirect('gallery')
        return render(request, 'photoshare/delete.html', {"photo" : photo_to_delete})
    else :
        return redirect(reverse('detail_photo', args=(photo_to_delete.id,)))


# view that allow a user to view only his gallery photos 
@login_required
def myGallery(request) :
    # request only photos for the currently authenticated user 
    user_photos = request.user.photos.all()
    context = {'photos' : user_photos}
    return render(request, 'photoshare/my_gallery.html',context)

def get_perms(request) :
    current_user = request.user 
    content_type = ContentType.objects.get_for_model(Photo)
    Permissions = Permission.objects.filter(content_type=content_type, user=current_user)
    return render(request, 'photoshare/perms.html', {'permissions' : Permissions})

# view that handles password forgotten
def reset_password(request) :
    regex_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    # check first if the user is authenticated 
    if request.user.is_authenticated :
        return redirect('gallery')
    else :
        # check if get request
        if request.method == 'GET' :
            # check for token query parameter 
            token = request.GET.get('token')
            if token :
                # get the PasswordResetToken corresponding to the token value 
                try :
                    token_object = PasswordResetToken.objects.get(token=token)
                except PasswordResetToken.DoesNotExist :
                    messages.error(request, 'invalid Token')
                    return redirect(reverse('reset_password'))
                # check if the token has expired 
                if token_object.expires_at < timezone.now() :
                    messages.error(request, 'Token expired, Get a new one to reset your Password')
                    return redirect(reverse('reset_password'))
                # the token is yet valid 
                return render(request, 'photoshare/new_password.html', {'token' : token_object})
             
            return render(request, 'photoshare/password_reset.html')
        elif request.method == 'POST' :
            # check is the form being submitted is the one for password confirmation  
            if request.POST.get('token') :
                # get the user from the hidden field submitted
                user = User.objects.get(username=request.POST.get('user'))
                token_object = PasswordResetToken.objects.get(token=request.POST.get('token'))
                # check for password1 and password2
                if not request.POST.get('password1') or not request.POST.get('password2') :
                    error_message = 'both fields are required'
                    return render(request, 'photoshare/new_password.html', {'error' : error_message,'token' : token_object})
                # validate password1
                password1 = request.POST.get('password1')
                try : 
                    validate_password(password1, user)
                except ValidationError as e :
                    error_messages = list(e.messages)
                    return render(request, 'photoshare/new_password.html', {'errors' : error_messages,'token' : token_object})
                # check password2 matches password1
                password2 = request.POST.get('password2')
                if password1 != password2 :
                    error_message = "The two passwords are not matching"
                    return render(request, 'photoshare/new_password.html', {'error' : error_message,'token' : token_object})
                # now that all is valid store the new password for user 
                user.set_password(password1)
                user.save()
                # delete the token used to reset password
                token_object.delete()
                # authenticate the user 
                user = authenticate(request, username=user.username, password=password1)
                if user is not None :
                    login(request, user)
                    messages.success(request, 'Password reset successefully !')
                    return redirect(reverse('gallery'))
            else :
                # get the email input from user and validate it 
                email_address = request.POST.get('email')
                # check if email is empty
                if not email_address :
                    error_message = 'Enter an email address, empty value submitted'
                    return render(request, 'photoshare/password_reset.html', {'error' : error_message})
                # validate the email 
                if re.match(regex_pattern, email_address) is None :
                    error_message = 'invalid email address'
                    return render(request, 'photoshare/password_reset.html', {'error' : error_message})
                else :
                    # now that the email is valid, get the user who has it 
                    try :
                        user = User.objects.get(email=email_address)
                    except User.DoesNotExist :
                        error_message = 'Given email address does not correspond to a user'
                        return render(request, 'photoshare/password_reset.html', {'error' : error_message})
                    # generate a password reset token 
                    token_generator = PasswordResetTokenGenerator()
                    token = token_generator.make_token(user)
                    # create the PasswordResetToekn object and store it in db 
                    toekn_data = PasswordResetToken.objects.create(
                        user=user,
                        token = token,
                        expires_at = timezone.now() + timedelta(hours=1)
                    )
                    # save it to db
                    toekn_data.save()
                    domain = 'localhost:8000'
                    password_reset_url = f"http://{domain}/gallery/accounts/resetpassword/?token={token}"
                    # send an email to the user with the generated password reset url 
                    email_subject = 'Password Reset'
                    email_message = f"to reset your password, click the following url : {password_reset_url}"
                    from_email = 'aminemaourid1@gmail.com'
                    sent_emails_number = send_mail(subject=email_subject, message=email_message, from_email=from_email, recipient_list=[email_address])
                    if sent_emails_number == 1 :
                        # the email has been successefully delivred to one recipient 
                        succes_message = 'Password reset url sent, check your email'
                        return render(request, 'photoshare/password_reset.html', {'success' : succes_message})
                    else :
                        error_message = 'Oops, something went wrong!'
                        return render(request, 'photoshare/password_reset.html', {'error' : error_message})
                





