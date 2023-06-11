from django.contrib import admin
from .models import Like
# Register your models here.

class LikeAdmin(admin.ModelAdmin):
    list_display = ['photo', 'created_by', 'added_at']
    list_filter = ['photo', 'created_by', 'added_at']

admin.site.register(Like, LikeAdmin)
