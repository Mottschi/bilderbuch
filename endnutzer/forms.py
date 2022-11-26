from django import forms
from betreiber.models import User, Buch, Seite, Sprachaufnahme, Mandant


class LoginForm(forms.Form):
	username = forms.CharField(max_length=150, label='Benutzername')
	password = forms.CharField(widget=forms.PasswordInput, label='Passwort')
	
class PasswordResetForm(forms.Form):
    username = forms.CharField(max_length=150, label='Benutzername')

class MandantenForm(forms.ModelForm):
    class Meta:
        model = Mandant
        fields = ['name', 'phone', 'street', 'house_nr', 'postal_code', 'city', 'country']
        labels = {
            'name': 'Name', 
            'phone': 'Telefonnummer', 
            'street': 'Straße', 
            'house_nr': 'Hausnummer', 
            'postal_code': 'Postleitzahl', 
            'country': 'Land',
            'city': 'Stadt',
        }