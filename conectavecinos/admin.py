from django.contrib import admin
from . import models


@admin.register(models.Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "titulo", "comunidad", "estado", "prioridad", "creada_en")
    list_filter = ("estado", "prioridad", "categoria", "visibilidad", "comunidad__municipalidad")
    search_fields = ("codigo", "titulo", "descripcion")
    list_select_related = ("comunidad", "estado", "prioridad")
    readonly_fields = ("codigo", "creada_en", "actualizada_en", "cerrada_en")

    def save_model(self, request, obj, form, change):
        if change and "estado" in form.changed_data:
            nuevo_estado = obj.estado
            obj.estado_id = models.Incidencia.objects.get(pk=obj.pk).estado_id
            super().save_model(request, obj, form, change)
            obj.cambiar_estado(nuevo_estado, request.user, "Cambio registrado desde la administración.")
        else:
            super().save_model(request, obj, form, change)


@admin.register(models.Seguimiento)
class SeguimientoAdmin(admin.ModelAdmin):
    list_display = ("incidencia", "responsable", "estado_anterior", "estado_nuevo", "creada_en")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


for modelo in (
    models.Municipalidad, models.Comunidad, models.UsuarioComunidad,
    models.Rol, models.UsuarioRol, models.Categoria, models.Prioridad,
    models.EstadoIncidencia, models.UnidadMunicipal, models.Asignacion,
    models.Decision, models.Evidencia, models.Comentario, models.Apoyo,
    models.Evaluacion, models.Notificacion,
):
    admin.site.register(modelo)
