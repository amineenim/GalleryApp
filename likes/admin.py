from django.contrib import admin
from .models import Like, Comment, Notification
# Register your models here.

class LikeAdmin(admin.ModelAdmin):
    list_display = ['photo', 'created_by', 'added_at']
    list_filter = ['photo', 'created_by', 'added_at']

admin.site.register(Like, LikeAdmin)

class CommentAdmin(admin.ModelAdmin) :
    list_display = ['comment_text','photo', 'created_by', 'created_at', 'get_when_created']
    list_filter = ['created_by', 'created_at', 'photo']

admin.site.register(Comment, CommentAdmin)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['notification', 'created_by', 'photo', 'is_like', 'is_comment', 'is_seen']
    list_filter = ['created_by', 'is_like', 'is_comment', 'is_seen', 'photo']

admin.site.register(Notification, NotificationAdmin)

