from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
# Create your models here.

class UserProfile(models.Model) :
    
    first_name = models.CharField(blank=True, null=True, max_length=100)
    last_name = models.CharField(blank=True, null=True, max_length=100)
    birthdate = models.DateField(blank=True, null=True)
    bio = models.CharField(max_length=300, null=True, blank=True)
    user = models.ForeignKey(User, related_name='profile_data', on_delete=models.CASCADE)
    profile_picture = models.ImageField(blank=True, null=True, upload_to='profile/')
    country = CountryField(default='US')
    
    def __str__(self) :
        return self.first_name + self.last_name
