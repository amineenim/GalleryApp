from django.urls import path
from . import views
app_name = 'friends'

urlpatterns = [
    path('send_request/<str:username>', views.send_friendship_request, name='send_request'),
    path('notifications/', views.get_notifications, name='notifications'),
    path('accept/<str:username>', views.accept_friendship_request, name='accept_request'),
    path('decline/<str:username>', views.decline_friendship_request, name='decline_request'),
]
