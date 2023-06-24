from django.urls import path
from . import views
app_name = 'profile'

urlpatterns = [
    path('', views.get_my_profile, name='my_profile'),
    path('<str:username>/', views.get_profile, name='view_profile'),
]
