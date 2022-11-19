from django import forms
from betreiber.models import User, Autor, Buch, Seite, Mandant

class LoginForm(forms.Form):
	username = forms.CharField(max_length=150)
	password = forms.CharField(widget=forms.PasswordInput)


class BetreiberForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email']

class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        exclude = []

class BuchForm(forms.ModelForm):
    file = forms.FileField(label='Thumbnail')

    class Meta:
        model = Buch
        fields = ['title', 'author', 'age']
        labels = {
            'title': 'Titel',
            'author': 'Autoren',
            'age': 'Altersfreigabe',
        }
        

class SeitenForm(forms.ModelForm):
    class Meta:
        model = Seite
        exclude = []

class MandantenForm(forms.ModelForm):
    class Meta:
        model = Mandant
        fields = ['name', 'phone', 'street', 'house_nr', 'postal_code', 'country']
        

class EndnutzerMandantenadminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class PasswordResetForm(forms.Form):
    username = forms.CharField(max_length=150)

class GenerateBuchcodesForm(forms.Form):
    amount = forms.IntegerField(max_value=1000, step_size=100)