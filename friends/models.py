from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.utils import timezone
# Create your models here.

# class that represents a FriendshipRequest Object 
class FriendshipRequest(models.Model) :
    initiated_by = models.ForeignKey(User, related_name='my_sent_requests', on_delete=models.CASCADE, null=False, blank=False)
    sent_to = models.ForeignKey(User, related_name='my_received_requests', on_delete=models.CASCADE, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(null=False, blank=False, default=False)


    def __str__(self) :
        return self.initiated_by.username + ' sent a request to ' + self.sent_to.username 
    

# class that reprsents a FriendsList object 
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

# class that represents notification linked to friedship 
class FriendshipNotification(models.Model) :
    class Meta :
        ordering = ('-created_at',)
    intended_to = models.ForeignKey(User, related_name='my_friendship_notifications', on_delete=models.CASCADE)
    content = models.CharField(null=False, blank=False, max_length=200)
    created_at = models.DateTimeField()
    is_seen = models.BooleanField(null=False, blank=False, default=False)
    

    def __str__(self) :
        return self.content
    
    def since_when(self) :
        # check if the creation_date is whitin the last 24 hours 
        if timezone.now() - timedelta(days=1) <= self.created_at <= timezone.now() :
            if timezone.now() - timedelta(hours=1) <= self.created_at :
                difference = timezone.now() - self.created_at 
                difference_in_seconds = difference.total_seconds()
                difference_in_minutes =int(difference_in_seconds//60)
                if difference_in_minutes == 0 :
                    return 'a few moments ago' 
                return f"{difference_in_minutes} minutes ago"
            else :
                difference = timezone.now() - self.created_at
                difference_in_seconds = difference.total_seconds()
                difference_in_hours = int(difference_in_seconds//3600)
                if difference_in_hours == 1 :
                    return f"1 hour ago"
                return f"{difference_in_hours} hours ago"
            
        elif timezone.now() - timedelta(days=2) <= self.created_at <= timezone.now() - timedelta(days=1):
            return "Yesterday"
        else :
            return self.created_at 
         

            