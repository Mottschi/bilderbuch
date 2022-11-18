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
    class Meta:
        model = Buch
        exclude = []

class SeitenForm(forms.ModelForm):
    class Meta:
        model = Seite
        exclude = []


class MandantenForm(forms.ModelForm):
    class Meta:
        model = Mandant
        exclude = []

class EndnutzerMandantenadminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class PasswordResetForm(forms.Form):
    username = forms.CharField(max_length=150)