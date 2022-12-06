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
from .forms import EndnutzerForm, EndnutzerEditForm, AktivierungsForm, ConfirmForm
from .helpers import is_endnutzer, not_logged_in, handle_uploaded_file, is_mandantenadmin

from betreiber.models import User, Autor, Mandant, Buch, Seite, Aktivierungscode, Einladung, Sprache
from betreiber.models import Sprachaufnahme
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
    sprachen = Sprache.objects.all()
    return render(request, 'endnutzer/bibliothek/index.html', {'sprachen': sprachen})


@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def api_library(request):
    '''
    /PF0510/ Ein eingeloggter Benutzer kann die Bibliothek des Mandanten einsehen.
    '''
    library = request.user.mandant.library
    bibliothek = []
    for buch in library:
        aufnahmen = request.user.mandant.aufnahmen(buch)
        sprachen = set()
        for aufnahme in aufnahmen:
            sprachen.add(aufnahme.language.id)
        book = buch.serialize()
        book['sprachen'] = list(sprachen)
        bibliothek.append(book)
    return JsonResponse(status=200, data = {'library':bibliothek})


@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def view_play_book(request, buch_id):
    '''
    /PF0530/ Bücher sollen sich nach Auswahl einer der verfügbaren Sprachen abspielen 
    lassen.
    '''
    try:
        buch = Buch.objects.get(pk=buch_id)
    except:
        messages.error(request, 'Das angegebene Buch konnte nicht gefunden werden.')
        return redirect(reverse('endnutzer:library'))

    if request.method == 'POST':
        try:
            aufnahme_id = int(request.POST['aufnahme'])
            aufnahme = Sprachaufnahme.objects.get(pk=aufnahme_id)
        except:
            messages.error(request, 'Diese Aufnahme konnte nicht gefunden werden.')
            return redirect(reverse('endnutzer:buch_abspielen', args=[buch_id]))
        if not aufnahme.is_public:
            messages.error(request, 'Diese Aufnahme ist leider nicht öffentlich.')
            return redirect(reverse('endnutzer:buch_abspielen', args=[buch_id]))
        return redirect(reverse('endnutzer:aufnahme_abspielen', args=[buch_id, aufnahme.language.id, aufnahme.recorded_by.id]))

    aufnahmen = request.user.mandant.aufnahmen(buch)
    if len(aufnahmen) == 0:        
        messages.error(request, f'Es wurden für dieses Buch noch keine Aufnahmen von Mitgliedern von "{request.user.mandant}" veröffentlicht.')
        return redirect(reverse('endnutzer:library'))
    
    return render(request, 'endnutzer/bibliothek/buch_abspielen.html', {
        'buch': buch,
        'aufnahmen': aufnahmen,
        })


@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def view_play_recording(request, buch_id, sprache_id, sprecher_id):
    return redirect(reverse('endnutzer:seite_abspielen', args=[buch_id, sprache_id, sprecher_id, 1]))


@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def view_play_page(request, buch_id, sprache_id, sprecher_id, seitenzahl):
    '''
    /PF0610/ Zur nächsten Seite blättern.
    /PF0620/ Zur vorherigen Seite blättern.
    '''
    template = 'endnutzer/bibliothek/seite_abspielen.html'
    try:
        buch = Buch.objects.get(pk=buch_id)
    except:
        messages.error(request, 'Das angegebene Buch wurde nicht gefunden.')

    if buch not in request.user.mandant.library:
            messages.error(request, f'Das gewählte Buch wurde auf Ihrem Mandanten "{request.user.mandant}" bisher noch nicht freigeschaltet.')
            return redirect(reverse('endnutzer:library'))

    try:
        sprache = Sprache.objects.get(pk=sprache_id)
    except:
        messages.error(request, f'Die gewählte Sprache wurde nicht gefunden.')
        return redirect(reverse('endnutzer:library'))

    try:
        sprecher = User.objects.get(pk=sprecher_id)
    except:
        messages.error(request, f'Der gewählte Sprecher wurde nicht gefunden.')
        return redirect(reverse('endnutzer:library'))
    
    try:
        seite = buch.seiten.get(seitenzahl=seitenzahl)
    except:
        messages.error(request, f'Die gewählte Seite wurde nicht gefunden.')
        return redirect(reverse('endnutzer:library'))

    try:
        aufnahme = Sprachaufnahme.objects.get(seite=seite, recorded_by=sprecher, language=sprache, is_public=True)
    except:
        messages.error(request, f'Die gewählte Aufnahme wurde nicht gefunden.')
        return redirect(reverse('endnutzer:library'))

    return render(request, template, {
        'seite': seite,
        'aufnahme': aufnahme,
    })


@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def view_record_book(request, buch_id):
    '''
    /PF0540/ Es soll sich eine neue Sprachaufzeichnung für ein Buch aufnehmen lassen, 
    unter Auswahl der benutzten Sprache.
    '''
    template = 'endnutzer/bibliothek/buch_aufnehmen.html'
    try:
        buch = Buch.objects.get(pk=buch_id)
    except:
        messages.error(request, 'Das gewählte Buch konnte nicht gefunden werden')
        return redirect(reverse('endnutzer:library'))

    if buch not in request.user.mandant.library:
        messages.error(request, f'Das gewählte Buch wurde auf Ihrem Mandanten "{request.user.mandant}" bisher noch nicht freigeschaltet.')
        return redirect(reverse('endnutzer:library'))

    if request.method == 'POST':
        try:
            password = request.POST['password']
        except:
            messages.error(request, 'Es wurde kein Passwort angegeben')
            return render(request, template, {
                'form': ConfirmForm(),
                'sprachen': request.user.sprachen.all(),
                'buch': buch,
            })

        if not check_password(password, request.user.password):
            messages.error(request, 'Das Passwort ist inkorrekt.')
            return render(request, template, {
                'form': ConfirmForm(),
                'sprachen': request.user.sprachen.all(),
                'buch': buch,
            })

        try:
            sprache = request.POST['sprache']
        except:
            messages.error(request, 'Es wurde keine Sprache ausgewählt.')
            return render(request, template, {
                'form': ConfirmForm(),
                'sprachen': request.user.sprachen.all(),
                'buch': buch,
            })
        
        try:
            sprache = Sprache.objects.get(name=sprache)
        except:
            messages.error(request, 'Es wurde keine existierende Sprache ausgewählt.')
            return render(request, template, {
                'form': ConfirmForm(),
                'sprachen': request.user.sprachen.all(),
                'buch': buch,
            })

        return redirect(reverse('endnutzer:seite_aufnehmen', args=(buch.id, 1, sprache.id)))

    return render(request, template, {
        'form': ConfirmForm(),
        'sprachen': request.user.sprachen.all(),
        'buch': buch,
    })


@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def view_record_page(request, buch_id, seitenzahl, sprache_id):
    '''
    In Verbindung mit /PF0540/
    /PF0660/ Zur nächsten Seite blättern. Zeigt die nächste Seite an.
    /PF0670/ Zur vorherigen Seite blättern. Zeigt die vorherige Seite an.
    /PF0680/ Aufnehmen. Erlaubt dem Benutzer eine Audioaufzeichnung für die aktuelle Seite aufzunehmen.

    '''
    # NOTE: currently, the extra password verification is only used when accessing this page
    # through the proper UI path, but not when accessing it directly via bookmark or history
    template = 'endnutzer/bibliothek/seite_aufnehmen.html'
    
    try:
        buch = Buch.objects.get(pk=buch_id)
    except:
        messages.error(request, 'Das angegebene Buch wurde nicht gefunden.')

    if buch not in request.user.mandant.library:
            messages.error(request, f'Das gewählte Buch wurde auf Ihrem Mandanten "{request.user.mandant}" bisher noch nicht freigeschaltet.')
            return redirect(reverse('endnutzer:library'))

    try:
        sprache = Sprache.objects.get(pk=sprache_id)
    except:
        messages.error(request, f'Die gewählte Sprache wurde nicht gefunden.')
        return redirect(reverse('endnutzer:library'))
    
    try:
        seite = buch.seiten.get(seitenzahl=seitenzahl)
    except:
        messages.error(request, f'Die gewählte Seite wurde nicht gefunden.')
        return redirect(reverse('endnutzer:library'))

    aufnahme = Sprachaufnahme.objects.get(language=sprache, seite=seite, recorded_by=request.user) if Sprachaufnahme.objects.filter(language=sprache, seite=seite, recorded_by=request.user).exists() else None
    aufgenommene_seitenzahlen = [seite.seitenzahl for seite in buch.seiten.all() if Sprachaufnahme.objects.filter(language=sprache, seite=seite, recorded_by=request.user).exists() ]
    
    return render(request, template, {
        'buch': buch,
        'sprache': sprache,
        'seite': seite,
        'aufgenommene_seitenzahlen': aufgenommene_seitenzahlen,
        'aufnahme': aufnahme,
    })


@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def api_record_page(request, buch_id, seitenzahl, sprache_id):
    filetypes = {
        "audio/webm": '.webm',
        "audio/mpeg": '.mp3',
        "audio/mp3": '.mp3',
        "audio/mp4": '.m4a',
        "audio/wav": '.wav',
        "audio/ogg": '.ogg',
        "audio/mpeg3": '.mp3',
        "audio/3gpp": '.3gpp',
    }
    try:
        buch = Buch.objects.get(pk=buch_id)
        seite = buch.seiten.get(seitenzahl=seitenzahl)
        sprache = Sprache.objects.get(pk=sprache_id)

        mime_type = request.FILES['file'].content_type
        extension = filetypes[mime_type]
    except:
        return JsonResponse(status=400, data = {})

    # generating new file name every time we replace a recording to avoid caching issues
    filename= f'{str(uuid.uuid4())}{extension}'
    audio_path = os.path.join('endnutzer', 'aufnahmen', str(request.user.mandant.id), filename)
    if conf_settings.RENDER:
        full_filepath = os.path.join(conf_settings.PERSISTENT_STORAGE_ROOT, audio_path)
    else:
        full_filepath = os.path.join('endnutzer', 'static', audio_path)

    if Sprachaufnahme.objects.filter(seite=seite, language=sprache, recorded_by=request.user).exists():
        # Da Aufnahmen unique_together (sprache, sprecher, seite) sind, muessen wir im Fall einer neuen Aufzeichnung
        # die alte loeschen, dabei wird automatisch auch die zugehoerige Datei geloescht
        aufnahme = Sprachaufnahme.objects.get(seite=seite, language=sprache, recorded_by=request.user)
        aufnahme.delete()
    
    # Alle oeffentlichen Aufnahmen des Benutzers fuer diese Buch/Sprach Kombination werden auf nicht oeffentlich gesetzt, da eine neue Aufnahme hinzugefuegt wurde
    for aufnahme in Sprachaufnahme.objects.filter(language=sprache, recorded_by=request.user, is_public=True):
        aufnahme.is_public = False
        aufnahme.save()

    aufnahme = Sprachaufnahme.objects.create(seite=seite, language=sprache, recorded_by=request.user, audio=audio_path, is_public=False)

    handle_uploaded_file(request.FILES['file'], full_filepath)
    return JsonResponse(status=200, data = {})


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
    # Unser Ziel ist es, alle Aufnahmen des Users zu gruppieren und am Ende in einer Liste die
    # nach dem Buch zu dem die Aufnahme gehoert sortiert ist anzuzeigen
    # Da die Buecher zu denen der Benutzer Aufnahmen angefertigt hat eine Teilmenge der Bibliothek des
    # Mandanten sind, moechten wir aber nicht durch alle Buecher oder auch alle Buecher des Mandanten loopen
    return render(request, 'endnutzer/user/aufzeichnungen.html')


@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def api_my_recordings(request):
    '''
    /PF0730/ Einsehen der eigenen Sprachaufzeichnungen.
    '''
    # Unser Ziel ist es, alle Aufnahmen des Users zu gruppieren und am Ende in einer Liste die
    # nach dem Buch zu dem die Aufnahme gehoert sortiert ist anzuzeigen
    # Da die Buecher zu denen der Benutzer Aufnahmen angefertigt hat eine Teilmenge der Bibliothek des
    # Mandanten sind, moechten wir aber nicht durch alle Buecher oder auch alle Buecher des Mandanten loopen
    alle_aufnahmen = Sprachaufnahme.objects.filter(recorded_by=request.user)
    aufzeichnungen = {}
    for aufnahme in alle_aufnahmen:
        if (aufnahme.seite.book, aufnahme.language) not in aufzeichnungen:
            aufzeichnungen[aufnahme.seite.book, aufnahme.language] = {
                'id': aufnahme.id,
                'thumbnail': aufnahme.seite.book.thumbnail,
                'title': aufnahme.seite.book.title,
                'sprache': aufnahme.language.name,
                'is_public': aufnahme.is_public,
                'aufnahmen_count': 1,
                'seiten_count': aufnahme.seite.book.seiten.count(),
                'delete_url': reverse('endnutzer:api_eigene_aufnahme_loeschen', args=[aufnahme.seite.book.id, aufnahme.language.id]),
                'toggle_publicity_url': reverse('endnutzer:api_sichtbarkeit_toggle', args=[aufnahme.seite.book.id, aufnahme.language.id]),
                'edit_url': reverse('endnutzer:seite_aufnehmen', args=[aufnahme.seite.book.id, 1, aufnahme.language.id]),
            }
        else:
            aufzeichnungen[aufnahme.seite.book, aufnahme.language]['aufnahmen_count'] += 1

    return JsonResponse(status=200, data={'aufnahmen': list(aufzeichnungen.values())})


@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def api_delete_recording(request, buch_id, sprache_id):
    '''
    Teil von /PF0730/ - Löschen eigener Sprachaufzeichnungen
    '''
    if request.method != 'POST':
        return JsonResponse(status=400, data={'error': 'Auf diesem Weg können keine Aufzeichnungen gelöscht werden!'})
    try:
        buch = Buch.objects.get(pk=buch_id)
    except:
        return JsonResponse(status=400, data={'error': 'Das angegebene Buch konnte nicht gefunden werden!'})

    try:
        sprache = Sprache.objects.get(pk=sprache_id)
    except:
        return JsonResponse(status=400, data={'error': 'Die angegebene Sprache konnte nicht gefunden werden!'})

    aufnahmen = Sprachaufnahme.objects.filter(recorded_by=request.user, language=sprache, seite__in=buch.seiten.all())

    if len(aufnahmen) == 0:
        return JsonResponse(status=400, data={'error': f'Es wurden keine Aufzeichnungen dieses Benutzers für das Buch "{buch}" auf {sprache} gefunden!'})

    for aufnahme in aufnahmen:
        aufnahme.delete()
    
    return JsonResponse(status=200, data={})


@login_required(login_url='endnutzer:login')
@user_passes_test(is_endnutzer, login_url='endnutzer:logout')
def api_modify_recording_visibility(request, buch_id, sprache_id):
    '''
    /PF0740/ Modifizieren der Sichtbarkeit von Sprachaufzeichnungen. 
    '''
    try:
        buch = Buch.objects.get(pk=buch_id)
    except:
        return JsonResponse(status=400, data={'error': 'Das angegebene Buch konnte nicht gefunden werden!'})

    try:
        sprache = Sprache.objects.get(pk=sprache_id)
    except:
        return JsonResponse(status=400, data={'error': 'Die angegebene Sprache konnte nicht gefunden werden!'})

    aufnahmen = Sprachaufnahme.objects.filter(recorded_by=request.user, language=sprache, seite__in=buch.seiten.all())

    if len(aufnahmen) == 0:
        return JsonResponse(status=400, data={'error': f'Es wurden keine Aufzeichnungen dieses Benutzers für das Buch "{buch}" auf {sprache} gefunden!'})

    if len(aufnahmen) != len(buch.seiten.all()):
        return JsonResponse(status=400, data={'error': f'Sie haben noch nicht alle Seiten dieses Buchs auf {sprache} aufgenommen, daher kann das Buch noch nicht sichtbar geschaltet werden.'})

    aktuelle_sichtbarkeit = aufnahmen[0].is_public
    
    for aufnahme in aufnahmen:
        aufnahme.is_public = not aktuelle_sichtbarkeit
        aufnahme.save()
    
    return JsonResponse(status=200, data={'sichtbarkeit': not aktuelle_sichtbarkeit})


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
        form = ConfirmForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Es wurde kein Passwort angegeben.")
            return render(request, 'endnutzer/user/deletion.html', {
                'form': ConfirmForm(),
                'deletion_date': deletion_date,
                'show_password_field': True if deletion_date is None or ready_for_deletion else False,
            })
        password = form.cleaned_data['password']
        if not check_password(password, user.password):
            messages.error(request, 'Das angegebene Passwort ist falsch.')
            return render(request, 'endnutzer/user/deletion.html', {
                'form': ConfirmForm(),
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
        'form': ConfirmForm(),
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
        form = ConfirmForm(request.POST)
        if not form.is_valid():
            return render(request, 'endnutzer/admin/deletion.html', {
                'form': ConfirmForm(),
                'deletion_date': deletion_date,
                'show_password_field': True if deletion_date is None or ready_for_deletion else False,
            })
        password = form.cleaned_data['password']
        if not check_password(password, request.user.password):
            messages.error(request, 'Das angegebene Passwort ist falsch.')
            return render(request, 'endnutzer/admin/deletion.html', {
                'form': ConfirmForm(),
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
        'form': ConfirmForm(),
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
            
            invite_link = f'http://{request.META["HTTP_HOST"]}/registration?invite={invite_code}'

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


@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')
def view_all_recordings(request):
    '''
    /PF1020/ Einsehen einer Liste aller öffentlichen Sprachaufzeichnungen, 
    die von mit dem Mandanten verbundenen Benutzerkonten getätigt wurden.
    '''
    return render(request, 'endnutzer/admin/aufzeichnungen.html', {})


@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')
def api_all_recordings(request):
    aufnahmen = request.user.mandant.aufnahmen()
    aufzeichnungen = {}
    for aufnahme in aufnahmen:
        if (aufnahme.recorded_by, aufnahme.seite.book, aufnahme.language) not in aufzeichnungen:
            aufzeichnungen[aufnahme.recorded_by, aufnahme.seite.book, aufnahme.language] = {
                'buch_id': aufnahme.seite.book.id,
                'title': aufnahme.seite.book.title,
                'sprache': aufnahme.language.name,
                'sprecher': aufnahme.recorded_by.username,
                'delete_url': reverse('endnutzer:api_user_aufnahme_loeschen', args=[aufnahme.recorded_by.id, aufnahme.seite.book.id, aufnahme.language.id]),
                'play_url': reverse('endnutzer:aufnahme_abspielen', args=[aufnahme.seite.book.id, aufnahme.language.id, aufnahme.recorded_by.id]),
            }
    aufnahmen = list(aufzeichnungen.values())
    aufnahmen = sorted(aufnahmen, key= lambda aufnahme: (aufnahme['title'], aufnahme['sprache'], aufnahme['sprecher']))
    return JsonResponse(status=200, data={'aufnahmen': aufnahmen})
    

@login_required(login_url='endnutzer:login')
@user_passes_test(is_mandantenadmin, login_url='endnutzer:logout')
def api_delete_users_recording(request, user_id, buch_id, sprache_id):
    '''
    /PF1030/ Löschen von Sprachaufzeichnungen.
    '''
    if request.method != 'POST':
        return JsonResponse(status=400, data={'error': 'Auf diesem Weg können keine Aufzeichnungen gelöscht werden!'})
    try:
        buch = Buch.objects.get(pk=buch_id)
    except:
        return JsonResponse(status=400, data={'error': 'Das angegebene Buch konnte nicht gefunden werden!'})

    try:
        user = User.objects.get(pk=user_id)
    except:
        return JsonResponse(status=400, data={'error': 'Das angegebene Buch konnte nicht gefunden werden!'})

    try:
        sprache = Sprache.objects.get(pk=sprache_id)
    except:
        return JsonResponse(status=400, data={'error': 'Die angegebene Sprache konnte nicht gefunden werden!'})

    aufnahmen = Sprachaufnahme.objects.filter(recorded_by=user, language=sprache, seite__in=buch.seiten.all())

    if len(aufnahmen) == 0:
        return JsonResponse(status=400, data={'error': f'Es wurden keine Aufzeichnungen dieses Benutzers für das Buch "{buch}" auf {sprache} gefunden!'})

    for aufnahme in aufnahmen:
        aufnahme.delete()
    
    return JsonResponse(status=200, data={})
