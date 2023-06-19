from datetime import date, timedelta
from django import forms 
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, FileExtensionValidator
from .models import UserProfile
from django_countries.fields import CountryField



class UserProfileCreateForm(forms.Form) :
    class Meta :
        model = UserProfile
        fields = '__all__'
    
    MAX_SIZE = 2 * 1024 * 1024 
    
    def clean_profile_picture(self) :
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture and profile_picture.size > self.MAX_SIZE :
            raise forms.ValidationError(f"the image size can't exceed {self.MAX_SIZE} bytes")
        return profile_picture
    
    def validate_birthdate(value) :
        min_age = date.today() - timedelta(days=365*5)
        if value < min_age :
            raise('must be at least 5 years')
        

    first_name = forms.CharField(label='First Name', max_length=100, widget=forms.TextInput(attrs={
        'class' : "w-full py-2 pl-3 border rounded-xl",
        'placeholder' : 'Your First name'
    }))
    last_name = forms.CharField(label='Last Name', max_length=100, widget=forms.TextInput(attrs={
        'class' : "w-full py-2 pl-3 border rounded-xl", 
        'placeholder' : 'Your Last name'
    }))
    birthdate = forms.DateField(label='Date of birth',
                                help_text='Please enter you birth date in the format dd/mm/YYYY', 
                                widget=forms.DateInput(attrs={
                                    'class' : 'w-full rounded-xl border py-2 px-3',
                                    'type' : 'date'
                                }))
    bio = forms.CharField(label='Little description about yourself', widget=forms.Textarea(attrs={
        'class' : "w-full resize-none rounded-xl border p-3",
        'placeholder' : 'Tell us a little bit about you',
        'rows' : 6
    }))
    profile_picture = forms.ImageField(label='Profile Picture',
                                       help_text='Upload a profile picture up to 2MB',
                                       widget=forms.FileInput(attrs={
                                           'class' : "w-1/2",
                                           'accept' : 'image/*'
                                       }),
                                       validators=[FileExtensionValidator(['jpeg', 'png', 'jpg'], 'Unvalid file format')])
    country = CountryField().formfield(widget=forms.Select(attrs={
        'class' : "w-full py-2 px-3 border rounded-xl"
    }))