from django.shortcuts import render, get_object_or_404
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
        # increment the number of likes if the photo isn't already liked by user 
        existing_likes = Like.objects.filter(photo=photo, created_by=request.user)
        if existing_likes.exists():
            photo.number_of_likes -= 1
            print('minus')
        else :
            photo.number_of_likes += 1
            print('plus')
        
        return render(request, 'photoshare/detail_photo.html', {'photo', photo})
    
    elif request.method == "GET" :
        print('0')
        return render(request, 'photoshare/detail_photo.html', {'photo', photo})

