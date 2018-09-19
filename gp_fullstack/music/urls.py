from django.urls import path

from . import views

urlpatterns = [
  path('', views.index),
  path('userform', views.userform),
  path('songs/<int:song_id>', views.songinfo),
  path('artists/<int:artist_id>', views.artist),
  path('artists', views.artist_list),
  path('songs', views.most_played_list),
]