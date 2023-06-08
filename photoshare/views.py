from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Photo
from django.contrib import messages
from .forms import PhotoForm, EditPhotoForm

# Create your views here.
# define a namespace for the app 
app_name = 'photoshare'
# the view rendering the gallery page ehere all photos are displayed 
def gellery(request) :
    categories = Category.objects.all()
    photos = Photo.objects.all()
    context = {'categories' : categories, 'photos' : photos}
    return render(request, 'photoshare/gallery.html', context)


# the view handling returning a form to add a new photo
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
def viewPhoto(request, pk) :
    photo = get_object_or_404(Photo, pk=pk)
    return render(request, 'photoshare/photo.html', {'photo' : photo})


# view that handles updating a photo in storage 
def editPhoto(request, pk) :
    # grab the photo to edit 
    photo_to_edit = get_object_or_404(Photo, pk=pk)
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
    
            