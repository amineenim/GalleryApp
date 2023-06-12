from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from photoshare.models import Photo
from .models import Like
# Create your views here.

# view that handles diplaying likes for a given Photo 
def likes_per_photo(request, photo_id) :
    return render(request, 'likes/likes_per_photo.html', {'id' : photo_id})


# view that handles the form to add a new like to a photo 
def add_like(request, photo_id) :
    photo = get_object_or_404(Photo, pk=photo_id)
    #return render(request, 'likes/add_like.html', {'photo' : photo})
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
        
