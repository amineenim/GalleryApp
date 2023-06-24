from django.urls import path
from . import views
app_name = 'friends'

urlpatterns = [
    path('send_request/<str:username>', views.send_friendship_request, name='send_request')
]
