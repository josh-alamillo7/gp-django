from django import forms

class UserForm(forms.Form):
  title = forms.CharField(label='Song Title', max_length=200)
  artist = forms.CharField(label='Artist', max_length=100)
  play_count = forms.IntegerField(label='Play Count', max_value=2000, min_value=1)

class LoginForm(forms.Form):
  username = forms.CharField(label='Username', max_length=30)
  password = forms.CharField(label='Password', max_length=15, widget=forms.PasswordInput())