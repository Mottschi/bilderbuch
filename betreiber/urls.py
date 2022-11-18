from django.urls import path
from . import views

app_name = 'betreiber'
urlpatterns = [
    path("login", views.view_login, name="login"),
    path("logout", views.view_logout, name="logout"),
    path("", views.view_index, name="index"),
    path("login/forgot_password", views.view_reset_password, name="reset_password"),
]