from django.urls import path
from . import views

app_name = 'betreiber'
urlpatterns = [
    path("login", views.view_login, name="login"),
    path("logout", views.view_logout, name="logout"),
    path("", views.view_index, name="index"),
    path("login/forgot_password", views.view_reset_password, name="reset_password"),
    path("buecher", views.view_buchliste, name="buchliste"),
    path("buch/add/metadaten", views.view_create_buch, name="create_buch"),
    path("buch/edit/metadaten/<int:buch_id>", views.view_edit_buch_metadaten, name="edit_buch_metadaten"),
    path("buch/edit/seitendaten/<int:buch_id>", views.view_edit_buch_seitendaten, name="edit_buch_seitendaten"),
    path("buch/delete/<int:buch_id>", views.view_delete_buch, name="delete_buch"),
    path("buch/generatecodes/<int:buch_id>", views.view_generate_buchcodes, name="generate_buchcodes"),
    path("autoren", views.view_autorenliste, name="autorenliste"),
    path("autor/add", views.view_create_autor, name="create_autor"),
    path("autor/edit/<int:autor_id>", views.view_edit_autor, name="edit_autor"),
    path("mandant/add", views.view_create_mandant, name="create_mandant"),
    path("mandanten", views.view_mandantenliste, name="mandantenliste"),
    path("mandant/edit/<int:mandant_id>", views.view_edit_mandant, name="edit_mandant"),
    path("mandant/delete/<int:mandant_id>", views.view_delete_mandant, name="delete_mandant"),
    path("buch/exportcodes/<int:buch_id>", views.api_export_buchcodes, name="api_export_buchcodes"),
    path("buch/generatecodes/<int:buch_id>/api", views.api_generate_buchcodes, name="api_generate_buchcodes"),
    path("buch/seiten/delete/<int:buch_id>/<int:seite_id>/", views.api_delete_buch_seite, name="api_delete_buch_seite"),
    path("buch/seiten/<int:buch_id>", views.api_get_buch_seiten, name="api_get_buch_seiten"),
    path("buch/seiten/create/<int:buch_id>/", views.api_create_buch_seite, name="api_create_buch_seite"),
    path("buch/seiten/update/<int:buch_id>/<int:seite_id>/", views.api_update_buch_seite, name="api_update_buch_seite"),

]