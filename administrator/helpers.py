def is_systemadmin(user):
    return user.groups.filter(name='systemadmin').exists()

def not_logged_in(user):
    return not user.is_authenticated