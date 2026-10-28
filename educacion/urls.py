from django.urls import path

from . import views

app_name = "educacion"

urlpatterns = [
    path("", views.index, name="index"),
    path("alumnos/", views.alumnos, name="alumnos"),
    path("carreras/", views.carreras, name="carreras"),
    path("asignaturas/", views.asignaturas, name="asignaturas"),
    path("notas/", views.notas, name="notas"),
]
