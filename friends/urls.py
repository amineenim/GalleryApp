from django.urls import path
from . import views
app_name = 'friends'

urlpatterns = [
    path('send_request/<str:username>', views.send_friendship_request, name='send_request'),
    path('notifications/', views.get_notifications, name='notifications'),
    path('accept/<str:username>', views.accept_friendship_request, name='accept_request'),
    path('decline/<str:username>', views.decline_friendship_request, name='decline_request'),
    path('all/', views.get_list_of_my_friends, name='my_friends'),
    path('start_conversation/<str:username>', views.start_conversation, name='new_conversation'),
]
