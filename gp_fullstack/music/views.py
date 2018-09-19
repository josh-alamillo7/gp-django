from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
  return HttpResponse('Some placeholder index.. welcome page and buttons or something')
  #Submit a song, browse songs by genre, browse songs by artist, get a music taste breakdown report.

def songinfo(request, song_id):
  return HttpResponse('This is the song info page for %s.' % song_id)

def userform(request):
  return HttpResponse('User form will go here')

def artist(request, artist_id):
  return HttpResponse('This will list all the songs for artist %s.' % artist_id)

def genre(request, genre_id):
  return HttpResponse('This will list all the songs for genre %s.' % genre_id)