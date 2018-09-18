from django.db import models

# Create your models here.
class User(models.Model):
  name = models.CharField(max_length=30)

class Artist(models.Model):
  name = models.CharField(max_length=100)

class Genre(models.Model):
  name = models.CharField(max_length=30)

class Song(models.Model):
  title = models.CharField(max_length=200)
  genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
  artist = models.Artist(Artist, on_delete=models.CASCADE)
  plays = models.PositiveIntegerField(default=0)

class PlayCount(models.Model):
  song = models.ForeignKey(Song, on_delete=models.CASCADE)
  user = models.User(User, on_delete=models.CASCADE)
  plays = models.PositiveIntegerField(default=0)