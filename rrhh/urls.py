from django.urls import path

from . import views

urlpatterns = [
    # CRUD de Empleados
    path("", views.index, name="index"),
    path("empleados/<int:pk>/", views.empleado_detalle, name="empleado_detalle"),
    path("empleados/crear/", views.empleado_crear, name="empleado_crear"),
    path("empleados/<int:pk>/editar/", views.empleado_actualizar, name="empleado_actualizar"),
    path("empleados/<int:pk>/eliminar/", views.empleado_eliminar, name="empleado_eliminar"),

    # Consultas de Base de Datos y Preguntas Random (Respuestas JSON con vista web comentada)
    path("consultas/salario-mayor/", views.consulta_salario_mayor, name="consulta_salario_mayor"),
    path("consultas/salario-maximo/", views.consulta_salario_maximo, name="consulta_salario_maximo"),
    path("consultas/por-cargo/", views.consulta_por_cargo, name="consulta_por_cargo"),
    path("consultas/estadisticas/", views.consulta_estadisticas_globales, name="consulta_estadisticas"),
    path("consultas/resumen-cargos/", views.consulta_resumen_cargos, name="consulta_resumen_cargos"),

    # Nuevas Propuestas del ORM
    path("consultas/rango-salarios/", views.consulta_rango_salarial, name="consulta_rango_salarial"),
    path("consultas/buscar/", views.consulta_buscar_nombre, name="consulta_buscar_nombre"),
    path("consultas/top/", views.consulta_top_salarios, name="consulta_top_salarios"),
    path("consultas/inactivos/", views.consulta_inactivos, name="consulta_inactivos"),
    path("consultas/alerta-sueldos/", views.consulta_avanzada_q, name="consulta_avanzada_q"),

    # Vista Web para Resultados (Dashboard interactivo para visualizar todo)
    path("consultas/panel/", views.panel_consultas_web, name="panel_consultas_web"),
]

