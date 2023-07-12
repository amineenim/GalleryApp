from django import forms
from .models import Photo, Category
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

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


class CreateUserForm(UserCreationForm) :
    class Meta :
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    email = forms.EmailField(label='Email Address',help_text='Address must contain @', widget=forms.EmailInput(attrs={
        'class' : "w-full py-2 pl-4 border rounded-xl",
        'placeholder' : "Enter your email"
    }))

    username = forms.CharField(label='Username',max_length=40, help_text="username can't exceed 40 characters",widget=forms.TextInput(attrs={
        'class' : "w-full py-2 pl-4 border rounded-xl",
        'placeholder' : "Enter your username"
    }))

    help_password =  "Your password can’t be too similar to your other personal information, Your password must contain at least 8 characters."

    password1 = forms.CharField(label='Password', help_text=help_password, widget=forms.PasswordInput(attrs={
        'class' : "w-full py-2 pl-4 border rounded-xl",
        'placeholder' : "Enter your Password"
    }))

    password2 = forms.CharField(label='Password confirmation', help_text="Enter the same password as before, for verification", widget=forms.PasswordInput(attrs={
        'class' : "w-full py-2 pl-4 border rounded-xl",
        'placeholder' : "Confirm your password"
    }))