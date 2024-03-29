from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.contrib import messages
from django.core.mail import send_mail

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
            if user is None:
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Ungültiges Passwort!')
                else:
                    messages.error(request, 'Ungültiger Benutzername!')
                return render(request, 'administrator/login.html', {
                    'form': LoginForm(),
                })
            if is_systemadmin(user):
                login(request, user)
                if 'next' in request.GET:
                    return redirect(request.GET['next'])
                return redirect(reverse('administrator:betreiberliste'))
            else:
                messages.error(request, 'Der angegebene Benutzername gehört nicht zu einem Systemadministratorkonto!')
                return render(request, 'administrator/login.html', {
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
@user_passes_test(is_systemadmin, login_url='administrator:logout')
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
            if first_name and last_name and email:
                password = User.objects.make_random_password()
                new_user = User.objects.create_user(username, email, password)
                new_user.first_name = first_name
                new_user.last_name = last_name
                new_user.is_staff = True
                new_user.save()
                betreiber_group = Group.objects.get(name='betreiber')
                new_user.groups.add(betreiber_group)
                messages.success(request, f'Betreiberkonto "{username}" für {first_name} {last_name} ({email}) wurde erfolgreich erstellt.')

                send_mail(
                    'Betreiberkonto erstellt',
                    f'Hallo {first_name} {last_name},\n\nIhr Betreiberkonto für Projekt Bilderbuch wurde erstellt.\n\nBenutzername: {username}\nPasswort: {password}\n\nMit freundlichen Grüßen,\nProjekt Bilderbuch Systemadmin {request.user.first_name}',
                    'projekt.bilderbuch@gmail.com',
                    [email],
                    fail_silently=False,
                )

                return redirect(reverse('administrator:betreiberliste'))
            else:
                messages.error(request, "Ein Fehler ist aufgetreten. Bitte stellen Sie sicher, alle Felder auszufuellen.")
                return render(request, 'administrator/newbetreiber.html', {
                    'form': form,
                })

        else:          
            # TODO Grund fuer Fehler anzeigen, evtl. ueber form.errors?
            for value in form.errors:
                print(f'key: "{""}", value: "{value}"')
            messages.error(request, f'Beim Erstellen des Benutzers ist ein Fehler aufgetreten.')
            return render(request, 'administrator/newbetreiber.html', {
                'form': form,
            })
    form =BetreiberForm()
    for key in form.fields:
            form.fields[key].widget.attrs.update({'class': 'form-control'})
    return render(request, 'administrator/newbetreiber.html', {
        'form': form,
    })

@login_required(login_url='administrator:login')
@user_passes_test(is_systemadmin, login_url='administrator:logout')
def view_edit_betreiber(request, edit_user_id):
    '''
    /PF0050/ Ein eingeloggter Administrator kann die Daten von Betreiberkonten editieren.
    '''
    if request.method == 'POST':
        try:
            edit_user = User.objects.get(pk=edit_user_id)
            form = BetreiberForm(request.POST, instance = edit_user)
            if form.is_valid():
                username = form.cleaned_data['username']
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']
                if first_name and last_name and email:
                    form.save()
                    messages.success(request, f'Das Betreiberkonto "{edit_user.username}" ({edit_user.first_name} {edit_user.last_name}) wurde erfolgreich aktualisiert.')
                    return redirect(reverse('administrator:betreiberliste'))
                else:
                    messages.error(request, 'Bitte alle Felder ausfüllen.')
                    return render(request, 'administrator/editbetreiber.html', {
                        'form': form,
                    })

            else:
                raise ValueError
        except:
            messages.error(request, f'Die Änderungen am Betreiberkonto "{edit_user.username}" ({edit_user.first_name} {edit_user.last_name}) konnten nicht gespeichert werden.')
            return render(request, 'administrator/editbetreiber.html', {
                'form': form,
            })
    
    try:
        edit_user = User.objects.get(pk=edit_user_id)
        form = BetreiberForm(instance=edit_user)
        for key in form.fields:
            form.fields[key].widget.attrs.update({'class': 'form-control'})
        return render(request, 'administrator/editbetreiber.html', {
            'form': form,
        })
    except:
        messages.error(request, "Das zu editierende Betreiberkonto konnte nicht gefunden werden.")
        return redirect(reverse('administrator:betreiberliste'))



@login_required(login_url='administrator:login')
@user_passes_test(is_systemadmin, login_url='administrator:logout')
def view_delete_betreiber(request, delete_user_id):
    '''
    /PF0060/ Ein eingeloggter Administrator kann bestehende Betreiberkonten löschen.
    '''
    delete_user = None
    try:
        delete_user = User.objects.get(pk=delete_user_id)
    except:
        messages.error(request, f'Das angegebene Betreiberkonto konnte nicht gefunden werden.')
        return redirect(reverse('administrator:betreiberliste'))
    if request.method == 'POST':
        if delete_user:
            delete_user.delete()
            messages.success(request, f'Das Betreiberkonto "{delete_user.username}" ({delete_user.first_name} {delete_user.last_name}) wurde erfolgreich gelöscht.')
        return redirect(reverse('administrator:betreiberliste'))

    return render(request, 'administrator/betreiber_deletion.html', {
        'target': delete_user,
    })


def view_access_forbidden(request):
    logout(request)
    return render(request, 'administrator/noaccess.html')
