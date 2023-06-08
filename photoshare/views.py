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
    # verify if there'a a category set 
    if request.GET.get('category') != '' and request.GET.get('category') is not None :
        selected_category = Category.objects.filter(name= request.GET.get('category'))[0]
        photos = photos.filter(category = selected_category)
        context = {'categories' : categories, 'photos' : photos, 'category' : selected_category }
        return render(request, 'photoshare/gallery.html', context)
   
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
    

# view that handles deleting a given photo resource
def deletePhoto(request, pk) :
    photo_to_delete = get_object_or_404(Photo, pk=pk)
    if request.method == "POST" :
        photo_to_delete.delete()
        messages.success(request, "Photo deleted with success !")
        return redirect('gallery')
    return render(request, 'photoshare/delete.html', {"photo" : photo_to_delete})
    