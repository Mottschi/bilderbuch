from django.urls import path
from . import views

app_name = 'endnutzer'
urlpatterns = [
    path("login", views.view_login, name="login"),
    path("logout", views.view_logout, name="logout"),
    path("", views.view_index, name="index"),
    path("login/forgot_password", views.view_reset_password, name="reset_password"),
    path("registration", views.view_registration, name='registration'),
    path("bibliothek", views.view_library, name='library'),
    path("mandant/profile", views.view_mandant_profile, name='mandantenprofil'),
    path("mandant/benutzerliste", views.view_user_accounts, name='benutzerliste'),
    path("mandant/benutzer/entfernen/<int:user_id>", views.view_kick_user, name='kick_user'),
    path("mandant/buch/aktivieren", views.view_activate_book, name='buch_aktivieren'),
    path("mandant/sprachaufzeichnungen", views.view_all_recordings, name='alle_aufzeichnungen'),
    path("mandant/einladung", views.view_invite_user, name='einladung'),
    path("mandant/loeschung/einleiten", views.view_mandant_deletion, name='mandant_loeschen'),
    path("mandant/loeschung/abbrechen", views.view_cancel_mandant_deletion, name='mandant_loeschung_abbrechen'),
    path("", views.view_registration, name=''),
]