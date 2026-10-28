from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html

from .models import Club, Jugador, Campeonato, Partido, Incidencia


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nombre_corto", "division_badge", "ciudad", "estadio", "colores_badge", "total_jugadores")
    list_filter = ("division", "ciudad")
    search_fields = ("nombre", "nombre_corto", "ciudad", "estadio")
    ordering = ("division", "nombre")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            jugadores_count=Count("jugadores")
        )

    @admin.display(description="División")
    def division_badge(self, obj):
        color = "#1d4ed8" if obj.division == "primera" else "#b45309"
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_division_display(),
        )

    @admin.display(description="Colores")
    def colores_badge(self, obj):
        return format_html(
            '<span style="display:inline-block; width:14px; height:14px; border-radius:50%; background:{}; border:1px solid #fff; margin-right:4px;"></span>'
            '<span style="display:inline-block; width:14px; height:14px; border-radius:50%; background:{}; border:1px solid #fff;"></span>',
            obj.color_primario,
            obj.color_secundario,
        )

    @admin.display(description="Plantel")
    def total_jugadores(self, obj):
        return f"{obj.jugadores_count} jugadores"


@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ("dorsal", "nombre_completo", "posicion", "club", "edad", "nacionalidad", "goles_count", "amarillas_count", "lesiones_count")
    list_filter = ("club__division", "posicion", "club", "nacionalidad")
    search_fields = ("nombre_completo", "rut", "club__nombre")
    ordering = ("club", "dorsal")
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            total_goles=Count("incidencias", filter=Q(incidencias__tipo="gol")),
            total_amarillas=Count("incidencias", filter=Q(incidencias__tipo="tarjeta_amarilla")),
            total_lesiones=Count("incidencias", filter=Q(incidencias__tipo="lesion")),
        )

    @admin.display(description="Goles")
    def goles_count(self, obj):
        return format_html('<span style="color:#10b981; font-weight:bold;">⚽ {}</span>', obj.total_goles)

    @admin.display(description="Amarillas")
    def amarillas_count(self, obj):
        return format_html('<span style="color:#eab308; font-weight:bold;">🟨 {}</span>', obj.total_amarillas)

    @admin.display(description="Lesiones")
    def lesiones_count(self, obj):
        return format_html('<span style="color:#ef4444; font-weight:bold;">🚑 {}</span>', obj.total_lesiones)


@admin.register(Campeonato)
class CampeonatoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "division", "temporada", "fecha_inicio", "fecha_fin", "activo")
    list_filter = ("division", "temporada", "activo")
    search_fields = ("nombre",)


@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = ("jornada", "campeonato", "partido_resultado", "fecha_partido", "estadio", "goleada_badge", "publico_asistente")
    list_filter = ("campeonato", "estado")
    search_fields = ("club_local__nombre", "club_visita__nombre", "estadio")
    date_hierarchy = "fecha_partido"
    list_select_related = ("campeonato", "club_local", "club_visita")
    list_per_page = 25

    @admin.display(description="Resultado")
    def partido_resultado(self, obj):
        return f"{obj.club_local.nombre_corto} {obj.goles_local} - {obj.goles_visita} {obj.club_visita.nombre_corto}"

    @admin.display(description="¿Goleada?")
    def goleada_badge(self, obj):
        if obj.es_goleada:
            return format_html('<span style="background-color:#ef4444; color:#fff; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:10px;">🔥 GOLEADA</span>')
        return "-"


@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ("minuto", "tipo_badge", "jugador", "club", "detalle", "gravedad_lesion", "partido")
    list_filter = ("tipo", "gravedad_lesion", "club__division")
    search_fields = ("jugador__nombre_completo", "club__nombre", "detalle")
    list_select_related = ("jugador", "club", "partido")
    list_per_page = 30

    @admin.display(description="Tipo")
    def tipo_badge(self, obj):
        colores = {
            "gol": "#10b981",
            "tarjeta_amarilla": "#eab308",
            "tarjeta_roja": "#ef4444",
            "lesion": "#a855f7",
        }
        color = colores.get(obj.tipo, "#6b7280")
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_tipo_display(),
        )
