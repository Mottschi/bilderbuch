'''
Helper Functions for the administrator part of application
'''

def is_systemadmin(user):
    '''
    Tests whether the user is in the systemadmin group.
    Returns True if the user is in the group, otherwise False.
    '''
    return user.groups.filter(name='systemadmin').exists()

def not_logged_in(user):
    '''
    Tests whether the user is currently non authenticated.
    Returns True for users that are not logged in, otherwise False.
    '''
    return not user.is_authenticated