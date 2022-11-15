from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group

from .forms import LoginForm, BetreiberForm
from .helpers import is_systemadmin, not_logged_in

from betreiber.models import User


# Create your views here.
@user_passes_test(not_logged_in, login_url='administrator:betreiberliste')
def view_login(request):
    '''
    /PF0010/ Ein nicht eingeloggter Administrator kann sich unter Angabe des 
    Benutzernamens und Passworts am System anmelden.
    '''

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and is_systemadmin(user):
                login(request, user)
                return redirect(reverse('administrator:betreiberliste'))
            else:
                print('unable to login')
                return render(request, 'administrator/login.html', {
                    'error': 'Fehler beim Einloggen',
                    'form': LoginForm(),
                })

    return render(request, 'administrator/login.html', {
        'form': LoginForm(),
    })


@login_required(login_url='administrator:login')
def view_logout(request):
    '''
    /PF0020/ Ein eingeloggter Administrator kann sich vom System abmelden.
    '''
    if request.user.is_authenticated:
        logout(request)
    return redirect(reverse('administrator:login'))

@login_required(login_url='administrator:login')
@user_passes_test(is_systemadmin, login_url='administrator:logout')
def view_display_betreiberliste(request):
    '''
    /PF0040/ Ein eingeloggter Administrator kann eine Liste der bestehenden 
    Betreiberkonten einsehen.
    '''
    users = User.objects.filter(groups__name='betreiber')
    return render(request, 'administrator/index.html', {
        'users': users,
    })

@login_required(login_url='administrator:login')
@user_passes_test(is_systemadmin)
def view_create_betreiber(request):
    '''
    /PF0030/ Ein eingeloggter Administrator kann neue Betreiberkonten für 
    Verlagsmitarbeiter einrichten
    '''
    if request.method == 'POST':
        # validate form, retreive data, create new user and assign the betreiber group to it
        # then, if all that went successful, return to the betreiberliste with success message
        form = BetreiberForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            # TODO Random Passwort generieren 
            password = 'Hello123'
            new_user = User.objects.create_user(username, email, password)
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.is_staff = True
            new_user.save()
            print(f'user created: {new_user}')
            # TODO Add user to betreiber group
            betreiber_group = Group.objects.get(name='betreiber')
            new_user.groups.add(betreiber_group)
            return redirect(reverse('administrator:betreiberliste'))
        else:
            return render(request, 'administrator/newbetreiber.html', {
                'error': 'Ein Fehler ist aufgetreten: ',
                'form': form,
            })
    
    return render(request, 'administrator/newbetreiber.html', {
        'form': BetreiberForm(),
    })

@login_required(login_url='administrator:login')
@user_passes_test(is_systemadmin)
def view_edit_betreiber(request, edit_user_id):
    '''
    /PF0050/ Ein eingeloggter Administrator kann die Daten von Betreiberkonten editieren.
    '''
    if request.method == 'POST':
        try:
            edit_user = User.objects.get(pk=edit_user_id)
            form = BetreiberForm(request.POST, instance = edit_user)
            if form.is_valid():
                form.save()
                return redirect(reverse('administrator:betreiberliste'))
            else:
                raise ValueError
        except:
            # TODO pass over the error message
            print('[EDIT-Post]: Ein Fehler ist aufgetreten')
            return redirect(reverse('administrator:betreiberliste'))
    
    try:
        edit_user = User.objects.get(pk=edit_user_id)
        form = BetreiberForm(instance=edit_user)
        return render(request, 'administrator/editbetreiber.html', {
            'betreiber': edit_user,
            'form': form,
        })
    except:
        # TODO pass over the error message
        print('[EDIT-Get]: Ein Fehler ist aufgetreten')
        return redirect(reverse('administrator:betreiberliste'))



@login_required(login_url='administrator:login')
@user_passes_test(is_systemadmin)
def view_delete_betreiber(request, delete_user_id):
    '''
    /PF0060/ Ein eingeloggter Administrator kann bestehende Betreiberkonten löschen.
    '''
    if request.method == 'POST':
        try:
            delete_user = User.objects.get(pk=delete_user_id)
            delete_user.delete()
        except:
            # TODO add error message to indicate we were unable to delete the requested user
            pass
    return redirect(reverse('administrator:betreiberliste'))

def view_access_forbidden(request):
    logout(request)
    return render(request, 'administrator/noaccess.html')