from django.urls import path
from . import views
app_name = 'friends'

urlpatterns = [
    path('send_request/<str:username>', views.send_friendship_request, name='send_request'),
    path('notifications/', views.get_notifications, name='notifications'),
    path('accept/<str:username>', views.accept_friendship_request, name='accept_request'),
    path('decline/<str:username>', views.decline_friendship_request, name='decline_request'),
    path('all/', views.get_list_of_my_friends, name='my_friends'),
    path('close_conversation/', views.close_conversation, name='close_conversation'),
    path('send/<str:username>', views.send_message, name='send_message'),
    path('messages/', views.get_messages_notifications, name='messages'),
]
