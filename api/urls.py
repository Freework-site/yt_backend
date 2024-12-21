from django.urls import path
from . import views

urlpatterns = [
    path('video-info/', views.get_video_info, name='video-info'),
]
