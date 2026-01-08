from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('videos/', views.gallery, name='gallery'),
    path('videos/upload/', views.upload_video, name='upload_videos'),
    path('videos/delete/<int:pk>/', views.delete_video, name='delete_video'),
    path('videos/edit/<int:pk>/', views.edit_video, name='edit_video'),
    path('videos/thumbnail/<int:pk>/', views.generate_thumbnail, name='generate_thumbnail'),
    path('videos/conclusion/', views.conclusion, name='conclusion'),
    path('videos/<int:pk>/', views.video_detail, name='video_detail'),
    
    # Авторизация
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]