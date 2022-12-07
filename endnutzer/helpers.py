'''
Helper Functions for the endnutzer part of application
'''

from django.contrib.auth.decorators import REDIRECT_FIELD_NAME
from functools import wraps
from django.contrib import messages
from django.shortcuts import resolve_url
from urllib.parse import urlparse

import os

def is_endnutzer(user):
    '''
    Tests whether the user is in the endnutzer group.
    Returns True if the user is in the group, otherwise False.
    '''
    return user.groups.filter(name='endnutzer').exists()

def is_mandantenadmin(user):
    return is_endnutzer(user) and user.is_mandantenadmin

def not_logged_in(user):
    '''
    Tests whether the user is currently non authenticated.
    Returns True for users that are not logged in, otherwise False.
    '''
    return not user.is_authenticated

# based on the example in django documentation:
# https://docs.djangoproject.com/en/4.1/topics/http/file-uploads/
# but extended to accept path/filename during function call
def handle_uploaded_file(filedata, filename):
    print('saving file in', filename)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb+') as destination:
        for chunk in filedata.chunks():
            destination.write(chunk)


# Übernahme der in Django eingebauten Funktion, erweitert um eine Fehlermeldung die im Fall, dass
# der Test fehlschlägt über messages.error angezeigt wird
def user_passes_test_with_error_message(
    test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME, error_message=None
):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            if error_message:
                messages.error(request, error_message)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if (not login_scheme or login_scheme == current_scheme) and (
                not login_netloc or login_netloc == current_netloc
            ):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login

            return redirect_to_login(path, resolved_login_url, redirect_field_name)

        return _wrapped_view

    return decorator