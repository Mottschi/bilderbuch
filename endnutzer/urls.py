from django.urls import path
from . import views

app_name = 'endnutzer'
urlpatterns = [
    path("", views.view_index, name="index"),
    path("login", views.view_login, name="login"),
]