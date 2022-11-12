from django.urls import path
from . import views

urlpatterns = [
    path("", views.view_display_betreiberliste, name="betreiberliste"),
    path("login", views.view_login, name="login"),
    path("logout", views.view_logout, name="logout"),
    path('betreiber/create', views.view_create_betreiber, name='create_betreiber'),
    path('betreiber/edit', views.view_create_betreiber, name='create_betreiber'),
    path('betreiber/delete', views.view_create_betreiber, name='create_betreiber'),
]