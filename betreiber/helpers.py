'''
Helper Functions for the betreiber part of application
'''

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