from django.contrib import admin
from django.db.models import Count

from .models import (
    Alumno,
    Asignatura,
    Carrera,
    DetalleAsignatura,
    Docente,
    Institucion,
    Nota,
    Sede,
)


class SedeInline(admin.TabularInline):
    model = Sede
    extra = 0


@admin.register(Institucion)
class InstitucionAdmin(admin.ModelAdmin):
    list_display = ("sigla", "nombre", "tipo", "cantidad_sedes")
    search_fields = ("sigla", "nombre")
    inlines = [SedeInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(sedes_count=Count("sedes"))

    @admin.display(description="Sedes")
    def cantidad_sedes(self, obj):
        return obj.sedes_count


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ("nombre", "institucion", "ciudad")
    list_filter = ("institucion", "ciudad")
    search_fields = ("nombre", "ciudad", "institucion__nombre", "institucion__sigla")
    list_select_related = ("institucion",)


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "area", "sede", "duracion_semestres", "cantidad_alumnos")
    list_filter = ("area", "modalidad", "sede__institucion", "sede__ciudad")
    search_fields = ("codigo", "nombre", "titulo")
    list_select_related = ("sede", "sede__institucion")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "sede", "sede__institucion"
        ).annotate(alumnos_count=Count("alumnos"))

    @admin.display(description="Alumnos")
    def cantidad_alumnos(self, obj):
        return obj.alumnos_count


@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ("rut", "nombre_completo", "especialidad", "email", "sede")
    list_filter = ("sede__institucion", "sede__ciudad")
    search_fields = ("rut", "nombres", "apellidos", "email", "especialidad")
    list_select_related = ("sede", "sede__institucion")

    @admin.display(description="Nombre")
    def nombre_completo(self, obj):
        return f"{obj.nombres} {obj.apellidos}"


@admin.register(Asignatura)
class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "area", "creditos")
    list_filter = ("area", "creditos")
    search_fields = ("codigo", "nombre", "descripcion")


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = (
        "rut",
        "nombre_completo",
        "carrera",
        "cohorte",
        "semestre_actual",
        "estado",
        "comuna",
    )
    list_filter = ("estado", "cohorte", "semestre_actual", "carrera__area", "carrera__sede__institucion")
    search_fields = ("rut", "nombres", "apellidos", "email", "carrera__nombre")
    list_select_related = ("carrera", "carrera__sede", "carrera__sede__institucion")
    list_per_page = 50

    @admin.display(description="Nombre")
    def nombre_completo(self, obj):
        return f"{obj.nombres} {obj.apellidos}"


@admin.register(DetalleAsignatura)
class DetalleAsignaturaAdmin(admin.ModelAdmin):
    list_display = (
        "asignatura",
        "carrera",
        "docente",
        "periodo",
        "semestre",
        "seccion",
        "modalidad",
        "cupos",
    )
    list_filter = ("periodo", "semestre", "modalidad", "carrera__area")
    search_fields = ("asignatura__nombre", "carrera__nombre", "docente__nombres", "docente__apellidos")
    list_select_related = ("asignatura", "carrera", "docente")


@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ("alumno", "asignatura", "carrera", "evaluacion", "valor", "fecha")
    list_filter = ("evaluacion", "fecha", "detalle_asignatura__carrera__area")
    search_fields = ("alumno__rut", "alumno__nombres", "alumno__apellidos", "detalle_asignatura__asignatura__nombre")
    list_select_related = ("alumno", "detalle_asignatura", "detalle_asignatura__asignatura", "detalle_asignatura__carrera")
    list_per_page = 50

    @admin.display(description="Asignatura")
    def asignatura(self, obj):
        return obj.detalle_asignatura.asignatura

    @admin.display(description="Carrera")
    def carrera(self, obj):
        return obj.detalle_asignatura.carrera
