'''
helpers.py
Here we will declare helper functions to use in other parts of the code
'''

from functools import wraps
from django.shortcuts import redirect, render
from django.urls import reverse

def no_logged_in_users_allowed(view_func):
    ''' When a logged in user opens a page meant for users that are not logged in, they 
        will get redirected to the entry page (index)'''
    wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('endnutzer:index'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def group_required_endnutzer(view_func):
    '''Protects views from members of groups other then the target'''
    wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # check for group membership of the user
        if request.user.groups.filter(name='endnutzer'):
            return view_func(request, *args, **kwargs)
        #TODO if not endnutzer, return error page
        return render(request, 'endnutzer/error.html')
    return _wrapped_view