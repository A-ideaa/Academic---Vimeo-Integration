from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_video, name='upload_video'),
    path('test-credentials/', views.test_credentials, name='test_credentials'),
    path('delete-video/<int:video_id>/', views.delete_video, name='delete_video'),
    path('video/<int:video_id>/', views.video_player, name='video_player'),
    path('check-progress/<str:vimeo_id>/', views.check_progress, name='check_progress'),
    path('check-video-status/<str:vimeo_id>/', views.check_video_status, name='check_video_status'),
] 