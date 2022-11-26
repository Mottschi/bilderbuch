from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import Group
from django.contrib import messages
from django.core.mail import send_mail

from .forms import LoginForm, PasswordResetForm, MandantenForm
from .helpers import is_endnutzer, not_logged_in, handle_uploaded_file, is_mandantenadmin

from betreiber.models import User, Autor, Mandant, Buch, Seite, Aktivierungscode, Einladung
from django.conf import settings as conf_settings

import random, os

# Create your views here.
@user_passes_test(not_logged_in, login_url='endnutzer:index')
def view_login(request):
    '''
    /PF0420/ Ein Benutzer mit bestehendem Konto, der nicht eingeloggt ist, 
    kann sich auf der Hauptseite der Anwendung unter Angabe von Benutzername 
    und Passwort einloggen.
    '''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and is_endnutzer(user):
                login(request, user)
                return redirect(reverse('endnutzer:index'))
            else:
                # TODO Fehlermeldung soll den Grund beinhalten
                messages.error(request, 'Fehler beim Einloggen')
                return render(request, 'endnutzer/login.html', {
                    'form': LoginForm(),
                })
    return render(request, 'endnutzer/login.html', {
        'form': LoginForm(),
    })


@login_required(login_url='endnutzer:login')
def view_logout(request):
    '''
    /PF0430/ Ein eingeloggter Benutzer kann sich ausloggen.
    '''
    logout(request)
    return redirect(reverse('endnutzer:login'))

@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def view_index(request):
    '''
    Nach erfolgreichem Login wird dem Benutzer die Einstiegsseite mit 
    einer Auswahl zwischen dem Zugang zur Bibliothek und Zugang zu den 
    Verwaltungsoptionen angezeigt. (/PB0115/)
    '''
    return render(request, 'endnutzer/index.html')

@user_passes_test(not_logged_in, login_url='endnutzer:index')
def view_reset_password(request):
    '''
    /PF0440/ Ein nicht eingeloggter Benutzer kann sein Passwort zurücksetzen, 
    dafür erhält er eine E-Mail mit Link zum Festlegen eines neuen Passworts.
    '''
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username)
                assert is_endnutzer(user)
            except:
                messages.error(request, f'Es wurde kein Endnutzer mit dem Benutzernamen {username} gefunden.')
                return redirect(reverse('endnutzer:login'))
            # TODO Password Reset Funktionalität
            # aktuell wird eMail mit neuem Passwort verschickt, statt pw reset token zu generieren und den per email zu versenden
            # fuers erste reicht das, eventuell gar fuer den Prototyp, kann aber auch am Ende wenn wir ansonsten alle Funktionalitaet
            # haben noch angepasst werden

            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()
            
            send_mail(
                'Passwortänderung',
                f'Hallo {user.first_name} {user.last_name},\n\nDas Passwort für Ihr Benutzerkonto für Projekt Bilderbuch wurde zurückgesetzt.\n\nBenutzername: {username}\nNeues Passwort: {password}\n\nMit freundlichen Grüßen,\nProjekt Bilderbuch Systemadmin',
                'projekt.bilderbuch@gmail.com',
                [user.email],
                fail_silently=False,
            )

            messages.success(request, f'Das Passwort für das Benutzerkonto {username} wurde zurückgesetzt. Sie werden eine E-Mail mit weiteren Informationen erhalten.')
            return redirect(reverse('endnutzer:login'))
    return render(request, 'endnutzer/reset_password.html', {
        'form': PasswordResetForm(),
    })

@user_passes_test(not_logged_in, login_url='endnutzer:index')
def view_registration(request, einladungscode):
    '''
    /PF0410/ Ein Benutzer, der einen Einladungslink erhalten hat, kann sich 
    über diesen ein Benutzerkonto erstellen, unter Angabe des Realnamens, der 
    Emailadresse, eines Benutzernamens und des gewünschten Passworts. Optional 
    können gesprochene Sprachen mit angegeben werden. 
    '''


@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def view_library(request):
    '''
    /PF0510/ Ein eingeloggter Benutzer kann die Bibliothek des Mandanten einsehen.
    '''
    mandant = request.user.mandant
    activated_codes = mandant.activated_codes.all()
    library = [code.book for code in activated_codes]
    return render(request, 'endnutzer/bibliothek/library.html', {
        'buecher': library,
    })


def view_play_book(request):
    '''
    /PF0530/ Bücher sollen sich nach Auswahl einer der verfügbaren Sprachen abspielen 
    lassen.
    '''

def view_play_page(request):
    '''
    /PF0610/ Zur nächsten Seite blättern.
    /PF0620/ Zur vorherigen Seite blättern.
    '''

def view_record_book(request):
    '''
    /PF0540/ Es soll sich eine neue Sprachaufzeichnung für ein Buch aufnehmen lassen, 
    unter Auswahl der benutzten Sprache.
    '''

def view_record_page(request):
    '''
    In Verbindung mit /PF0540/
    /PF0660/ Zur nächsten Seite blättern. Zeigt die nächste Seite an.
    /PF0670/ Zur vorherigen Seite blättern. Zeigt die vorherige Seite an.
    /PF0680/ Aufnehmen. Erlaubt dem Benutzer eine Audioaufzeichnung für die aktuelle Seite aufzunehmen.

    '''

def view_profile(request):
    '''
    /PF0710// Einsehen der persönlichen Daten, die mit dem Konto verbunden sind 
    (Realname, Emailadresse, Benutzername, gesprochene Sprachen).
    /PF0720/ Modifizieren der persönlichen Daten.
    '''

def view_change_password(request):
    '''
    /PF0721/ Modifizieren des Passworts
    '''

def view_my_recordings(request):
    '''
    /PF0730/ Einsehen der eigenen Sprachaufzeichnungen.
    '''

def view_delete_recording(request):
    '''
    Teil von /PF0730/ - Löschen eigener Sprachaufzeichnungen
    '''

def view_modify_recording_visibility(request):
    '''
    /PF0740/ Modifizieren der Sichtbarkeit von Sprachaufzeichnungen. 
    '''

def view_account_deletion(request):
    '''
    /PF0750/ Einleiten der Löschung des eigenen Benutzerkontos. 
    '''

def view_cancel_deletion(request):
    '''
    /PF0751/ Abbrechen der Löschung des Benutzerkontos
    '''


'''****************************Mandantenadmin****************************************'''

@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')
def view_mandant_profile(request):
    '''
    /PF0810/ Einsehen der zum Mandanten gehörenden Daten.
    '''
    mandant = request.user.mandant
    form = MandantenForm(instance = mandant)
    if request.method == 'POST':
        '''
        /PF0820/ Editieren der zum Mandanten gehörenden Daten.
        '''
        form = MandantenForm(request.POST, instance = mandant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mandantendetails geaendert')
            return redirect(reverse('endnutzer:index'))
    
    return render(request, 'endnutzer/mandant/profile.html', {
        'form': form,
        })


@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')
def view_mandant_deletion(request):
    '''
    /PF0830/ Löschen des Mandanten und aller damit verbundenen Benutzerkonten.
    '''

@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')
def view_cancel_mandant_deletion(request):
    '''
    /PF0831/ Löschen des Mandanten abbrechen.
    '''

@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')
def view_user_accounts(request):
    '''
    /PF0910/ Einsehen einer Liste aller mit dem Mandanten verbundenen Benutzerkonten.
    '''

@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')
def view_kick_user(request):
    '''
    /PF0920/ Entfernen von mit dem Mandanten verbundenen Benutzerkonten.
    '''

@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')
def view_invite_user(request):
    '''
    /PF0930/ Versenden von Einladungslinks zur Erstellung von Benutzerkonten,
    die mit dem Mandanten verbunden sind.
    '''

@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')    
def view_activate_book(request):
    '''
    /PF1010/ Aktivieren von Büchercodes, um Bücher der Bibliothek des Mandanten
    hinzuzufügen.
    '''

@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')
def view_all_recordings(request):
    '''
    /PF1020/ Einsehen einer Liste aller öffentlichen Sprachaufzeichnungen, 
    die von mit dem Mandanten verbundenen Benutzerkonten getätigt wurden.
    '''

@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')
def view_delete_recording(request):
    '''
    /PF1030/ Löschen von Sprachaufzeichnungen.
    '''