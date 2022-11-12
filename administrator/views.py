from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import LoginForm

def is_sysadmin(user):
    return user.groups.filter(name='systemadmin').exists()

# Create your views here.
def view_login(request):
    '''
    /PF0010/ Ein nicht eingeloggter Administrator kann sich unter Angabe des 
    Benutzernamens und Passworts am System anmelden.
    '''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('administrator:betreiberliste'))
            else:
                print('unable to login')
                return render(request, 'endnutzer/login.html', {
                    'error': 'Fehler beim Einloggen',
                })

    return render(request, 'administrator/login.html', {
        'form': LoginForm(),
    })


@login_required
def view_logout(request):
    '''
    /PF0020/ Ein eingeloggter Administrator kann sich vom System abmelden.
    '''

@login_required
@user_passes_test(is_sysadmin)
def view_display_betreiberliste(request):
    '''
    /PF0040/ Ein eingeloggter Administrator kann eine Liste der bestehenden 
    Betreiberkonten einsehen.
    '''
    render(request, 'administrator/index.html')

@login_required
@user_passes_test(is_sysadmin)
def view_create_betreiber(request):
    '''
    /PF0030/ Ein eingeloggter Administrator kann neue Betreiberkonten für 
    Verlagsmitarbeiter einrichten
    '''

@login_required
@user_passes_test(is_sysadmin)
def view_edit_betreiber(request):
    '''
    /PF0050/ Ein eingeloggter Administrator kann die Daten von Betreiberkonten editieren.
    '''

@login_required
@user_passes_test(is_sysadmin)
def view_delete_betreiber(request):
    '''
    /PF0060/ Ein eingeloggter Administrator kann bestehende Betreiberkonten löschen.
    '''