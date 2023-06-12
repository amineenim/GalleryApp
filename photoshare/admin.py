from django.contrib import admin
from .models import Category, Photo
# Register your models here.
admin.site.register(Category)


class PhotoAdmin(admin.ModelAdmin):
    fields=['category', 'description', 'image']
    list_display = ['category','number_of_likes', 'description', 'created_by', 'created_at']
    list_filter = ['category', 'created_by', 'created_at']
admin.site.register(Photo, PhotoAdmin)