from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Categoria, Persona, Evento, Asistencia


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "color_badge", "cantidad_eventos", "fecha_creacion")
    search_fields = ("nombre", "descripcion")
    ordering = ("nombre",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            eventos_count=Count("eventos")
        )

    @admin.display(description="Color")
    def color_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>',
            obj.color,
            obj.color,
        )

    @admin.display(description="Total Eventos")
    def cantidad_eventos(self, obj):
        return obj.eventos_count


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ("rut", "nombre_completo", "email", "telefono", "ciudad", "cantidad_asistencias")
    search_fields = ("rut", "nombre_completo", "email", "ciudad")
    ordering = ("nombre_completo",)
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            asistencias_count=Count("asistencias")
        )

    @admin.display(description="Eventos asistidos")
    def cantidad_asistencias(self, obj):
        return obj.asistencias_count


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "categoria",
        "precio_display",
        "es_gratuito",
        "fecha_inicio",
        "ubicacion",
        "cantidad_asistentes",
        "estado",
    )
    list_filter = ("categoria", "es_gratuito", "estado", "es_online")
    search_fields = ("titulo", "descripcion", "ubicacion", "organizador")
    ordering = ("-fecha_inicio",)
    date_hierarchy = "fecha_inicio"
    list_select_related = ("categoria",)
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            asistentes_count=Count("asistencias")
        )

    @admin.display(description="Valor")
    def precio_display(self, obj):
        if obj.es_free:
            return format_html('<span style="color: #10b981; font-weight: bold;">GRATIS / FREE</span>')
        return format_html('<span>${:,.0f}</span>', obj.valor)

    @admin.display(description="Asistentes")
    def cantidad_asistentes(self, obj):
        return obj.asistentes_count


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ("codigo_ticket", "evento", "persona", "precio_pagado", "asistio", "fecha_registro")
    list_filter = ("asistio", "evento__categoria", "evento__es_gratuito")
    search_fields = (
        "codigo_ticket",
        "persona__nombre_completo",
        "persona__rut",
        "persona__email",
        "evento__titulo",
    )
    list_select_related = ("evento", "persona")
    list_per_page = 25
    readonly_fields = ("fecha_registro",)
