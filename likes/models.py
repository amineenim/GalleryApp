from django.db import models
from photoshare.models import Photo
from django.contrib.auth.models import User
# Create your models here.

class Like(models.Model) :
    photo = models.ForeignKey(Photo, related_name='likes', on_delete=models.CASCADE, null=False)
    created_by = models.ForeignKey(User, related_name='user_likes', on_delete=models.SET_NULL, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) :
        return self.photo + ' liked by ' + self.created_by