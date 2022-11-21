from django import forms
from betreiber.models import User, Autor, Buch, Seite, Mandant
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
	username = forms.CharField(max_length=150, label='Benutzername')
	password = forms.CharField(widget=forms.PasswordInput, label='Passwort')


class BetreiberForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email']
		labels = {
            'username': 'Benutzername', 
            'first_name': 'Vorname', 
            'last_name': 'Nachname', 
            'email': 'E-Mail',
        }


class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        exclude = []
        labels = {
            'first_name': 'Vorname',
            'middle_name': 'Mittelname',
            'last_name': 'Nachname',
        }


class BuchForm(forms.ModelForm):
    file = forms.FileField(label='Titelseite', required=True)

    class Meta:
        model = Buch
        fields = ['title', 'author', 'age']
        labels = {
            'title': 'Titel',
            'author': 'Autoren',
            'age': 'Altersfreigabe',
        }

class EditBuchForm(BuchForm):
    file = forms.FileField(label='Titelseite', required=False)


class SeitenForm(forms.ModelForm):
    class Meta:
        model = Seite
        exclude = []


class MandantenForm(forms.ModelForm):
    class Meta:
        model = Mandant
        fields = ['name', 'phone', 'street', 'house_nr', 'postal_code', 'country']
        labels = {
            'name': 'Name', 
            'phone': 'Telefonnummer', 
            'street': 'Straße', 
            'house_nr': 'Hausnummer', 
            'postal_code': 'Postleitzahl', 
            'country': 'Land',
        }

class EndnutzerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class PasswordResetForm(forms.Form):
    username = forms.CharField(max_length=150, label='Benutzername')


class GenerateBuchcodesForm(forms.Form):
    amount = forms.IntegerField(max_value=1000, label='Anzahl')