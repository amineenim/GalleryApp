from django.urls import path 
from . import views
app_name = 'likes'

urlpatterns = [
    path('<int:photo_id>/likes/', views.likes_per_photo, name="likes_per_photo"),
    path('<int:photo_id>/add_like/', views.add_like, name='add_like'),
]
