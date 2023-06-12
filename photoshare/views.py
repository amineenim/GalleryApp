from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Category, Photo
from django.contrib import messages
from .forms import PhotoForm, EditPhotoForm, CreateUserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from likes.models import Like 

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


# the view rendering the gallery page ehere all photos are displayed 
@login_required
def gellery(request) :
    categories = Category.objects.all()
    photos = Photo.objects.all()
    # verify if there'a a category set 
    if request.GET.get('category') != '' and request.GET.get('category') is not None :
        selected_category = Category.objects.filter(name= request.GET.get('category'))[0]
        photos = photos.filter(category = selected_category)
        context = {'categories' : categories, 'photos' : photos, 'category' : selected_category }
        return render(request, 'photoshare/gallery.html', context)
   
    context = {'categories' : categories, 'photos' : photos}
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
    # get also the likes for the photo to pass it to the form displaying it 
    likes_for_photo = Like.objects.filter(photo=photo, created_by = request.user)
    user_likes_photo = False 
    if likes_for_photo.exists() :
        user_likes_photo = True

    return render(request, 'photoshare/photo.html', {'photo' : photo, 'is_user_likes' : user_likes_photo })


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
