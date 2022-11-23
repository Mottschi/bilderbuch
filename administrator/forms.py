from django import forms
from betreiber.models import User

class LoginForm(forms.Form):
	username = forms.CharField(max_length=150)
	password = forms.CharField(widget=forms.PasswordInput)
	
	username.widget.attrs.update({'class': 'form-control'})
	password.widget.attrs.update({'class': 'form-control'})


class BetreiberForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email']
