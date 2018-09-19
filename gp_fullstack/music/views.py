from django.shortcuts import render
from django.http import HttpResponse
from django.db.models.signals import post_save

from .models import User, Artist, Genre, Song, PlayCount
from .forms import UserForm

# Create your views here.

def index(request):
  return HttpResponse('Some placeholder index.. welcome page and buttons or something')
  #Submit a song, browse songs by genre, browse songs by artist, get a music taste breakdown report.

def songinfo(request, song_id):
  return HttpResponse('This is the song info page for %s.' % song_id)

def userform(request):

  def save_play_count(instance, **kwargs):
    new_play_count = PlayCount(song=new_song, user=current_user, plays=play_count)
    new_play_count.save()

  post_save.connect(save_play_count, sender=Song)

  if request.method == 'POST':
    form = UserForm(request.POST)
    if form.is_valid():
      #later, get the current user info somehow
      current_user = User.objects.filter(name='Josh737')[0]
      artist = form.cleaned_data['artist']
      title = form.cleaned_data['title']
      play_count = form.cleaned_data['play_count']

      if Artist.objects.filter(name=artist).exists():
        matching_artist = Artist.objects.filter(name=artist)[0]
        artist_id = matching_artist.id
        if Song.objects.filter(title=title, artist_id=artist_id).exists():
          print('it exists')
        else:
          new_song = Song(title=title, artist=matching_artist, plays=play_count)
          new_song.save()
          #new_song.save()
          #new_play_count.save()


      else:
        new_artist = Artist(name=artist)
        new_artist.save()
      #Add to database logic
      #if Artist.objects.filter(Name=)
  else:
    form = UserForm()
  return render(request, 'music/userform.html', {'form': form})

def artist(request, artist_id):
  return HttpResponse('This will list all the songs for artist %s.' % artist_id)

def genre(request, genre_id):
  return HttpResponse('This will list all the songs for genre %s.' % genre_id)