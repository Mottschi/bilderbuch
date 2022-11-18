from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.contrib import messages
from django.core.mail import send_mail

from .forms import LoginForm, BetreiberForm, EndnutzerMandantenadminForm, PasswordResetForm
from .helpers import is_betreiber, not_logged_in

from betreiber.models import User

# Create your views here.
@user_passes_test(not_logged_in, login_url='betreiber:index')
def view_login(request):
    '''
    /PF0110/ Ein nicht eingeloggter Mitarbeiter kann sich unter Angabe des 
    Benutzernamens und Passworts am System anmelden.
    '''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and is_betreiber(user):
                login(request, user)
                return redirect(reverse('betreiber:index'))
            else:
                print('unable to login')
                # TODO Fehlermeldung soll den Grund beinhalten
                messages.error(request, 'Fehler beim Einloggen')
                return render(request, 'betreiber/login.html', {
                    'form': LoginForm(),
                })
    return render(request, 'betreiber/login.html', {
        'form': LoginForm(),
    })


@login_required(login_url='betreiber:login')
def view_logout(request):
    '''
    /PF0120/ Ein eingeloggter Mitarbeiter kann sich vom System abmelden.
    '''
    if request.user.is_authenticated:
        logout(request)
    return redirect(reverse('betreiber:login'))

@login_required(login_url='betreiber:login')
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def view_index(request):
    '''
    Einstiegsseite Funktion beschreibung
    '''
    return render(request, 'betreiber/index.html')

@user_passes_test(not_logged_in, login_url='betreiber:index')
def view_reset_password(request):
    '''
    /PF0130/ Ein nicht eingeloggter Mitarbeiter kann sein Passwort zurücksetzen, 
    dafür erhält er eine E-Mail mit Link zum Festlegen eines neuen Passworts.
    '''
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username)
                assert is_betreiber(user)
                
                # TODO Password Reset Funktionalität
                # aktuell wird eMail mit neuem Passwort verschickt, statt pw reset token zu generieren und den per email zu versenden
                # fuers erste reicht das, eventuell gar fuer den Prototyp, kann aber auch am Ende wenn wir ansonsten alle Funktionalitaet
                # haben noch angepasst werden

                password = User.objects.make_random_password()
                user.set_password(password)
                user.save()
                
                send_mail(
                    'Passwortänderung',
                    f'Hallo {user.first_name} {user.last_name},\n\nDas Passwort für Ihr Betreiberkonto für Projekt Bilderbuch wurde zurückgesetzt.\n\nBenutzername: {username}\nNeues Passwort: {password}\n\nMit freundlichen Grüßen,\nProjekt Bilderbuch Systemadmin',
                    'projekt.bilderbuch@gmail.com',
                    [user.email],
                    fail_silently=False,
                )

                messages.success(request, f'Das Passwort für das Betreiberkonto {username} wurde zurückgesetzt. Sie werden eine E-Mail mit weiteren Informationen erhalten.')
                return redirect(reverse('betreiber:login'))
            except:
                # TODO Fehlermeldung soll den Grund beinhalten - aktuell gehen wir von einer einzigen möglichen Ursache zum Scheitern aus, realistisch?
                messages.error(request, f'Es wurde kein Betreiberkonto mit dem Benutzernamen {username} gefunden.')
        else:
            print('not valid')
    return render(request, 'betreiber/reset_password.html', {
        'form': PasswordResetForm(),
    })


def view_buchliste(request):
    '''
    /PF0201/ Der Mitarbeiter kann eine Liste aller Bücher einsehen.
    '''

def view_create_buch(request):
    '''
    /PF0210/ Der Mitarbeiter kann neue Bücher der Anwendung hinzufügen.
    '''

def view_edit_buch_metadaten(request, buch_id):
    '''
    /PF0220/ Der Mitarbeiter kann die Daten bestehender Bücher editieren.
    Teil 1 - Metadaten
    '''

def view_edit_buch_seitendaten(request, buch_id):
    '''
    /PF0220/ Der Mitarbeiter kann die Daten bestehender Bücher editieren.
    Teil 2 - Seitendaten
    '''

def view_delete_buch(request, buch_id):
    '''
    /PF0230/ Der Mitarbeiter kann Bücher aus der Anwendung löschen.
    '''

def view_generate_buchcodes(request, buch_id):
    '''
    /PF0240/ Der Mitarbeiter kann neue Aktivierungscodes für Bücher generieren und exportieren.
    '''

def view_autorenliste(request):
    '''
    /PF0260/ Autorenliste
    '''

def view_create_autor(request):
    '''
    /PF0270/ Neuer Autor
    '''

def view_edit_autor(request, autor_id):
    '''
    /PF0280/ Autor editieren
    '''

def view_create_mandant(request):
    '''
    /PF0310/ Der Mitarbeiter kann neue Mandanten erstellen, dabei wird gleichzeitig 
    ein Benutzerkonto mit Adminrechten für den Mandanten erstellt.
    '''

def view_mandantenliste(request):
    '''
    /PF0320/ Der Mitarbeiter kann eine Liste aller Mandanten einsehen.
    '''

def view_edit_mandant(request, mandant_id):
    '''
    /PF0330/ Der Mitarbeiter kann Mandanten editieren.
    '''

def view_delete_mandant(request, mandant_id):
    '''
    /PF0340/ Der Mitarbeiter kann Mandanten löschen.
    '''