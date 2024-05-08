from django.urls import path
from .views import TrackAPIView, PlayListAPIView, PlayListInfoAPIView, TrackLikeAPIView, AlbumAPIView

urlpatterns = [
    path('tracks/', TrackAPIView.as_view()),
    path('playlists/', PlayListAPIView.as_view()),
    path('playlists_info/', PlayListInfoAPIView.as_view()),
    path('like_tracks/', TrackLikeAPIView.as_view()),
    path('album/', AlbumAPIView.as_view()),
    path('album/<str:album>', AlbumAPIView.as_view())
]

