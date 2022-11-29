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
    path("bibliothek/api", views.api_library, name='api_library'),
    path("buch/<int:buch_id>/abspielen", views.view_play_book, name='buch_abspielen'),
    path("buch/<int:buch_id>/aufnehmen", views.view_record_book, name='buch_aufnehmen'),
    path("bibliothek", views.view_library, name='library'),
    path("mandant/profil", views.view_mandant_profile, name='mandantenprofil'),
    path("mandant/benutzerliste", views.view_user_accounts, name='benutzerliste'),
    path("mandant/benutzer/entfernen/<int:user_id>", views.view_kick_user, name='kick_user'),
    path("mandant/buch/aktivieren", views.view_activate_book, name='buch_aktivieren'),
    path("mandant/sprachaufzeichnungen", views.view_all_recordings, name='alle_aufzeichnungen'),
    path("mandant/einladung", views.view_invite_user, name='einladung'),
    path("mandant/loeschung/einleiten", views.view_mandant_deletion, name='mandant_loeschen'),
    path("mandant/loeschung/abbrechen", views.view_cancel_mandant_deletion, name='mandant_loeschung_abbrechen'),
    path("user/profil/passwort", views.view_change_password, name='passwort_aendern'),
    path("user/aufnahmen/sichtbarkeit/<int:buch_id>", views.api_modify_recording_visibility, name='sichtbarkeit_toggle'),
    path("user/aufnahmen", views.view_my_recordings, name='eigene_aufnahmen'),
    path("user/aufnahmen/delete", views.view_delete_recording, name='eigene_aufnahme_loeschen'),
    path("user/loeschung/einleiten", views.view_account_deletion, name='account_loeschen'),
    path("user/loeschung/abbrechen", views.view_cancel_deletion, name='account_loeschung_abbrechen'),
]