from django.contrib import admin
from .models import FriendshipRequest, FriendsList
# Register your models here.

class FriendshipRequestAdmin(admin.ModelAdmin) :
    list_display = ['initiated_by', 'sent_to', 'created_at', 'status']
    list_filter = ['initiated_by', 'sent_to', 'created_at', 'status']

admin.site.register(FriendshipRequest, FriendshipRequestAdmin)

class FriendsListAdmin(admin.ModelAdmin) :
    fields = ['belongs_to', 'friends']
    list_display = ['belongs_to', 'get_number_of_friends']
    list_filter = ['belongs_to']

admin.site.register(FriendsList, FriendsListAdmin)



