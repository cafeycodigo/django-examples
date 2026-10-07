from django.contrib import admin

from .models import Vehiculo


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    # Registra el modelo Vehiculo en el sitio de administración.
    # Columnas que se muestran en el listado de vehículos.
    list_display = (
        "patente",
        "marca",
        "modelo",
        "anio",
        "combustible",
        "kilometraje",
        "fecha_registro",
    )
    # Filtros laterales para acotar el listado por estos campos.
    list_filter = ("marca", "combustible", "anio")
    # Campos que puede usar el buscador del listado.
    search_fields = ("patente", "marca", "modelo")
    # Muestra primero los vehículos registrados más recientemente.
    ordering = ("-fecha_registro",)
    # Evita que el ID y la fecha de registro se modifiquen desde el formulario.
    readonly_fields = ("id_vehiculo", "fecha_registro")
    # Organiza el formulario de edición en secciones y agrupa campos relacionados.
    fieldsets = (
        (
            "Datos del vehículo",
            {
                "fields": (
                    "patente",
                    ("marca", "modelo"),
                    ("anio", "combustible"),
                    ("kilometraje", "color", "capacidad_pasajeros"),
                )
            },
        ),
        # Presenta los datos generados automáticamente en una sección aparte.
        ("Registro", {"fields": ("id_vehiculo", "fecha_registro")}),
    )
    # Limita a 25 vehículos cada página del listado.
    list_per_page = 25
