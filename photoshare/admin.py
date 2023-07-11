from django.contrib import admin
from .models import Category, Photo, PasswordResetToken, EmailVerificationToken
# Register your models here.
admin.site.register(Category)


class PhotoAdmin(admin.ModelAdmin):
    fields=['category', 'description', 'image']
    list_display = ['category','number_of_likes', 'description', 'created_by', 'created_at']
    list_filter = ['category', 'created_by', 'created_at']
admin.site.register(Photo, PhotoAdmin)

class PasswordResetTokenAdmin(admin.ModelAdmin) :
    fields = ['user', 'token', 'created_at', 'expires_at']
    list_display = ['user', 'token', 'created_at', 'expires_at']
    list_filter = ['user', 'created_at', 'expires_at']

admin.site.register(PasswordResetToken, PasswordResetTokenAdmin)

class EmailVerificationTokenAdmin(admin.ModelAdmin) :
    fields = ['user', 'token', 'created_at', 'expires_at']
    list_display = ['user', 'token', 'created_at', 'expires_at']
    list_filter = ['user', 'created_at', 'expires_at']
    
admin.site.register(EmailVerificationToken, EmailVerificationTokenAdmin)