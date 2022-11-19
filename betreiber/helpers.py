'''
Helper Functions for the betreiber part of application
'''

import os

def is_betreiber(user):
    '''
    Tests whether the user is in the systemadmin group.
    Returns True if the user is in the group, otherwise False.
    '''
    return user.groups.filter(name='betreiber').exists()

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
    with open(filename, 'wb+') as destination:
        for chunk in filedata.chunks():
            destination.write(chunk)