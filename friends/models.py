from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
# Create your models here.

# class that represents a FriendshipRequest Object 
class FriendshipRequest(models.Model) :
    initiated_by = models.ForeignKey(User, related_name='my_sent_requests', on_delete=models.CASCADE, null=False, blank=False)
    sent_to = models.ForeignKey(User, related_name='my_received_requests', on_delete=models.CASCADE, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(null=False, blank=False, default=False)


    def __str__(self) :
        return self.initiated_by.username + ' sent a request to ' + self.sent_to.username 
    

# class that reprensts a FriendsList object 
class FriendsList(models.Model) :
    belongs_to = models.OneToOneField(User, on_delete=models.CASCADE)
    friends = models.ManyToManyField(User, related_name='my_friends')

    def __str__(self) :
        return self.belongs_to.username
    
    # customize the apperance for the admin dashboard
    @admin.display(
            boolean=False,
            ordering='-get_number_of_friends',
            description= 'number of friends',
    )
    def get_number_of_friends(self) :
        return self.friends.count()
    