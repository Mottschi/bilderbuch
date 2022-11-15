def is_betreiber(user):
    return user.groups.filter(name='betreiber').exists()

def not_logged_in(user):
    return not user.is_authenticated