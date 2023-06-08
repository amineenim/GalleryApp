from django.urls import path
from . import views 



urlpatterns = [
    path('',views.gellery, name='gallery'),
    path('new/', views.addNew, name='new'),
    path('<str:pk>/', views.viewPhoto, name='detail_photo'),
    path('<str:pk>/edit/', views.editPhoto, name="edit"),
    
]


