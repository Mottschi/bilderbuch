from django import forms
from betreiber.models import User, Buch, Seite, Sprachaufnahme, Mandant, Aktivierungscode


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

class EinladungsForm(forms.Form):
     email = forms.EmailField(label = 'E-Mail', required=True)

class EndnutzerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email']
        help_texts = {
            'username': None,
        }
        widgets = {
             'password': forms.PasswordInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
             field.required = True
    

class AktivierungsForm(forms.ModelForm):
     class Meta:
          model = Aktivierungscode
          fields = ['code']
          labels = {
               'code': 'Aktivierungscode'
          }

class LoeschForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label='Passwort')