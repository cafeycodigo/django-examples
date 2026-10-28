from django.urls import path
from . import views

app_name = "futbol"

urlpatterns = [
    # 0. Menú interactivo y dashboard de fútbol
    path("", views.index, name="index"),

    # 1. SELECT *
    path("select-all/", views.orm_select_all, name="orm_select_all"),

    # 2. WHERE (.filter())
    path("where/", views.orm_where, name="orm_where"),

    # 3. ORDER BY (.order_by())
    path("order-by/", views.orm_order_by, name="orm_order_by"),

    # 4. JOIN (.select_related())
    path("join/", views.orm_join, name="orm_join"),

    # 5. AGREGACIONES (COUNT, SUM, AVG)
    path("agregaciones/", views.orm_agregaciones, name="orm_agregaciones"),

    # Consultas temáticas específicas solicitadas:
    path("goleadas/", views.orm_goleadas, name="orm_goleadas"),
    path("lesionados/", views.orm_lesionados, name="orm_lesionados"),
    path("sancionados/", views.orm_sancionados, name="orm_sancionados"),
    path("goleadores/", views.orm_goleadores, name="orm_goleadores"),
    path("tabla-posiciones/", views.orm_tabla_posiciones, name="orm_tabla_posiciones"),
]
