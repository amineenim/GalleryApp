from django.db import models
from photoshare.models import Photo
from django.contrib.auth.models import User
# Create your models here.

class Like(models.Model) :
    photo = models.ForeignKey(Photo, related_name='likes', on_delete=models.CASCADE, null=False)
    created_by = models.ForeignKey(User, related_name='user_likes', on_delete=models.SET_NULL, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) :
        return ' liked by ' + self.created_by.username

# class that represents a Comment Model 

class Comment(models.Model) :
    class Meta :
        ordering = ('created_at',)
        
    comment_text = models.CharField(max_length=400, blank=False, null=False)
    photo = models.ForeignKey(Photo, related_name='comments', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) :
        return self.comment_text
    