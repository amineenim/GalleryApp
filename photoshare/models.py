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
    
    def get_not_hidden_comments(self) :
        return self.comments.filter(is_hidden=False)

class PasswordResetToken(models.Model) :
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_reset_password_token')
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()


class EmailVerificationToken(models.Model) :
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=False, related_name='email_verification_tokens')
    token = models.CharField(max_length=255, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    expires_at = models.DateTimeField(null=False)
    