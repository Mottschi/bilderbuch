from django import forms
from betreiber.models import User, Buch, Seite, Sprachaufnahme


class LoginForm(forms.Form):
	username = forms.CharField(max_length=150, label='Benutzername')
	password = forms.CharField(widget=forms.PasswordInput, label='Passwort')
	
class PasswordResetForm(forms.Form):
    username = forms.CharField(max_length=150, label='Benutzername')