'''
Helper Functions for the endnutzer part of application
'''

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