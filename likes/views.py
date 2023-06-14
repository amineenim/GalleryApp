from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from photoshare.models import Photo
from .models import Like
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CommentCreateForm
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
            return redirect(reverse('detail_photo', args=(photo.id,)))
        else : 
            # delete the corresponding like object and decrement the number of likes
            like.delete()
            photo.number_of_likes -= 1
            photo.save()
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

        return redirect(reverse('detail_photo', args=(photo.id,)))

# view that handles displaying the comments for a given photo
@login_required
def comments_per_photo(request, photo_id) :
    photo = get_object_or_404(Photo, id=photo_id)
    # check if the user is the owner of the photo 
    if request.user == photo.created_by :
        return render(request, 'likes/comments_per_photo.html', {'photo' : photo})
    
    messages.error(request, 'unauthorized action')
    return redirect(reverse('gallery'))

