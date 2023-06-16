from django.urls import path 
from . import views
app_name = 'likes'

urlpatterns = [
    path('<int:photo_id>/likes/', views.likes_per_photo, name="likes_per_photo"),
    path('<int:photo_id>/add_like/', views.add_like, name='add_like'),
    # this route is for clearing messages if there are any 
    path('messages/clear/', views.clear_messages, name='clear_messages'),
    # paths for comments 
    path('<int:photo_id>/add_comment/', views.add_comment, name='add_comment'),
    path('<int:photo_id>/comments/', views.comments_per_photo, name="comments_per_photo"),
    path('comments/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comments/<int:comment_id>/remove/', views.delete_comment, name='delete_comment'),
    path('comments/<int:comment_id>/hide/', views.hide_comment, name='hide_comment'),
]
