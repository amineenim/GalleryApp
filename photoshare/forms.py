from django import forms
from .models import Photo 
from .models import Category

class PhotoForm(forms.ModelForm) :
    class Meta :
        model = Photo
        fields = ('category', 'image', 'description')


        widgets = {
            'category' : forms.Select(attrs={
                'class' : "rounded-xl border py-2 pl-4 mt-1 w-full"
            })
        }
 
    image = forms.ImageField(label='image :',widget=forms.FileInput(attrs={
        'class' : "w-full rounded-xl ml-6 border mt-1"
    }))

    description= forms.CharField(label='description :',widget=forms.Textarea(attrs={
        'placeholder' : 'Type in the description for your image',
        'class' : "w-full rounded-xl border py-4 px-5 resize-none mt-1"
    }))


class EditPhotoForm(forms.ModelForm) : 
    class Meta :
        model = Photo 
        fields = ('description',)

    
    description = forms.CharField(widget=forms.Textarea(attrs={
        'class' : "w-full rounded-xl border py-4 px-5 resize-none mt-2"
    }))