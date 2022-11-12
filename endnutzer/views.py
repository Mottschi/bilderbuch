from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from .helpers import no_logged_in_users_allowed, group_required_endnutzer
from django.contrib.auth import authenticate, login, logout

# Create your views here.
# @no_logged_in_users_allowed
def view_login(request):
    if request.method == 'POST':
        print('trying to login')
        form = LoginForm(request.POST)

        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']

            print(username, password)
            user = authenticate(request, username=username, password=password)
            print(user)
            if user is not None:
                print('logging in')
                login(request, user)
                return redirect(reverse('endnutzer:index'))
            else:
                print('unable to login')
                return render(request, 'endnutzer/login.html', {
                    'error': 'Fehler beim Einloggen',
                })
        # render index
        
    
    return render(request, 'endnutzer/login.html', {
        'form': LoginForm(),
    })

#@login_required(login_url='endnutzer/login')
#@group_required_endnutzer
def view_index(request):
    return render(request, 'endnutzer/index.html')
