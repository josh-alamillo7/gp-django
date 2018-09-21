from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models.signals import post_save
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

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

      #from here, it means the password was correct
      if AuthUser.objects.filter(username=submitted_username).exists() != True:
        new_auth_user = AuthUser.objects.create_user(submitted_username, config['APP_EMAIL'], config['APP_PW'])

      authenticated_user = authenticate(request, username=submitted_username, password=submitted_password)
      if authenticated_user is not None:
        auth_login(request, authenticated_user)
        if User.objects.filter(name = submitted_username).exists() != True:
          new_user = User(name = submitted_username)
          new_user.save()   
        return render(request, 'music/index.html')
      else:
        return render(request, 'login/index.html', {'form': form})

           
        #if the user that logged in doesn't exist yet, add them to our database and create a (Django) user object for them.

    #some authentication logic and processes
    
  else:
    form = LoginForm()
    return render(request, 'login/index.html', {'form': form})

@login_required(login_url='./login')
def index(request):

  return render(request, 'music/index.html')
  #Submit a song, browse songs by genre, browse songs by artist, get a music taste breakdown report.

@login_required(login_url='./login')
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

@login_required(login_url='./login')
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
      current_user = User.objects.filter(name=request.user.username)[0]
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
      return render(request, 'music/success.html')
  else:
    form = UserForm()
  return render(request, 'music/userform.html', {'form': form})

@login_required(login_url='./login')
def artist_list(request):
  artist_list = Artist.objects.order_by('name')
  return render(request, 'artists/index.html', {'artist_list': artist_list})

@login_required(login_url='./login')
def most_played_list(request):
  most_played_list = Song.objects.order_by('-plays')[:20]
  return render(request, 'songs/index.html', {'most_played_list': most_played_list})

@login_required(login_url='./login')
def artist(request, artist_id):
  artist = get_object_or_404(Artist, pk=artist_id)
  artist_name = artist.name
  song_list = Song.objects.filter(artist_id=artist_id).order_by('-plays')[:15]

  return render(request, 'artists/detail.html', {'artist_name': artist_name, 'song_list': song_list})

@login_required(login_url='./login')
def logout(request):
  auth_logout(request)
  form = LoginForm()
  return render(request, 'login/index.html', {'form': form})

@login_required(login_url='./login')
def mailrequest(request):
  return render(request, 'request/index.html')

@login_required(login_url='./login')
def mail(request):

  #mail functionality
  username = request.user.username
  useremail = request.user.email

  user_id = User.objects.filter(name=username)[0].id
  user_play_counts = PlayCount.objects.filter(user_id=user_id)

  genre_counts = {}
  artist_counts = {}
  max_genre_count = 0
  max_artist_count = 0
  max_genre = None
  max_artist = None

  for count in user_play_counts:
    current_song = Song.objects.filter(id=count.song_id)[0]
    current_artist = str(Artist.objects.filter(id=current_song.artist_id)[0])
    if Genre.objects.filter(id=current_song.genre_id).exists():
      current_genre = str(Genre.objects.filter(id=current_song.genre_id)[0])
    if current_artist in artist_counts.keys():
      artist_counts[current_artist] = artist_counts[current_artist] + count.plays
    else:
      artist_counts[current_artist] = count.plays
    if current_genre in genre_counts.keys():
      genre_counts[current_genre] = genre_counts[current_genre] + count.plays
    else:
      genre_counts[current_genre] = count.plays

  for artist in artist_counts:
    if artist_counts[artist] > max_artist_count:
      max_artist = artist
      max_artist_count = artist_counts[artist]
  for genre in genre_counts:
    if genre_counts[genre] > max_genre_count:
      max_genre = genre
      max_genre_count = genre_counts[genre]

  mailtext = 'Hi ' + username + ', \n \n Thank you for your interest in receiving a listener report! Our current service informs a user of their most-played artist and genre. In the future as our app grows, you will receive some nice graphs representing more detailed information! Currently, your most-played artist is ' + max_artist + ' and your most-played genre is ' + max_genre + '. Thanks again for using the app! \n Best, \n Josh'

  print(mailtext)
  #sending mail doesn't work yet, but let's try and deploy this first.
  #send_mail('Your personalized music report', mailtext, useremail, [useremail], fail_silently=False,)

  return render(request, 'request/confirm.html')