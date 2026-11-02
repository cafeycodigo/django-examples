from django.contrib import admin
from .models import Libro, Ejemplar, Usuario, Prestamo, Multa


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("id_usuario", "rut", "nombre_completo", "email_institucional", "carrera_o_departamento", "activo")
    search_fields = ("rut", "nombre_completo", "email_institucional")
    list_filter = ("activo", "carrera_o_departamento")


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ("id_libro", "titulo", "autor", "isbn", "editorial", "anio_publicacion")
    search_fields = ("titulo", "autor", "isbn")
    list_filter = ("editorial", "anio_publicacion")


@admin.register(Ejemplar)
class EjemplarAdmin(admin.ModelAdmin):
    list_display = ("id_ejemplar", "codigo_barra", "id_libro", "estado", "ubicacion", "fecha_adquisicion")
    search_fields = ("codigo_barra", "id_libro__titulo")
    list_filter = ("estado", "ubicacion")


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ("id_prestamo", "usuario", "id_ejemplar", "fecha_prestamo", "fecha_devolucion_pactada", "fecha_devolucion_real", "estado")
    search_fields = ("usuario__username", "usuario__first_name", "usuario__last_name", "usuario__email", "id_ejemplar__codigo_barra")
    list_filter = ("estado", "fecha_prestamo", "fecha_devolucion_pactada")


@admin.register(Multa)
class MultaAdmin(admin.ModelAdmin):
    list_display = ("id_multa", "id_prestamo", "dias_retraso", "monto_multa", "pagada", "fecha_generacion")
    search_fields = ("id_prestamo__usuario__username", "id_prestamo__usuario__email")
    list_filter = ("pagada", "fecha_generacion")
