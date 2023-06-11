from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Category(models.Model) :
    class Meta :
        verbose_name_plural = 'categories'
        ordering = ('name',)
        
    name = models.CharField(max_length=70, null=False, blank=False)

    def __str__(self) :
        return self.name 
    

class Photo(models.Model) :
    description = models.TextField(max_length=500, null=False, blank=False)
    # when a category is deletd, photos are not their category is set to null
    category = models.ForeignKey(Category, related_name="photos", on_delete=models.SET_NULL, null=True)
    image = models.ImageField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="photos", on_delete=models.CASCADE)
    number_of_likes = models.IntegerField(null=False, default=0)

    def __str__(self) :
        return self.description
