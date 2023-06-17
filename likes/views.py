from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from photoshare.models import Photo
from .models import Like, Comment, Notification
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CommentCreateForm, CommentEditForm
# Create your views here.

# view that handles diplaying likes for a given Photo 
@login_required
def likes_per_photo(request, photo_id) :
    # get the photo
    photo = get_object_or_404(Photo, pk=photo_id)
    # check if the photo corresponds to the current user 
    if photo.created_by == request.user :
        # get the likes for the photo 
        likes_for_photo = Like.objects.filter(photo=photo)
        return render(request, 'likes/likes_per_photo.html', {'likes' : likes_for_photo, 'photo' : photo})
    else : 
        messages.error(request, "unauthorized to visit this page")
        return redirect(reverse('gallery'))

# view that handles the form to add a new like to a photo 
@login_required
def add_like(request, photo_id) :
    photo = get_object_or_404(Photo, pk=photo_id)
    # check if the form has been submitted 
    if request.method == "POST" :
        # get or create the like object if already doesn't exist 
        like, created = Like.objects.get_or_create(photo= photo, created_by = request.user)
        if created :
            # increment the number of likes for the photo 
            photo.number_of_likes += 1 
            photo.save()
            # check if the authenticated user is not the owner of the photo
            if request.user != photo.created_by :
                # create a notification for the like 
                notification_text = request.user.username + ' Liked your photo from ' + photo.category.name + ' category.'
                Notification.objects.create(
                    notification=notification_text,
                    created_by = request.user,
                    photo = photo,
                    is_like = True,
                    is_comment = False
                )
            return redirect(reverse('detail_photo', args=(photo.id,)))
        else : 
            # delete the corresponding like object and decrement the number of likes
            like.delete()
            photo.number_of_likes -= 1
            photo.save()
            # delete the corresponding notification for that like 
            corresponding_notification = Notification.objects.filter(created_by=request.user, photo=photo, is_like=True)
            if corresponding_notification :
                corresponding_notification[0].delete()
            return redirect(reverse('detail_photo', args=(photo.id,)))
        
# view that handles clearing nessages
def clear_messages(request) :
    if request.method == "POST" :
        redirect_url = request.POST.get('previous_url')
        storage = messages.get_messages(request)
        storage.used = True
        return redirect(redirect_url)

# view that handles adding a comment to a given Photo
@login_required
def add_comment(request, photo_id) :
    # get the photo instance 
    photo = get_object_or_404(Photo, id=photo_id)
    # check the request method 
    if request.method == "POST" :
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            comment_to_insert = form.save(commit=False)
            comment_to_insert.photo = photo
            comment_to_insert.created_by = request.user
            comment_to_insert.save()
            # create a corresponding notification object for the comment 
            notification_text = request.user.username + ' commented your photo from ' + photo.category.name + ' category.'
            Notification.objects.create(
                notification=notification_text,
                created_by = request.user,
                photo = photo,
                is_like = False,
                is_comment = True
            )
        return redirect(reverse('detail_photo', args=(photo.id,)))

# view that handles displaying the comments for a given photo
@login_required
def comments_per_photo(request, photo_id) :
    photo = get_object_or_404(Photo, id=photo_id)
    # check if the user is the owner of the photo 
    if request.user == photo.created_by or request.user.is_superuser :
        return render(request, 'likes/comments_per_photo.html', {'photo' : photo})
    
    messages.error(request, 'unauthorized action')
    return redirect(reverse('gallery'))

# view that handles editing his own comment 
@login_required
def edit_comment(request, comment_id) :
    comment_to_edit = get_object_or_404(Comment, id=comment_id)
    related_photo = comment_to_edit.photo
    # check if the user is the owner of comment 
    if comment_to_edit.created_by == request.user :
        if request.method == 'GET' :
            form = CommentEditForm(instance=comment_to_edit)
            return render(request, 'likes/edit_comment.html', {'form' : form, 'photo' : related_photo})
        elif request.method == 'POST' :
            form = CommentEditForm(request.POST, instance=comment_to_edit)
            if form.is_valid() :
                form.save()
                return redirect(reverse('likes:comments_per_photo', args=(comment_to_edit.photo.id,)))

    # if the user is not the owner of the comment
    else : 
        messages.error(request, "Unauthorized action")
        return redirect(reverse('gallery'))


# view that handles deleting a comment 
@login_required
def delete_comment(request, comment_id) :
    comment_to_delete = get_object_or_404(Comment, id=comment_id)
    # check if the user is the owner of the comment or if it's an admin
    if comment_to_delete.created_by != request.user and not(request.user.is_superuser):
        messages.error(request, 'Unauthorized action')
        return redirect(reverse('gallery'))
    else :
        comment_to_delete.delete()
        if request.user.is_superuser :
            # delete the corresponding notification for that comment 
            corresponding_notification = Notification.objects.filter(created_by = comment_to_delete.created_by, photo=comment_to_delete.photo, is_comment=True, comment=comment_to_delete)
            if corresponding_notification.exists() :
                corresponding_notification[0].delete()
            return redirect(reverse('likes:comments_per_photo', args=(comment_to_delete.photo.id,)))
        else : 
            # delete the corresponding notification for that comment 
            corresponding_notification = Notification.objects.filter(created_by = request.user, photo=comment_to_delete.photo, is_comment=True, comment=comment_to_delete)
            if corresponding_notification.exists() :
                corresponding_notification[0].delete()
            return redirect(reverse('detail_photo', args=(comment_to_delete.photo.id,)))

# view that handles hiding a comment on one of his photos 
@login_required
def hide_comment(request, comment_id) : 
    # get the comment 
    comment_to_hide = get_object_or_404(Comment, id=comment_id)
    related_photo = comment_to_hide.photo
    # check that the comment belongs to a photo owned by the authenticated user 
    if request.user != comment_to_hide.photo.created_by :
        messages.error(request, 'Unauthorized action')
        return redirect(reverse('gallery'))
    # check if the method is GET 
    if request.method == 'GET' : 
        return render(request, 'likes/hide_comment.html', {'comment' : comment_to_hide, 'photo' : related_photo})
    elif request.method == 'POST' :
        comment_to_hide.is_hidden = True 
        comment_to_hide.save()
        return redirect(reverse('likes:comments_per_photo', args=(comment_to_hide.photo.id,)))
    
# view that allows a user to check if there are any notifications for him
@login_required
def get_notifications(request) :
    # initiate an empty list to store notifications
    user_notifications = []
    # get the photos for tha autheticated user, and grab the notifications related to each of them 
    user_photos = request.user.photos.all()
    for photo in user_photos :
        has_notifications = photo.notifications.exists()
        if has_notifications : 
            photo_notifications = photo.notifications.all()
            for notification in photo_notifications :
                user_notifications.append(notification)
    # after looping over all user's photos and getting notifications for each render the template 
    return render(request, 'likes/notifications.html', {'notifications' : user_notifications})

