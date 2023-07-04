from django.contrib import admin
from .models import FriendshipRequest, FriendsList, FriendshipNotification, Conversation, ConversationMessage
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


class FriendshipNotificationAdmin(admin.ModelAdmin) :
    fields = ['intended_to', 'content', 'created_at']
    list_display = ['intended_to', 'content', 'created_at']
    list_filter = ['intended_to', 'created_at']

admin.site.register(FriendshipNotification, FriendshipNotificationAdmin)

class ConversationAdmin(admin.ModelAdmin) :
    fields = ['member_one', 'member_two']
    list_display = ['member_one', 'member_two']

admin.site.register(Conversation, ConversationAdmin)

class ConversationMessageAdmin(admin.ModelAdmin) :
    fields = ['conversation', 'sent_by', 'created_at']
    list_display = ['conversation', 'sent_by', 'created_at', 'is_seen']
    list_filter = ['conversation', 'sent_by', 'created_at', 'is_seen']

admin.site.register(ConversationMessage, ConversationMessageAdmin)