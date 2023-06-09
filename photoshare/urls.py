from django.urls import path
from . import views 


urlpatterns = [
    path('',views.gellery, name='gallery'),
    path('new/', views.addNew, name='new'),
    path('<str:pk>/', views.viewPhoto, name='detail_photo'),
    path('<str:pk>/edit/', views.editPhoto, name="edit"),
    path('<str:pk>/remove/', views.deletePhoto, name="delete"),
    path('accounts/login', views.loginUser, name='login'),
    path('accounts/logout', views.logoutUser, name='logout'),
    path('accounts/register', views.registerUser, name='register'),
]


