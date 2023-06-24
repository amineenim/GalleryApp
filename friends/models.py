from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# class that represents a FriendshipRequest Object 
class FriendshipRequest(models.Model) :
    initiated_by = models.ForeignKey(User, related_name='my_sent_requests', on_delete=models.CASCADE, null=False, blank=False)
    sent_to = models.ForeignKey(User, related_name='my_received_requests', on_delete=models.CASCADE, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(null=False, blank=False, default=False)


    def __str__(self) :
        return self.initiated_by.username + ' sent a request to ' + self.sent_to.username 
    
