from django.db import models

# Create your models here.
class User(models.Model):
  name = models.CharField(max_length=30, unique=True)

  def __str__(self):
    return self.name

class Artist(models.Model):
  name = models.CharField(max_length=100, unique=True)

  def __str__(self):
    return self.name

class Genre(models.Model):
  name = models.CharField(max_length=30, unique=True, null=True)

  def __str__(self):
    return self.name

class Song(models.Model):
  title = models.CharField(max_length=200)
  genre = models.ForeignKey(Genre, on_delete=models.CASCADE, default=None, null=True)
  artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
  plays = models.PositiveIntegerField(default=0)

  def __str__(self):
    return self.title

class PlayCount(models.Model):
  song = models.ForeignKey(Song, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  plays = models.PositiveIntegerField(default=0)