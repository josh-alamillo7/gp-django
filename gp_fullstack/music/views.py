from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
  return HttpResponse('Some placeholder index.. welcome page and buttons or something')
  #Submit a song, browse songs by genre, browse songs by artist, get a music taste breakdown report.

def userform(request):
  return HttpResponse('User form will go here')