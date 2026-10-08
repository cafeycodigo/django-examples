from django.contrib import admin
from django.db.models import Count

from .models import Cargo, Empleado


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cantidad_empleados")
    search_fields = ("nombre",)
    ordering = ("nombre",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            empleados_count=Count("empleados")
        )

    @admin.display(description="Empleados")
    def cantidad_empleados(self, obj):
        return obj.empleados_count


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = (
        "rut",
        "nombre_completo",
        "cargo",
        "salario",
        "activo",
        "fecha_ingreso",
    )
    list_filter = ("cargo", "activo")
    search_fields = (
        "rut",
        "nombre_completo",
        "cargo__nombre",
        "email",
    )
    ordering = ("nombre_completo",)
    readonly_fields = ("fecha_ingreso", "fecha_creacion")
    list_select_related = ("cargo",)
    list_per_page = 25
