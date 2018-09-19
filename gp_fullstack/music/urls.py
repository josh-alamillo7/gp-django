from django.urls import path

from . import views

urlpatterns = [
  path('', views.index),
  path('userform', views.userform),
  path('songs/<int:song_id>', views.songinfo),
  path('artists/<int:artist_id>', views.artist),
  path('genres/<int:genre_id>', views.genre),
]