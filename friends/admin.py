from django.contrib import admin
from .models import FriendshipRequest
# Register your models here.

class FriendshipRequestAdmin(admin.ModelAdmin) :
    list_display = ['initiated_by', 'sent_to', 'created_at', 'status']
    list_filter = ['initiated_by', 'sent_to', 'created_at', 'status']

admin.site.register(FriendshipRequest, FriendshipRequestAdmin)


