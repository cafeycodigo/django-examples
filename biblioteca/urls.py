from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("crear/", views.prestamo_crear, name="prestamo_crear"),

    # Crud de usuarios
    path("usuarios/", views.usuario_listar, name="usuario_listar"),
    path("usuarios/crear/", views.usuario_crear, name="usuario_crear"),
    path("usuarios/<int:pk>/", views.usuario_detalle, name="usuario_detalle"),
    path("usuarios/<int:pk>/editar/", views.usuario_actualizar, name="usuario_actualizar"),
    path("usuarios/<int:pk>/eliminar/", views.usuario_eliminar, name="usuario_eliminar"),


    # Crud de libros
    
]

