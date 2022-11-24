from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import Group
from django.contrib import messages
from django.core.mail import send_mail

from .forms import LoginForm, MandantenForm, EndnutzerForm, PasswordResetForm, AutorForm, GenerateBuchcodesForm, BuchForm, EditBuchForm, SeitenForm, SeitenEditForm
from .helpers import is_betreiber, not_logged_in, handle_uploaded_file

from betreiber.models import User, Autor, Mandant, Buch, Seite, Aktivierungscode
from django.conf import settings as conf_settings

import random, os

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
    Bei erfolgreichem Login wird der Benutzer auf die Hauptseite für Betreiber geleitet, 
    auf der sich Zugänge zu den verschiedenen Verwaltungskategorien befinden. (/PB0050/)
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
            except:
                messages.error(request, f'Es wurde kein Betreiberkonto mit dem Benutzernamen {username} gefunden.')
                return redirect(reverse('betreiber:login'))
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
    return render(request, 'betreiber/reset_password.html', {
        'form': PasswordResetForm(),
    })


@login_required(login_url='betreiber:login')
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def view_buchliste(request):
    '''
    /PF0201/ Der Mitarbeiter kann eine Liste aller Bücher einsehen.
    '''
    buecher = Buch.objects.all()
    return render(request, 'betreiber/buch/liste.html', {
        'buecher': buecher,
    })


@login_required(login_url='betreiber:login')
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def view_create_buch(request):
    '''
    /PF0210/ Der Mitarbeiter kann neue Bücher der Anwendung hinzufügen.
    '''
    form = BuchForm()
    if request.method == 'POST':
        form = BuchForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            buch = form.save()
            filename = f'{buch.id}_{buch.title}_{uploaded_file.name}'

            # NOTE Check this path setting once on production server
            if conf_settings.DEBUG:
                filepath = os.path.join('betreiber', 'thumbnails')
                buch.thumbnail = os.path.join(filepath, filename)
                buch.save()
                filepath = os.path.join('betreiber', 'static', filepath, filename)

            else:
                filepath = os.path.join(conf_settings.STATIC_ROOT, 'thumbnails')
                buch.thumbnail = os.path.join(filepath, filename)
                buch.save()
            
            handle_uploaded_file(uploaded_file, filepath)
            return redirect(reverse('betreiber:edit_buch_seitendaten', args=(buch.id,)))
        else:
            messages.error(request, "Bitte das Form korrekt ausfüllen.")

    return render(request, 'betreiber/buch/create.html', {
        'form': form,
    })


@login_required(login_url='betreiber:login')
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def view_edit_buch_metadaten(request, buch_id):
    '''
    /PF0220/ Der Mitarbeiter kann die Daten bestehender Bücher editieren.
    Teil 1 - Metadaten
    '''
    try:
        buch = Buch.objects.get(pk=buch_id)
    except:
        messages.errors(request, "Das gewünschte Buch konnte nicht gefunden werden.")
        return redirect(reverse('betreiber:buchliste'))
    if request.method == 'POST':
        form = EditBuchForm(request.POST, request.FILES, instance=buch)
        if form.is_valid():
            form.save()
            try:
                uploaded_file = request.FILES['file']

                # step 1: delete old file
                thumbnail = buch.thumbnail
                if conf_settings.DEBUG:
                    file_with_path = os.path.join('betreiber', 'static', thumbnail)
                else:
                    file_with_path = os.path.join(conf_settings.STATIC_ROOT, 'thumbnails', thumbnail)
                if thumbnail and os.path.exists(file_with_path):
                    os.remove(file_with_path)
               
               # step 2: save new file
                filename = f'{buch.id}_{buch.title}_{uploaded_file.name}'
                if conf_settings.DEBUG:
                    filepath = os.path.join('betreiber', 'thumbnails')
                    buch.thumbnail = os.path.join(filepath, filename)
                    buch.save()
                    filepath = os.path.join('betreiber', 'static', filepath, filename)

                else:
                    filepath = os.path.join(conf_settings.STATIC_ROOT, 'thumbnails')
                    buch.thumbnail = os.path.join(filepath, filename)
                    buch.save()
            
                handle_uploaded_file(uploaded_file, filepath)
            except Exception:
                # wenn keine Datei hochgeladen wurde ist kein weiterer Schritt noetig
                pass
            messages.success(request, f'Das Buch {buch.title} wurde erfolgreich aktualisiert')
            return redirect(reverse('betreiber:buchliste'))
        else:
            messages.error(request, f'Die Änderungen konnten nicht gespeichert werden.')
            return render(request, 'betreiber/buch/metadaten.html', {
                'form': form,
                'buch': buch,
            })

    form = EditBuchForm(instance=buch)
    return render(request, 'betreiber/buch/metadaten.html', {
        'form': form,
        'buch': buch,
    })


@login_required(login_url='betreiber:login')
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def view_edit_buch_seitendaten(request, buch_id):
    '''
    /PF0220/ Der Mitarbeiter kann die Daten bestehender Bücher editieren.
    Teil 2 - Seitendaten
    '''
    # handled via API instead
    try:
        buch = Buch.objects.get(pk=buch_id)
    except:
        messages.errors(request, "Das gewünschte Buch konnte nicht gefunden werden.")
        return redirect(reverse('betreiber:buchliste'))
    return render(request, 'betreiber/buch/seitendaten.html', {
        'buch': buch,
        'form': SeitenForm(),
        'seiten': buch.seiten.all(),
    })


@login_required(login_url='betreiber:login')
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def api_delete_buch_seite(request, buch_id, seite_id):
    '''
    Teil der in /PF0210/ beschriebenen Schnittstelle zum Editieren und Löschen von Seiten
    '''
    if request.method != 'DELETE':
        return JsonResponse(status=405, data={'error': 'Auf diesem Weg können keine Seiten gelöscht werden.'})
    try:
        buch = Buch.objects.get(pk=buch_id)
        seite = Seite.objects.get(pk=seite_id)
        seitenzahl = seite.seitenzahl
        assert seite.book == buch
        seite.delete()
        for seite in buch.seiten.filter(seitenzahl__gt=seitenzahl):
            seite.seitenzahl -= 1
            seite.save()
        status = 200
    except:
        status = 404

    return JsonResponse(status=status, data={})


@login_required(login_url='betreiber:login')
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def api_create_buch_seite(request, buch_id):
    if request.method != 'POST':
        return JsonResponse(status=405, data={'error': 'Auf diesem Weg können keine Seiten erstellt werden.'})
    
    try:
        buch = Buch.objects.get(pk=buch_id)
    except:
        return JsonResponse(status=400, data={'error': 'Das gewählte Buch konnte nicht gefunden werden.'})
    
    # Do stuff
    form = SeitenForm(request.POST, request.FILES)

    if not form.is_valid():
        return JsonResponse(status=400, data={'error': 'Das Formular wurde nicht korrekt mit gültigen Daten ausgefüllt.'})
    text = form.cleaned_data['text']
    seitenzahl = len(buch.seiten.all()) + 1

    
    uploaded_file = request.FILES['file']
    filename = f'{buch.id}_{seitenzahl}_{uploaded_file.name}'
    # NOTE Check this path setting once on production server
    if conf_settings.DEBUG:
        filepath = os.path.join('betreiber', 'seiten')
        picture = os.path.join(filepath, filename)
        filepath = os.path.join('betreiber', 'static', picture)
    else:
        raise NotImplementedError
    handle_uploaded_file(uploaded_file, filepath)
    seite = Seite.objects.create(text=text, picture=picture, book=buch, seitenzahl=seitenzahl)
    return JsonResponse(status=200, data={'seite': seite.serialize()})


@login_required(login_url='betreiber:login')
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def api_get_buch_seiten(request, buch_id):
    try:
        buch = Buch.objects.get(pk=buch_id)
        seiten = buch.seiten.all()
        seiten = [seite.serialize() for seite in seiten]
        data = {'seiten': seiten}
        status=200
    except:
        status = 404
        data = {}
    return JsonResponse(status=status, data=data)


@login_required(login_url='betreiber:login')
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def api_update_buch_seite(request, buch_id, seite_id):
    if request.method != 'POST':
        return JsonResponse(status=405, data={'error': 'Auf diesem Weg können keine Seiten aktualisiert werden.'})
    
    try:
        buch = Buch.objects.get(pk=buch_id)
    except:
        return JsonResponse(status=404, data={'error': 'Das gewählte Buch konnte nicht gefunden werden.'})

    try:
        seite = Seite.objects.get(pk=seite_id)
        assert seite.book == buch
    except:
        return JsonResponse(status=404, data={'error': 'Die angegebene Seite des Buchs konnte nicht gefunden werden.'})

    # Do stuff
    form = SeitenEditForm(request.POST, request.FILES, instance=seite)
    if not form.is_valid():
        return JsonResponse(status=400, data={'error': 'Das Formular wurde nicht korrekt mit gültigen Daten ausgefüllt.'})

    seite = form.save()

    if request.FILES.get('file', None):
        uploaded_file = request.FILES['file']
        filename = f'{buch.id}_{seite.seitenzahl}_{uploaded_file.name}'
        # NOTE Check this path setting once on production server
        if conf_settings.DEBUG:
            filepath = os.path.join('betreiber', 'seiten')
            picture = os.path.join(filepath, filename)
            filepath = os.path.join('betreiber', 'static', picture)
        else:
            raise NotImplementedError
        
        # delete old picture before saving the new one
        old_picture = seite.picture
        if conf_settings.DEBUG:
            old_picturefile_with_path = os.path.join('betreiber', 'static', old_picture)
        else:
            raise NotImplementedError
        if old_picture and os.path.exists(old_picturefile_with_path):
            os.remove(old_picturefile_with_path)
            
        handle_uploaded_file(uploaded_file, filepath)
        seite.picture = picture
        seite.save()
    return JsonResponse(status=200, data={'seite': seite.serialize()})
   

@login_required(login_url='betreiber:login')
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def view_delete_buch(request, buch_id):
    '''
    /PF0230/ Der Mitarbeiter kann Bücher aus der Anwendung löschen.
    '''
    try:
        buch = Buch.objects.get(pk=buch_id)
    except:
        messages.error(request, 'Das gewählte Buch konnte nicht gefunden werden.')
        return redirect(reverse('betreiber:buchliste'))
    if request.method == 'POST':
        buch.delete()
        messages.success(request, f'Das Buch "{buch} wurde erfolgreich gelöscht"')
        return redirect(reverse('betreiber:buchliste'))
    return render(request, 'betreiber/buch/delete.html', {'buch': buch})


#TODO REDO AND USE FRONTEND for EXPORT
@login_required(login_url='betreiber:login')
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def view_generate_buchcodes(request, buch_id):
    '''
    /PF0240/ Der Mitarbeiter kann neue Aktivierungscodes für Bücher generieren und exportieren.
    '''
    try:
        buch = Buch.objects.get(pk=buch_id)
    except:
        messages.error(request, 'Das gewünschte Buch konnte nicht gefunden werden.')
        return redirect(reverse('betreiber:buchliste'))
        
    return render(request, 'betreiber/buch/codes.html', {'buch': buch, 'form': GenerateBuchcodesForm()})


def api_generate_buchcodes(request, buch_id):
    if request.method != 'POST':
        status = 405
        return JsonResponse(status=status, data={})

    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    def generate_key():
        code = [random.choice(alphabet) for i in range(16)]
        return ''.join(code)

    try:
        buch = Buch.objects.get(pk=buch_id)
    except:
        status = 404
        return JsonResponse(status=status, data={})

    form = GenerateBuchcodesForm(request.POST)
    if form.is_valid():
        amount = form.cleaned_data['amount']
        while amount > 0:
            codes = set()
            good_codes = set()
            missing = 0
            while len(codes) < amount:
                codes.add(generate_key())
            for code in codes:
                try:
                    Aktivierungscode.objects.create(code=code, book=buch, was_exported=True)
                    good_codes.add(code)
                except:
                    missing += 1
            amount = missing                
        status = 200
        return JsonResponse(status=status, data={'codes': [code for code in good_codes], 'title': buch.title})
    else:
        status = 401
        return JsonResponse(status=status, data={})


# NOTE Diese Funktion hat bei der aktuellen Implementierung keinen Nutzen mehr
@login_required
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def api_export_buchcodes(request, buch_id):
    try:
        buch = Buch.objects.get(pk=buch_id)
    except:
        status = 404
        return JsonResponse(status=status)
    q_codes = Aktivierungscode.objects.filter(book=buch, was_exported=False)
    codes = []
    for code in q_codes:
        code.was_exported = True
        code.save()
        codes.append(code.code)
    return JsonResponse(data={'codes': codes})


@login_required(login_url='betreiber:login')
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def view_autorenliste(request):
    '''
    /PF0260/ Autorenliste
    '''
    autoren = Autor.objects.all()
    return render(request, 'betreiber/autor/liste.html', {
        'autoren': autoren,
    })


@login_required(login_url='betreiber:login')
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def view_create_autor(request):
    '''
    /PF0270/ Neuer Autor
    '''
    if request.method == 'POST':
        form = AutorForm(request.POST)
        if form.is_valid():
            autor = form.save()
            messages.success(request, f'Der Autor "{autor}" wurde erfolgreich registriert')
            return redirect(reverse('betreiber:autorenliste'))
        else:
            messages.error(request, 'Es ist ein Fehler aufgetreten:')
    else:
        form = AutorForm()

    return render(request, 'betreiber/autor/action.html', {
        'form': form,
        'action': 'erstellen'
    })


@login_required(login_url='betreiber:login')
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def view_edit_autor(request, autor_id):
    '''
    /PF0280/ Autor editieren
    '''
    try:
        autor = Autor.objects.get(pk=autor_id)
    except:
        messages.error(request, "Der angegebene Autor konnte nicht gefunden werden.")
        return redirect(reverse('betreiber:autorenliste'))

    if request.method == 'POST':
        form = AutorForm(request.POST, instance=autor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Der Autor "{autor}" wurde erfolgreich aktualisiert')
            return redirect(reverse('betreiber:autorenliste'))
        else:
            messages.error(request, 'Es ist ein Fehler aufgetreten:')
    else:
        form = AutorForm(instance=autor)

    return render(request, 'betreiber/autor/action.html', {
        'form': form,
        'action': 'editieren'
    })


@login_required(login_url='betreiber:login')
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def view_create_mandant(request):
    '''
    /PF0310/ Der Mitarbeiter kann neue Mandanten erstellen, dabei wird gleichzeitig 
    ein Benutzerkonto mit Adminrechten für den Mandanten erstellt.
    '''
    if request.method == 'POST':
        mandanten_form = MandantenForm(request.POST)
        mandanten_admin_form = EndnutzerForm(request.POST)

        if not mandanten_admin_form.is_valid():
            messages.error(request, 'Der Mandantenadmin konnte nicht erstellt werden.')
            return render(request, 'betreiber/mandant/create.html', {
                'mandanten_form': mandanten_form,
                'admin_form': mandanten_admin_form,
            })

        first_name = mandanten_admin_form.cleaned_data['first_name']
        last_name = mandanten_admin_form.cleaned_data['last_name']
        email = mandanten_admin_form.cleaned_data['email']

        if not (first_name and last_name and email):
            messages.error(request, 'Bitte alle Felder zum Mandantenadmin ausfüllen.')
            return render(request, 'betreiber/mandant/create.html', {
                'mandanten_form': mandanten_form,
                'admin_form': mandanten_admin_form,
            })

        if not mandanten_form.is_valid():
            messages.error(request, 'Der Mandant kann unter den angegebenen Daten nicht erstellt werden.')
            return render(request, 'betreiber/mandant/create.html', {
                'mandanten_form': mandanten_form,
                'admin_form': mandanten_admin_form,
            })
        
        # Mandantenadmin erstellen
        username = mandanten_admin_form.cleaned_data['username']
        password = User.objects.make_random_password()
        mandanten_admin = User.objects.create_user(username, email, password)
        mandanten_admin.first_name = first_name
        mandanten_admin.last_name = last_name

        endnutzer_group = Group.objects.get(name='endnutzer')
        mandanten_admin.groups.add(endnutzer_group)

        # Mandant erstellen
        name = mandanten_form.cleaned_data['name']
        phone = mandanten_form.cleaned_data['phone']
        street = mandanten_form.cleaned_data['street']
        house_nr = mandanten_form.cleaned_data['house_nr']
        postal_code = mandanten_form.cleaned_data['postal_code']
        country = mandanten_form.cleaned_data['country']
        city = mandanten_form.cleaned_data['city']
        manager = mandanten_admin

        try:
            mandant = Mandant.objects.create(name=name, phone=phone, street=street, house_nr=house_nr, postal_code=postal_code, country=country, manager=manager, city=city)
            mandanten_admin.mandant = mandant
            mandanten_admin.save()
        except:
            mandanten_admin.delete()
            messages.error('Mandant konnte nicht erstellt werden.')
            return render(request, 'betreiber/mandant/create.html', {
                'mandanten_form': mandanten_form,
                'admin_form': mandanten_admin_form,
            })

        send_mail(
            'Mandant und zugehöriges Administratorkonto erstellt',
            f'Hallo {first_name} {last_name},\n\nIhr Mandantenadminkonto für Projekt Bilderbuch wurde erstellt.\n\nBenutzername: {username}\nPasswort: {password}\n\nMit freundlichen Grüßen,\nProjekt Bilderbuch Betreiber {request.user.first_name}',
            'projekt.bilderbuch@gmail.com',
            [email],
            fail_silently=False,
        )
        messages.success(request, f'Der Mandant "{mandant.name}" wurde erfolgreich erstellt.')
        return redirect(reverse('betreiber:mandantenliste'))
                    
        return render(request, 'betreiber/mandant/create.html', {
            'mandanten_form': mandanten_form,
            'admin_form': mandanten_admin_form,
        })

    mandanten_form = MandantenForm()
    mandanten_admin_form = EndnutzerForm()
    return render(request, 'betreiber/mandant/create.html', {
        'mandanten_form': mandanten_form,
        'admin_form': mandanten_admin_form,
    })


@login_required(login_url='betreiber:login')
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def view_mandantenliste(request):
    '''
    /PF0320/ Der Mitarbeiter kann eine Liste aller Mandanten einsehen.
    '''
    mandanten = Mandant.objects.all()
    return render(request, 'betreiber/mandant/liste.html', {
        'mandanten': mandanten,
    })


@login_required(login_url='betreiber:login')
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def view_edit_mandant(request, mandant_id):
    '''
    /PF0330/ Der Mitarbeiter kann Mandanten editieren.
    '''
    try:
        mandant = Mandant.objects.get(pk=mandant_id)
        form = MandantenForm(instance=mandant)
    except:
        messages.error(request, f'Der zu editierende Mandant wurde nicht gefunden.')
        return redirect(reverse('betreiber:mandantenliste'))
    if request.method == 'POST':
        form = MandantenForm(request.POST, instance=mandant)
        mandanten_admin_form = EndnutzerForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'Ein Fehler ist aufgetreten.')
            return render(request, 'betreiber/mandant/edit.html', {
                'form': form,
                'mandant': mandant,
                'members': mandant.member.all(),
                'mandantenadminform': mandanten_admin_form,
            })

        manager_id = request.POST.get('manager', None)
        new_manager = None
        if manager_id:
            try:
                manager_id = int(manager_id)
                if manager_id != mandant.manager.id:
                    new_manager = User.objects.get(pk=manager_id)
                    assert new_manager.mandant == mandant
            except Exception as e:
                messages.error(request, f'Nicht in der Lage den neuen Mandantenadmin zu setzen: {e}')
                return redirect(reverse('betreiber:mandantenliste'))
        else:
            if not mandanten_admin_form.is_valid():
                messages.error(request, 'Wenn die Option "Neuen Mandantenadmin erstellen" gewählt wird, müssen auch alle Daten für den neuen Mandantenadmin angegeben werden.')
                return render(request, 'betreiber/mandant/edit.html', {
                    'form': form,
                    'mandant': mandant,
                    'members': mandant.member.all(),
                    'mandantenadminform': mandanten_admin_form,
                })

            first_name = mandanten_admin_form.cleaned_data['first_name']
            last_name = mandanten_admin_form.cleaned_data['last_name']
            email = mandanten_admin_form.cleaned_data['email']

            if not (first_name and last_name and email):
                messages.error(request, 'Bitte alle Felder zum Mandantenadmin ausfüllen.')
                return render(request, 'betreiber/mandant/edit.html', {
                    'form': form,
                    'mandant': mandant,
                    'members': mandant.member.all(),
                    'mandantenadminform': mandanten_admin_form,
                })

            username = mandanten_admin_form.cleaned_data['username']
            password = User.objects.make_random_password()
            mandanten_admin = User.objects.create_user(username, email, password)
            mandanten_admin.first_name = first_name
            mandanten_admin.last_name = last_name

            endnutzer_group = Group.objects.get(name='endnutzer')
            mandanten_admin.groups.add(endnutzer_group)

            send_mail(
                'Mandant und zugehöriges Administratorkonto erstellt',
                f'Hallo {first_name} {last_name},\n\nIhr Mandantenadminkonto für Projekt Bilderbuch wurde erstellt.\n\nBenutzername: {username}\nPasswort: {password}\n\nMit freundlichen Grüßen,\nProjekt Bilderbuch Betreiber {request.user.first_name}',
                'projekt.bilderbuch@gmail.com',
                [email],
                fail_silently=False,
            )

            mandanten_admin.mandant = mandant
            mandanten_admin.save()
            
            new_manager = mandanten_admin

        form.save()
        if new_manager:
            mandant.manager = new_manager
            mandant.save()
        messages.success(request, f'Der Mandant "{mandant.name}" wurde erfolgreich aktualisiert.')
        return redirect(reverse('betreiber:mandantenliste'))

    return render(request, 'betreiber/mandant/edit.html', {
        'form': form,
        'mandant': mandant,
        'members': mandant.member.all(),
        'mandantenadminform': EndnutzerForm(),
    })



@login_required(login_url='betreiber:login')
@user_passes_test(is_betreiber, login_url='betreiber:logout')
def view_delete_mandant(request, mandant_id):
    '''
    /PF0340/ Der Mitarbeiter kann Mandanten löschen.
    '''
    mandant = None
    try:
        mandant = Mandant.objects.get(pk=mandant_id)
    except:
        messages.error(request, f'Der zu löschende Mandant wurde nicht gefunden.')
    if request.method == 'POST':
        if mandant:
            try:
                mandant.delete()
                messages.success(request, f'Der Mandant "{mandant.name}" wurde erfolgreich gelöscht.')
            except Exception as e:
                messages.error(request, f'Beim Löschen des Mandanten "{mandant.name}" ist ein Fehler aufgetreten: {e}')
        return redirect(reverse('betreiber:mandantenliste'))
    return render(request, 'betreiber/mandant/delete.html', {'mandant': mandant,})
