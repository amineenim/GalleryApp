from django.urls import path
from . import views
urlpatterns = [
    path('send_request/', views.send_friendship_request, name='send_request')
]
