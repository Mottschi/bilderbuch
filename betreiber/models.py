from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.
class User(AbstractUser):
    '''
    Datenmodell fuer alle drei Anwendergruppen
    '''
    mandant = models.ForeignKey('Mandant', on_delete=models.CASCADE, blank=True, null=True, default=None)
    deletion = models.DateTimeField(null=True, blank=True, default = None)

class Mandant(models.Model):
    class Country(models.TextChoices):
        GERMANY = 'DE', _('Deutschland')
        AUSTRIA = 'AT', _('Österreich')
        SWITZERLAND = 'CH', _('Schweiz')

    name = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=20)
    street = models.CharField(max_length=50)
    house_nr = models.CharField(max_length=5)
    postal_code = models.CharField(max_length=5)
    deletion = models.DateTimeField(null=True, blank=True, default=None)
    country = models.CharField(max_length = 2, choices=Country.choices, default=Country.GERMANY)
    #NOTE: may need models.RESTRICT instead - something to look into if we run into problems with deletion of mandant
    manager = models.ForeignKey('User', on_delete=models.PROTECT, related_name='verwalter')


class Aktivierungscode(models.Model):
    code = models.CharField(max_length=16, unique=True)
    mandant = models.ForeignKey('Mandant', on_delete=models.SET_NULL, blank=True, null=True, default=None)
    was_exported = models.BooleanField(default=False)
    book = models.ForeignKey('Buch', on_delete=models.CASCADE)

class Buch(models.Model):
    thumbnail = models.CharField(max_length=150)
    title = models.CharField(max_length=40)
    author = models.ManyToManyField('Autor')
    age = models.PositiveSmallIntegerField()

class Autor(models.Model):
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30)

class Seite(models.Model):
    seitenzahl = models.PositiveSmallIntegerField()
    text = models.CharField(max_length=255)
    picture = models.CharField(max_length=150)
    book = models.ForeignKey('Buch', on_delete=models.CASCADE)

class Sprachaufnahme(models.Model):
    seite = models.ForeignKey('Seite', on_delete = models.CASCADE)
    audio = models.CharField(max_length=150)
    is_public = models.BooleanField(default = False)
    language = models.ForeignKey('Sprache', on_delete = models.CASCADE)
    recorded_by = models.ForeignKey('User', on_delete = models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['language', 'recorded_by', 'seite'], name='SpezifischeSprachaufnahme')
        ]

class Sprache(models.Model):
    name = models.CharField(max_length=25)
    code = models.CharField(max_length=2)
    flag = models.CharField(max_length=150)
    users = models.ManyToManyField('User')

class Einladung(models.Model):
    code = models.UUIDField()
    is_used = models.BooleanField(default=False)
    mandant = models.ForeignKey('Mandant', on_delete=models.CASCADE)
