from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models.signals import post_save
from django.contrib.auth import authenticate
from django.contrib.auth.models import User as AuthUser

from .models import User, Artist, Genre, Song, PlayCount
from .forms import UserForm, LoginForm
from .config import config

# Create your views here.

def login(request):
  
  if request.method == 'POST':
    form = LoginForm(request.POST)
    if form.is_valid():
      submitted_username = form.cleaned_data['username']
      submitted_password = form.cleaned_data['password']
      

      #password validation
      '''
      different_chars = 0
      if len(config['APP_PW']) != len(submitted_password):
        return render(request, 'login/index.html', {'form': form})
      for index in range(0, len(config['APP_PW'])):
        if submitted_password[index] != config['APP_PW'][index]:
          different_chars = different_chars + 1
      if different_chars > 0:
        return render(request, 'login/index.html', {'form': form})
      '''

      #from here, it means the password was correct
      if User.objects.filter(name = submitted_username).exists():
        print('user exists')
      else:
        #if the user that logged in doesn't exist yet, add them to our database and create a (Django) user object for them.
        new_user = User(name = submitted_username)
        new_user.save()
        new_auth_user = AuthUser.objects.create_user(submitted_username, config['APP_EMAIL'], config['APP_PW'])
        authenticated_user = authenticate(username=submitted_username, password=submitted_password)

        if authenticated_user is not None:
          print('success')
          return render(request, 'music/index.html')
        else:
          print('failure')
          return render(request, 'login/index.html', {'form': form})





    #some authentication logic and processes
    
  else:
    form = LoginForm()
    return render(request, 'login/index.html', {'form': form})

def index(request):

  return render(request, 'music/index.html')
  #Submit a song, browse songs by genre, browse songs by artist, get a music taste breakdown report.

def songinfo(request, song_id):

  top_listeners = []
  song = get_object_or_404(Song, pk=song_id)
  song_title = song.title
  song_artist = Artist.objects.filter(id=song.artist_id)[0].name
  matching_playcounts = PlayCount.objects.order_by('-plays').filter(song_id=song_id)[:20]

  for count in matching_playcounts:
    matching_user = User.objects.filter(id=count.user_id)[0]
    top_listeners.append({'user': matching_user.name, 'play_count': count.plays})

  return render(request, 'songs/detail.html', {'top_listeners': top_listeners, 
    'song_title': song_title, 'song_artist': song_artist})

def userform(request):

  title = None
  current_user = None
  play_count = None
  song_exists = False

  def save_play_count(instance, **kwargs):
    if song_exists == False:
      new_play_count = PlayCount(song=instance, user=current_user, plays=play_count)
      new_play_count.save()

  def save_song_after_artist(instance, **kwargs):
    new_song = Song(title=title, artist=instance, plays=play_count)
    new_song.save()

  post_save.connect(save_play_count, sender=Song)
  post_save.connect(save_song_after_artist, sender=Artist)

  if request.method == 'POST':
    form = UserForm(request.POST)
    if form.is_valid():
      #later, get the current user info somehow
      current_user = User.objects.filter(name='Claudia54')[0]
      artist = form.cleaned_data['artist']
      title = form.cleaned_data['title']
      play_count = form.cleaned_data['play_count']

      if Artist.objects.filter(name=artist).exists():
        matching_artist = Artist.objects.filter(name=artist)[0]
        artist_id = matching_artist.id
        if Song.objects.filter(title=title, artist_id=artist_id).exists():
          song_exists = True
          #check if there is a matching user
          matching_song = Song.objects.filter(title=title, artist_id=artist_id)[0]
          if PlayCount.objects.filter(user_id=current_user.id, song_id=matching_song.id).exists():
            matching_play_count = PlayCount.objects.filter(user_id=current_user.id, song_id=matching_song.id)[0]
            play_count_difference = play_count - matching_play_count.plays
            matching_play_count.plays = play_count
            matching_song.plays = matching_song.plays + play_count_difference
            matching_play_count.save()
            matching_song.save()
          else:
            new_play_count = PlayCount(song=matching_song, user=current_user, plays=play_count)
            matching_song.plays = matching_song.plays + play_count
            new_play_count.save()
            matching_song.save()
        else:
          new_song = Song(title=title, artist=matching_artist, plays=play_count)
          new_song.save()

      else:
        new_artist = Artist(name=artist)
        new_artist.save()
  else:
    form = UserForm()
  return render(request, 'music/userform.html', {'form': form})

def artist_list(request):
  artist_list = Artist.objects.order_by('name')
  return render(request, 'artists/index.html', {'artist_list': artist_list})

def most_played_list(request):
  most_played_list = Song.objects.order_by('-plays')[:20]
  return render(request, 'songs/index.html', {'most_played_list': most_played_list})

def artist(request, artist_id):
  artist = get_object_or_404(Artist, pk=artist_id)
  artist_name = artist.name
  song_list = Song.objects.filter(artist_id=artist_id).order_by('-plays')[:15]

  return render(request, 'artists/detail.html', {'artist_name': artist_name, 'song_list': song_list})