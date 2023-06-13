import datetime
from django.db import models
from photoshare.models import Photo
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import admin
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
        ordering = ('-created_at',)
        
    comment_text = models.CharField(max_length=400, blank=False, null=False)
    photo = models.ForeignKey(Photo, related_name='comments', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) :
        return self.comment_text
    
    
    @admin.display(
            boolean=False,
            ordering="-created_at",
            description="published since"
    )

    def get_when_created(self):
        time_now = timezone.now()
        if time_now - datetime.timedelta(days=1) <= self.created_at <= time_now:
            if time_now - datetime.timedelta(hours=1) <= self.created_at:
                difference = time_now - self.created_at
                difference_in_seconds = difference.total_seconds()
                difference_in_minutes = int(difference_in_seconds // 60)
                if difference_in_minutes == 0:
                    seconds = int(difference_in_seconds % 60)
                    return f"{seconds} seconds ago"
                return f"{difference_in_minutes} minutes ago"
            else:
                difference = time_now - self.created_at
                difference_in_seconds = difference.total_seconds()
                hours = int(difference_in_seconds // 3600)
                if hours == 1:
                    return f"1 hour ago"
                return f"{hours} hours ago"
        elif time_now - datetime.timedelta(days=2) <= self.created_at <= time_now - datetime.timedelta(days=1):
            return "yesterday"
        else:
            return self.created_at

