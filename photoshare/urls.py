from django.urls import path
from . import views 


urlpatterns = [
    path('',views.gellery, name='gallery'),
    path('new/', views.addNew, name='new'),
    path('mine/', views.myGallery, name='mygallery'),
    path('permissions/', views.get_perms, name='perms'),
    path('<str:pk>/', views.viewPhoto, name='detail_photo'),
    path('<str:pk>/edit/', views.editPhoto, name="edit"),
    path('<str:pk>/remove/', views.deletePhoto, name="delete"),
    path('accounts/login', views.loginUser, name='login'),
    path('accounts/logout', views.logoutUser, name='logout'),
    path('accounts/register', views.registerUser, name='register'),
    path('accounts/resetpassword/', views.reset_password, name='reset_password'),
    path('accounts/verify_email/', views.verify_email, name='verify_email')
]


