from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.
class User(AbstractUser):
    '''
    Datenmodell fuer alle drei Anwendergruppen
    '''
    mandant = models.ForeignKey('Mandant', on_delete=models.CASCADE, blank=True, null=True, default=None, related_name='member')
    deletion = models.DateTimeField(null=True, blank=True, default = None)

    class Meta:
        ordering = ['username']

    @property
    def is_mandantenadmin(self):
        return self.mandant.manager == self

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
    city = models.CharField(max_length=30, default='')
    deletion = models.DateTimeField(null=True, blank=True, default=None)
    country = models.CharField(max_length = 2, choices=Country.choices, default=Country.GERMANY)
    manager = models.OneToOneField('User', on_delete=models.RESTRICT, related_name='verwaltet')

    @property
    def user_count(self):
        return User.objects.filter(mandant=self).count()

    @property
    def book_count(self):
        return Aktivierungscode.objects.filter(mandant=self).count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Mandanten'


class Aktivierungscode(models.Model):
    code = models.CharField(max_length=16, unique=True)
    mandant = models.ForeignKey('Mandant', on_delete=models.SET_NULL, blank=True, null=True, default=None, related_name='activated_codes')
    was_exported = models.BooleanField(default=False)
    book = models.ForeignKey('Buch', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.code} ({self.book})'

class Buch(models.Model):
    thumbnail = models.CharField(max_length=150)
    title = models.CharField(max_length=40)
    author = models.ManyToManyField('Autor')
    age = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name_plural = 'Bücher'

    def __str__(self):
        return self.title

class Autor(models.Model):
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30)

    class Meta:
        ordering = ['last_name', 'first_name', 'middle_name']
        verbose_name_plural = 'Autoren'

    def __str__(self):
        return f'{self.first_name}{" " + self.middle_name if self.middle_name else ""} {self.last_name}'

class Seite(models.Model):
    seitenzahl = models.PositiveSmallIntegerField()
    text = models.CharField(max_length=255)
    picture = models.CharField(max_length=150)
    book = models.ForeignKey('Buch', on_delete=models.CASCADE, related_name='seiten')

    class Meta:
        verbose_name_plural = 'Seiten'
        constraints = [
            models.UniqueConstraint(fields=['seitenzahl', 'book'], name='SpezifischeSeite')
        ]
        ordering = ['seitenzahl']

    def serialize(self):
        return {
            'seitenzahl': self.seitenzahl,
            'text': self.text,
            'picture': self.picture,
            'id': self.id}

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
        verbose_name_plural = 'Seiten'

class Sprache(models.Model):
    name = models.CharField(max_length=25)
    code = models.CharField(max_length=2)
    flag = models.CharField(max_length=150)
    users = models.ManyToManyField('User')

    class Meta:
        verbose_name_plural = 'Sprachen'

    def __str__(self):
        return self.name

class Einladung(models.Model):
    code = models.UUIDField()
    is_used = models.BooleanField(default=False)
    mandant = models.ForeignKey('Mandant', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Einladungen'

    def __repr__(self):
        return f'{"Unb" if not self.is_used else "B"}enutzte Einladung zu {self.mandant.name} - Code: {self.code}'
