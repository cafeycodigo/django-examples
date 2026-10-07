from django.urls import path

from . import views


app_name = "automotora_basica"

urlpatterns = [
    path("", views.vehiculo_list, name="vehiculo_list"),
    path("nuevo/", views.vehiculo_create, name="vehiculo_create"),
    path("<int:pk>/editar/", views.vehiculo_update, name="vehiculo_update"),
    path("<int:pk>/eliminar/", views.vehiculo_delete, name="vehiculo_delete"),
]
