from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.core.mail import send_mail
from django.db import IntegrityError
from django.utils.timezone import now


from .forms import LoginForm, PasswordResetForm, PasswordChangeForm, MandantenForm, EinladungsForm
from .forms import EndnutzerForm, EndnutzerEditForm, AktivierungsForm, LoeschForm
from .helpers import is_endnutzer, not_logged_in, handle_uploaded_file, is_mandantenadmin

from betreiber.models import User, Autor, Mandant, Buch, Seite, Aktivierungscode, Einladung, Sprache
from django.conf import settings as conf_settings

import random, os, uuid
from datetime import datetime, date, timedelta

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
def view_registration(request):
    '''
    /PF0410/ Ein Benutzer, der einen Einladungslink erhalten hat, kann sich 
    über diesen ein Benutzerkonto erstellen, unter Angabe des Realnamens, der 
    Emailadresse, eines Benutzernamens und des gewünschten Passworts. Optional 
    können gesprochene Sprachen mit angegeben werden. 
    '''
    try:
        einladung = Einladung.objects.get(code=request.GET['invite'])
    except:
        messages.error(request, "Einladung konnte nicht gefunden werden. Bitte beachten Sie, dass Einladungen nur zur Erstellung eines Kontos benutzt werden können, nicht für mehrere Konten.")
        return redirect(reverse('endnutzer:login'))
        
    mandant = einladung.mandant
    
    if request.method == 'POST':
        form = EndnutzerForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            password_comparison = form.cleaned_data['password_comparison']

            if password != password_comparison:
                messages.error(request, 'Die beiden Angaben zum Passwort stimmen nicht überein')
                return render(request, 'endnutzer/user/registration.html',{
                    'mandant': mandant,
                    'form': form,
                })

            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.mandant = mandant
            endnutzer_group = Group.objects.get(name='endnutzer')
            user.groups.add(endnutzer_group)
            user.save()
            
            for name in form.cleaned_data['sprachen']:
                sprache = Sprache.objects.get(name=name)
                user.sprachen.add(sprache)
            messages.success(request, f'Ihr Benutzerkonto wurde erfolgreich erstellt.')
            einladung.delete()
            return redirect(reverse('endnutzer:login'))
        else:
            messages.error(request, 'Bitte korrigieren Sie Ihre Angaben und senden Sie das Formular erneut ab.')        
    else:
        form = EndnutzerForm()

    return render(request, 'endnutzer/user/registration.html',{
        'mandant': mandant,
        'form': form,
    })


@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def view_library(request):
    '''
    /PF0510/ Ein eingeloggter Benutzer kann die Bibliothek des Mandanten einsehen.
    '''
    return render(request, 'endnutzer/bibliothek/index.html', {})


@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def api_library(request):
    '''
    /PF0510/ Ein eingeloggter Benutzer kann die Bibliothek des Mandanten einsehen.
    '''
    mandant = request.user.mandant
    activated_codes = mandant.activated_codes.all()
    library = [code.book.serialize() for code in activated_codes]
    return JsonResponse(status=200, data = {'library':library})


@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def view_play_book(request, buch_id):
    '''
    /PF0530/ Bücher sollen sich nach Auswahl einer der verfügbaren Sprachen abspielen 
    lassen.
    '''
    raise NotImplementedError


@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def view_play_page(request, buch_id, seite_id):
    '''
    /PF0610/ Zur nächsten Seite blättern.
    /PF0620/ Zur vorherigen Seite blättern.
    '''
    raise NotImplementedError

@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def view_record_book(request):
    '''
    /PF0540/ Es soll sich eine neue Sprachaufzeichnung für ein Buch aufnehmen lassen, 
    unter Auswahl der benutzten Sprache.
    '''
    raise NotImplementedError

@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def view_record_page(request):
    '''
    In Verbindung mit /PF0540/
    /PF0660/ Zur nächsten Seite blättern. Zeigt die nächste Seite an.
    /PF0670/ Zur vorherigen Seite blättern. Zeigt die vorherige Seite an.
    /PF0680/ Aufnehmen. Erlaubt dem Benutzer eine Audioaufzeichnung für die aktuelle Seite aufzunehmen.

    '''
    raise NotImplementedError

@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def view_profile(request):
    '''
    /PF0710// Einsehen der persönlichen Daten, die mit dem Konto verbunden sind 
    (Realname, Emailadresse, Benutzername, gesprochene Sprachen).
    /PF0720/ Modifizieren der persönlichen Daten.
    '''
    form = EndnutzerEditForm(instance=request.user)
    if request.method == 'POST':
        form = EndnutzerEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Die Daten für dieses Profil wurden aktualisiert.')
            return redirect(reverse('endnutzer:index'))
        messages.error(request, 'Bitte die Felder korrekt ausfüllen.')
    return render(request, 'endnutzer/user/profile.html', {
        'form': form,
    })

@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def view_change_password(request):
    '''
    /PF0721/ Modifizieren des Passworts
    '''
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            fail = False
            password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']
            new_password_comparison = form.cleaned_data['new_password_comparison']
            if not check_password(password, request.user.password):
                fail = True
                messages.error(request, 'Das alte Passwort ist nicht korrekt.')
            if new_password != new_password_comparison:
                fail = True
                messages.error(request, 'Das neue Passwort stimmt nicht mit dem Vergleichspasswort überein.')
            if fail:
                return render(request, 'endnutzer/user/password.html', {'form': PasswordChangeForm()})
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Das Passwort wurde erfolgreich geändert.')
            return redirect(reverse('endnutzer:userprofil'))
        messages.error('Bitte das Formular korrekt ausfüllen.')
    return render(request, 'endnutzer/user/password.html', {'form': PasswordChangeForm()})

@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def view_my_recordings(request):
    '''
    /PF0730/ Einsehen der eigenen Sprachaufzeichnungen.
    '''
    raise NotImplementedError

@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def view_delete_recording(request):
    '''
    Teil von /PF0730/ - Löschen eigener Sprachaufzeichnungen
    '''
    raise NotImplementedError

@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def api_modify_recording_visibility(request):
    '''
    /PF0740/ Modifizieren der Sichtbarkeit von Sprachaufzeichnungen. 
    '''
    raise NotImplementedError

@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def view_account_deletion(request):
    '''
    /PF0750/ Einleiten der Löschung des eigenen Benutzerkontos. 
    '''
    user = request.user
    if user.is_mandantenadmin:
        messages.error(request, 'Es ist nicht möglich dieses Benutzerkonto zu löschen, solange es die Rolle des Mandantenadmin trägt. Bitte geben Sie die Leitung über den Mandanten zuerst an einen anderen Benutzer weiter oder löschen Sie den gesamten Mandanten.')
        return redirect(reverse('endnutzer:userprofil'))
    
    deletion_date = None if user.deletion is None else user.deletion + timedelta(days=7)
    ready_for_deletion = deletion_date is not None and deletion_date < now()

    if request.method== 'POST':
        form = LoeschForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Es wurde kein Passwort angegeben.")
            return render(request, 'endnutzer/user/deletion.html', {
                'form': LoeschForm(),
                'deletion_date': deletion_date,
                'show_password_field': True if deletion_date is None or ready_for_deletion else False,
            })
        password = form.cleaned_data['password']
        if not check_password(password, user.password):
            messages.error(request, 'Das angegebene Passwort ist falsch.')
            return render(request, 'endnutzer/user/deletion.html', {
                'form': LoeschForm(),
                'deletion_date': deletion_date,
                'show_password_field': True if deletion_date is None or ready_for_deletion else False,
            })
        
        if ready_for_deletion:
            user.delete()
            messages.success(request, f'Das Benutzerkonto "{user}" wurde erfolgreich gelöscht.')
            return redirect(reverse('endnutzer:logout'))
        elif deletion_date:
            messages.error(request, 'Das Einleiten der Löschung ist noch keine 7 Tage her, daher kann die Löschung noch nicht durchgeführt werden.')
            return redirect(reverse('endnutzer:userprofil'))
        else:
            user.deletion = now()
            user.save()
            messages.success(request, 'Der Löschvorgang wurde erfolgreich eingeleitet. Um die Löschung abzuschließen, warten Sie bitte 7 Tage ab und bestätigen Sie die Löschung anschließend erneut über diese Seite.')
            return redirect(reverse('endnutzer:userprofil'))
        
    return render(request, 'endnutzer/user/deletion.html', {
        'form': LoeschForm(),
        'deletion_date': deletion_date,
        'show_password_field': True if deletion_date is None or ready_for_deletion else False,
    })


@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def view_cancel_deletion(request):
    '''
    /PF0751/ Abbrechen der Löschung des Benutzerkontos
    '''
    request.user.deletion = None
    request.user.save()
    messages.success(request, "Die Löschung wurde abgebrochen.")
    return redirect(reverse('endnutzer:userprofil'))


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
    
    return render(request, 'endnutzer/admin/mandant_profile.html', {
        'form': form,
        })


@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')
def view_mandant_deletion(request):
    '''
    /PF0830/ Löschen des Mandanten und aller damit verbundenen Benutzerkonten.
    (Benutzerkonten werden durch Cascade geloescht, kein manuelles Loeschen notwendig)
    '''
    mandant = request.user.mandant
    deletion_date = None if mandant.deletion is None else mandant.deletion + timedelta(days=30)
    ready_for_deletion = deletion_date is not None and deletion_date < now()
    if request.method == 'POST':
        form = LoeschForm(request.POST)
        if not form.is_valid():
            return render(request, 'endnutzer/admin/deletion.html', {
                'form': LoeschForm(),
                'deletion_date': deletion_date,
                'show_password_field': True if deletion_date is None or ready_for_deletion else False,
            })
        password = form.cleaned_data['password']
        if not check_password(password, request.user.password):
            messages.error(request, 'Das angegebene Passwort ist falsch.')
            return render(request, 'endnutzer/admin/deletion.html', {
                'form': LoeschForm(),
                'deletion_date': deletion_date,
                'show_password_field': True if deletion_date is None or ready_for_deletion else False,
            })
                
        if deletion_date:
            if ready_for_deletion:
                mandant.delete()
                messages.success(request, f'Der Mandant "{mandant.name} wurde erfolgreich gelöscht.')
                return redirect(reverse('endnutzer:logout'))
            else:
                messages.error(request, 'Das Einleiten der Löschung ist noch keine 30 Tage her, daher kann die Löschung noch nicht durchgeführt werden.')
                return redirect(reverse('endnutzer:mandantenprofil'))
        else:
            mandant.deletion = now()
            mandant.save()
            messages.success(request, "Der Löschvorgang wurde erfolgreich eingeleitet. Um die Löschung abzuschließen, warten Sie bitte 30 Tage ab und bestätigen Sie die Löschung anschließend erneut über diese Seite.")
            return redirect(reverse('endnutzer:mandantenprofil'))
    

    return render(request, 'endnutzer/admin/deletion.html', {
        'form': LoeschForm(),
        'deletion_date': deletion_date,
        'show_password_field': True if deletion_date is None or ready_for_deletion else False,
    })


@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')
def view_cancel_mandant_deletion(request):
    '''
    /PF0831/ Löschen des Mandanten abbrechen.
    '''
    mandant = request.user.mandant
    mandant.deletion = None
    mandant.save()
    messages.success(request, 'Der Löschvorgang für diesen Mandanten wurde abgebrochen.')
    return redirect(reverse("endnutzer:mandantenprofil"))

@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')
def view_user_accounts(request):
    '''
    /PF0910/ Einsehen einer Liste aller mit dem Mandanten verbundenen Benutzerkonten.
    '''
    mandant = request.user.mandant
    users = mandant.member.all()
    return render(request, 'endnutzer/admin/users.html', {
        'users': users,
    })

@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')
def view_kick_user(request, user_id):
    '''
    /PF0920/ Entfernen von mit dem Mandanten verbundenen Benutzerkonten.
    '''
    try:
        target = User.objects.get(pk=user_id)
    except:
        messages.error(request, 'Der angegebene Benutzer konnte nicht gefunden werden.')
        return redirect(reverse('endnutzer:benutzerliste'))
    if target == target.mandant.manager:
        messages.error(request, 'Der Mandantenadmin kann sich nicht selbst aus dem Mandanten entfernen.')
        return redirect(reverse('endnutzer:benutzerliste'))
    if request.method == 'POST':
        target.delete()
        messages.success(request, f'Der Benutzer {target.username} ({target.get_full_name()}) wurde erfolgreich entfernt.')
        return redirect(reverse('endnutzer:benutzerliste'))
    return render(request, 'endnutzer/admin/kick_user.html', {
        'target': target,
    })
    

@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')
def view_invite_user(request):
    '''
    /PF0930/ Versenden von Einladungslinks zur Erstellung von Benutzerkonten,
    die mit dem Mandanten verbunden sind.
    '''
    form = EinladungsForm()
    if request.method == 'POST':
        form = EinladungsForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            mandant = request.user.mandant
            invite_code = None
            while not invite_code:
                invite_code = uuid.uuid4()
                if Einladung.objects.filter(code=invite_code).exists():
                    invite_code = None
            einladung = Einladung.objects.create(code=invite_code, is_used=False, mandant=mandant)
            if conf_settings.DEBUG:
                invite_link = f'http://127.0.0.1:8000/registration?invite={invite_code}'
            else:
                # TODO Generate invite link to render platform
                # can only be done once we know the host url
                raise NotImplementedError
            send_mail(
                    'Einladung zu Projekt Bilderuch',
                    f'Hallo,\n\nSie wurden eingeladen, dem Mandanten {mandant.name} im Projekt Bilderbuch beizutreten. Benutzen Sie dafür folgenden Link:\n\n{invite_link}\n\nMit freundlichen Grüßen,\nProjekt Bilderbuch',
                    'projekt.bilderbuch@gmail.com',
                    [email],
                    fail_silently=True,
                )
            messages.success(request, "Einladung verschickt.")
            return render(request, 'endnutzer/admin/einladung.html', {
                'form': EinladungsForm(),
            })
        else:
            messages.error(request, 'Die Einladung konnte nicht verschickt werden.')
    return render(request, 'endnutzer/admin/einladung.html', {
        'form': form,
    })

@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')    
def view_activate_book(request):
    '''
    /PF1010/ Aktivieren von Büchercodes, um Bücher der Bibliothek des Mandanten
    hinzuzufügen.
    '''
    form = AktivierungsForm()
    if request.method == 'POST':
        # get the code from the form
        try:
            code = Aktivierungscode.objects.filter(code=request.POST['code'])[0]
        except Exception as e:
            print(e)
            messages.error(request, 'Der angegebene Code existiert nicht. Bitte überprüfen Sie die Schreibweise und versuchen Sie es erneut.')
            return render(request, 'endnutzer/admin/activate_book.html', {
                'form': form,
            })
        
        if code.mandant is not None:
            if code.mandant == request.user.mandant:
                messages.error(request, 'Sie haben diesen Code bereits in Ihrem Mandant registriert.')
                return render(request, 'endnutzer/admin/activate_book.html', {
                    'form': form,
                })

            messages.error(request, 'Dieser Code ist aktuell bereits in einem Mandanten registriert und kann daher im Moment nicht erneut verwendet werden.')
            return render(request, 'endnutzer/admin/activate_book.html', {
                'form': form,
            })
    
        try:
            code.mandant = request.user.mandant
            code.save()
        except IntegrityError:
            messages.error(request, f'Das Buch "{code.book}" zu dem dieser Code gehört wurde für diesen Mandanten bereits freigeschaltet.')
            return render(request, 'endnutzer/admin/activate_book.html', {
                'form': form,
            })
        except Exception as e:
            messages.error(request, 'Der Code konnte nicht aktiviert werden.')
            return render(request, 'endnutzer/admin/activate_book.html', {
                'form': form,
            })
        messages.success(request, f'Das Buch "{code.book} wurde erfolgreich Ihrer Bibliothek hinzugefügt.')
        return redirect(reverse('endnutzer:library'))
    return render(request, 'endnutzer/admin/activate_book.html', {
        'form': form,
    })

# TODO
@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')
def view_all_recordings(request):
    '''
    /PF1020/ Einsehen einer Liste aller öffentlichen Sprachaufzeichnungen, 
    die von mit dem Mandanten verbundenen Benutzerkonten getätigt wurden.
    '''
    raise NotImplementedError
    members = request.user.mandant.member.all()
    recordings = [member.recordings.filter(is_public = True) for member in members]
    

# TODO
@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')
def view_delete_recording(request):
    '''
    /PF1030/ Löschen von Sprachaufzeichnungen.
    '''
    raise NotImplementedError
