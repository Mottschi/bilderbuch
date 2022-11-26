from django.urls import path
from . import views

app_name = 'endnutzer'
urlpatterns = [
    path("login", views.view_login, name="login"),
    path("logout", views.view_logout, name="logout"),
    path("", views.view_index, name="index"),
    path("login/forgot_password", views.view_reset_password, name="reset_password"),
    path("registration", views.view_registration, name='registration'),
    path("library", views.view_library, name='library'),
    path("mandant/profile", views.view_mandant_profile, name='mandant_profile'),
    path("", views.view_registration, name=''),
    path("", views.view_registration, name=''),
    path("", views.view_registration, name=''),
    path("", views.view_registration, name=''),
    path("", views.view_registration, name=''),
    path("", views.view_registration, name=''),
    path("", views.view_registration, name=''),
    path("", views.view_registration, name=''),
]