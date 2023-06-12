from django.urls import path 
from . import views
app_name = 'likes'

urlpatterns = [
    path('<int:photo_id>/likes/', views.likes_per_photo, name="likes_per_photo"),
    path('<int:photo_id>/add_like/', views.add_like, name='add_like'),
    # this route is for clearing messages if there are any 
    path('messages/clear/', views.clear_messages, name='clear_messages'),
]
