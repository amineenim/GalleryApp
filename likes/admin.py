from django.contrib import admin
from .models import Like, Comment
# Register your models here.

class LikeAdmin(admin.ModelAdmin):
    list_display = ['photo', 'created_by', 'added_at']
    list_filter = ['photo', 'created_by', 'added_at']

admin.site.register(Like, LikeAdmin)

class CommentAdmin(admin.ModelAdmin) :
    list_display = ['comment_text','photo', 'created_by', 'created_at', 'get_when_created']
    list_filter = ['created_by', 'created_at', 'photo']

admin.site.register(Comment, CommentAdmin)
