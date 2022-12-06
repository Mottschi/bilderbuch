from django import forms
from betreiber.models import User, Autor, Buch, Seite, Mandant
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
	username = forms.CharField(max_length=150, label='Benutzername')
	password = forms.CharField(widget=forms.PasswordInput, label='Passwort')

	username.widget.attrs.update({'class': 'form-control'})
	password.widget.attrs.update({'class': 'form-control'})


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
    def __init__(self, *args, **kwargs):
        # From Django Documentation: https://docs.djangoproject.com/en/4.1/ref/forms/widgets/#customizing-widget-instances
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        


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
    def __init__(self, *args, **kwargs):
        # From Django Documentation: https://docs.djangoproject.com/en/4.1/ref/forms/widgets/#customizing-widget-instances
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['id'] = visible.id_for_label
            visible.field.widget.attrs['placeholder'] = ''
        self.fields['author'].widget.attrs['class'] = 'form-select'
        self.fields['author'].widget.attrs['size'] = '5'
        self.fields['age'].widget.attrs.pop('placeholder', None) 

class EditBuchForm(BuchForm):
    file = forms.FileField(label='Titelseite', required=False)


class SeitenForm(forms.ModelForm):
    file = forms.FileField(label='Bild')

    field_order = ['file', 'text']
    class Meta:
        model = Seite
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'cols': 40})
        }
    def __init__(self, *args, **kwargs):
        # From Django Documentation: https://docs.djangoproject.com/en/4.1/ref/forms/widgets/#customizing-widget-instances
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['id'] = visible.id_for_label
            visible.field.widget.attrs['placeholder'] = ''

class SeitenEditForm(forms.ModelForm):
    file = forms.FileField(label='Bild', required=False)

    field_order = ['file', 'text']
    class Meta:
        model = Seite
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'cols': 40})
        }
    def __init__(self, *args, **kwargs):
        # From Django Documentation: https://docs.djangoproject.com/en/4.1/ref/forms/widgets/#customizing-widget-instances
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['id'] = visible.id_for_label
            visible.field.widget.attrs['placeholder'] = ''


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
    def __init__(self, *args, **kwargs):    
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['id'] = visible.id_for_label
            visible.field.widget.attrs['placeholder'] = ''
        self.fields['country'].widget.attrs['class'] = 'form-select'

class EndnutzerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        help_texts = {
            'username': None,
        }
    def __init__(self, *args, **kwargs):    
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['id'] = visible.id_for_label
            visible.field.widget.attrs['placeholder'] = ''



class PasswordResetForm(forms.Form):
    username = forms.CharField(max_length=150, label='Benutzername')


class GenerateBuchcodesForm(forms.Form):
    amount = forms.IntegerField(max_value=1000, label='Anzahl' )
    amount.widget.attrs['class'] = 'form-control'
    amount.widget.attrs['type'] = 'range'