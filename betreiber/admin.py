from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Mandant)
admin.site.register(Aktivierungscode)
admin.site.register(Buch)
admin.site.register(Autor)
admin.site.register(Seite)
admin.site.register(Sprachaufnahme)
admin.site.register(Sprache)
admin.site.register(Einladung)