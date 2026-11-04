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
    path("libros/", views.libro_listar, name="libro_listar"),
    path("libros/crear/", views.libro_crear, name="libro_crear"),
    path("libros/<int:pk>/", views.libro_detalle, name="libro_detalle"),
    path("libros/<int:pk>/editar/", views.libro_actualizar, name="libro_actualizar"),
    path("libros/<int:pk>/eliminar/", views.libro_eliminar, name="libro_eliminar"),
]
