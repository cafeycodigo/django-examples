"""
=============================================================================
GUÍA PEDAGÓGICA DEL ORM DE DJANGO - APLICACIÓN FÚTBOL & CAMPEONATOS
=============================================================================
En este módulo explicamos cómo gestionar campeonatos de fútbol chileno
(Primera División y Primera B), partidos simulados, incidencias (goleadas,
lesionados, tarjetas amarillas y rojas) y analítica con el ORM de Django:

  1. SELECT *      -> Consultar todos los partidos, clubes y jugadores (.all())
  2. WHERE         -> Filtrar goleadas, lesionados y tarjetas amarillas (.filter())
  3. ORDER BY      -> Tablas de goleadores y orden cronológico (.order_by())
  4. JOIN          -> Unir partido con club local, visita e incidencias (.select_related())
  5. AGGREGATIONS  -> Estadísticas (COUNT, SUM, AVG) y tabla de posiciones (.aggregate() y .annotate())

Todas las respuestas se devuelven en formato JSON estructurado y autodocumentado.
=============================================================================
"""

from django.db.models import Avg, Count, Max, Min, Sum, Q, F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Club, Jugador, Campeonato, Partido, Incidencia


# =============================================================================
# FUNCIONES AUXILIARES DE SERIALIZACIÓN
# =============================================================================
def partido_a_dict(p, incluir_incidencias=False):
    """Serializa un partido a formato diccionario para JSON."""
    data = {
        "id": p.id,
        "campeonato": p.campeonato.nombre,
        "division": p.campeonato.get_division_display(),
        "jornada": p.jornada,
        "fecha": p.fecha_partido.strftime("%Y-%m-%d %H:%M"),
        "estadio": p.estadio,
        "resultado": f"{p.club_local.nombre_corto} {p.goles_local} - {p.goles_visita} {p.club_visita.nombre_corto}",
        "local": {
            "id": p.club_local.id,
            "nombre": p.club_local.nombre,
            "sigla": p.club_local.nombre_corto,
            "goles": p.goles_local,
            "color": p.club_local.color_primario,
        },
        "visita": {
            "id": p.club_visita.id,
            "nombre": p.club_visita.nombre,
            "sigla": p.club_visita.nombre_corto,
            "goles": p.goles_visita,
            "color": p.club_visita.color_primario,
        },
        "total_goles": p.total_goles,
        "es_goleada": p.es_goleada,
        "publico": p.publico_asistente,
        "estado": p.estado,
    }
    if incluir_incidencias:
        data["incidencias"] = [
            {
                "minuto": inc.minuto,
                "tipo": inc.get_tipo_display(),
                "jugador": inc.jugador.nombre_completo,
                "club": inc.club.nombre_corto,
                "detalle": inc.detalle,
                "gravedad": inc.get_gravedad_lesion_display() if inc.gravedad_lesion else None,
            }
            for inc in p.incidencias.select_related("jugador", "club").order_by("minuto")
        ]
    return data


# =============================================================================
# 0. VISTA PRINCIPAL (INDEX): MENÚ Y DEMOSTRACIÓN COMPLETA DEL ORM
# =============================================================================
def index(request):
    """
    Punto de entrada de la aplicación Fútbol.
    Muestra la guía completa del ORM y permite ejecutar consultas con ?paso=
    """
    paso = request.GET.get("paso", "").lower().strip()

    if paso == "select":
        return orm_select_all(request)
    elif paso == "where":
        return orm_where(request)
    elif paso in ["order", "order_by", "orderby"]:
        return orm_order_by(request)
    elif paso == "join":
        return orm_join(request)
    elif paso in ["agregaciones", "agg"]:
        return orm_agregaciones(request)
    elif paso == "goleadas":
        return orm_goleadas(request)
    elif paso == "lesionados":
        return orm_lesionados(request)
    elif paso in ["tarjetas", "sancionados"]:
        return orm_sancionados(request)
    elif paso in ["posiciones", "tabla"]:
        return orm_tabla_posiciones(request)
    elif paso == "goleadores":
        return orm_goleadores(request)
    elif paso == "todos":
        # Ejecución pedagógica combinada
        total_partidos = Partido.objects.count()
        total_goles = Partido.objects.aggregate(total=Sum("goles_local") + Sum("goles_visita"))["total"] or 0
        total_amarillas = Incidencia.objects.filter(tipo="tarjeta_amarilla").count()
        total_rojas = Incidencia.objects.filter(tipo="tarjeta_roja").count()
        total_lesiones = Incidencia.objects.filter(tipo="lesion").count()
        goleadas_count = Partido.objects.filter(Q(goles_local__gte=F("goles_visita") + 3) | Q(goles_visita__gte=F("goles_local") + 3) | Q(goles_local + F("goles_visita") >= 4)).count()

        return JsonResponse({
            "titulo": "Resumen Integral: Fútbol Chileno y Campeonatos con Django ORM",
            "kpis": {
                "total_clubes": Club.objects.count(),
                "clubes_primera": Club.objects.filter(division="primera").count(),
                "clubes_primera_b": Club.objects.filter(division="primera_b").count(),
                "total_jugadores": Jugador.objects.count(),
                "total_partidos_disputados": total_partidos,
                "total_goles_anotados": total_goles,
                "partidos_con_goleada": goleadas_count,
                "tarjetas_amarillas_mostradas": total_amarillas,
                "tarjetas_rojas_mostradas": total_rojas,
                "lesiones_registradas": total_lesiones,
            },
            "enlaces_demostracion": {
                "select_all": "/futbol/select-all/",
                "where_filtros": "/futbol/where/",
                "order_by": "/futbol/order-by/",
                "join_relaciones": "/futbol/join/",
                "agregaciones": "/futbol/agregaciones/",
                "partidos_goleadas": "/futbol/goleadas/",
                "informe_lesionados": "/futbol/lesionados/",
                "jugadores_con_amarillas": "/futbol/sancionados/",
                "tabla_posiciones": "/futbol/tabla-posiciones/",
                "tabla_goleadores": "/futbol/goleadores/",
            }
        }, json_dumps_params={"indent": 2, "ensure_ascii": False})

    return JsonResponse({
        "modulo": "Gestión de Campeonatos de Fútbol Chileno con Django ORM",
        "descripcion": (
            "API que simula campeonatos chilenos de Primera División y Primera B, "
            "registrando resultados de partidos, goleadas, jugadores lesionados y amonestados."
        ),
        "menu_lecciones_orm": {
            "paso_1_select": {
                "nombre": "SELECT *",
                "descripcion": "Consultar clubes, partidos o jugadores.",
                "url": "/futbol/select-all/",
                "sql": "SELECT * FROM futbol_partido LIMIT 10;",
                "orm": "Partido.objects.all()[:10]",
            },
            "paso_2_where": {
                "nombre": "WHERE (Filtros específicos)",
                "descripcion": "Filtrar partidos por goleadas, lesionados o tarjetas amarillas.",
                "url": "/futbol/where/",
                "sql": "SELECT * FROM futbol_incidencia WHERE tipo = 'tarjeta_amarilla';",
                "orm": "Incidencia.objects.filter(tipo='tarjeta_amarilla')",
            },
            "paso_3_order_by": {
                "nombre": "ORDER BY (Ordenamiento)",
                "descripcion": "Ordenar partidos con más goles o tabla de goleadores.",
                "url": "/futbol/order-by/",
                "sql": "SELECT * FROM futbol_partido ORDER BY (goles_local + goles_visita) DESC;",
                "orm": "Partido.objects.annotate(total=F('goles_local') + F('goles_visita')).order_by('-total')",
            },
            "paso_4_join": {
                "nombre": "JOIN (.select_related())",
                "descripcion": "Unir Partido con Club Local y Visita sin consultas N+1.",
                "url": "/futbol/join/",
                "sql": "SELECT p.*, cl.nombre, cv.nombre FROM futbol_partido p INNER JOIN futbol_club cl ...",
                "orm": "Partido.objects.select_related('club_local', 'club_visita', 'campeonato')",
            },
            "paso_5_agregaciones": {
                "nombre": "AGGREGATIONS (COUNT, SUM, AVG)",
                "descripcion": "Estadísticas globales del torneo y cálculos matemáticos.",
                "url": "/futbol/agregaciones/",
                "sql": "SELECT COUNT(*), AVG(goles_local + goles_visita) FROM futbol_partido;",
                "orm": "Partido.objects.aggregate(total_partidos=Count('id'), promedio_goles=Avg(...))",
            },
            "consultas_especificas_campeonato": {
                "quien_se_lesiono": "/futbol/lesionados/ (o ?paso=lesionados)",
                "quien_tuvo_amarilla": "/futbol/sancionados/ (o ?paso=tarjetas)",
                "partidos_con_goleada": "/futbol/goleadas/ (o ?paso=goleadas)",
                "tabla_de_posiciones": "/futbol/tabla-posiciones/ (o ?paso=posiciones)",
                "tabla_de_goleadores": "/futbol/goleadores/ (o ?paso=goleadores)",
            }
        }
    }, json_dumps_params={"indent": 2, "ensure_ascii": False})


# =============================================================================
# 1. SELECT * -> Partido.objects.all()
# =============================================================================
def orm_select_all(request):
    """
    PASO 1: SELECT * (Consultar partidos)
    SQL: SELECT * FROM futbol_partido LIMIT 10;
    ORM: Partido.objects.select_related('club_local', 'club_visita', 'campeonato')[:10]
    """
    limite = int(request.GET.get("limite", 10))
    partidos = (
        Partido.objects.select_related("club_local", "club_visita", "campeonato")
        .all()[:limite]
    )

    return JsonResponse({
        "leccion": "Paso 1: SELECT *",
        "sql_equivalente": f"SELECT * FROM futbol_partido LIMIT {limite};",
        "django_orm": f"Partido.objects.select_related('club_local', 'club_visita', 'campeonato').all()[:{limite}]",
        "total_partidos_en_bd": Partido.objects.count(),
        "partidos": [partido_a_dict(p) for p in partidos],
    }, json_dumps_params={"indent": 2, "ensure_ascii": False})


# =============================================================================
# 2. WHERE -> Incidencia.objects.filter() / Partido.objects.filter()
# =============================================================================
def orm_where(request):
    """
    PASO 2: WHERE (Filtros en el campeonato)
    Demuestra filtros específicos:
      A. Quiénes recibieron tarjeta amarilla
      B. Quiénes sufrieron lesiones
      C. Clubes de Primera División vs Primera B
    """
    # Consulta A: Jugadores con tarjeta amarilla
    # SQL: SELECT * FROM futbol_incidencia WHERE tipo = 'tarjeta_amarilla';
    amarillas = (
        Incidencia.objects.filter(tipo="tarjeta_amarilla")
        .select_related("jugador", "club", "partido")
        .order_by("-id")[:5]
    )

    # Consulta B: Jugadores que se lesionaron en el campeonato
    # SQL: SELECT * FROM futbol_incidencia WHERE tipo = 'lesion';
    lesionados = (
        Incidencia.objects.filter(tipo="lesion")
        .select_related("jugador", "club", "partido")
        .order_by("-id")[:5]
    )

    # Consulta C: Clubes clasificados en Primera División
    # SQL: SELECT * FROM futbol_club WHERE division = 'primera';
    clubes_primera = Club.objects.filter(division="primera")

    return JsonResponse({
        "leccion": "Paso 2: Cláusula WHERE con .filter()",
        "demostraciones": [
            {
                "caso": "A. Jugadores con Tarjeta Amarilla en el Campeonato",
                "sql": "SELECT * FROM futbol_incidencia WHERE tipo = 'tarjeta_amarilla' LIMIT 5;",
                "orm": "Incidencia.objects.filter(tipo='tarjeta_amarilla')[:5]",
                "total_tarjetas_amarillas": Incidencia.objects.filter(tipo="tarjeta_amarilla").count(),
                "muestra": [
                    {
                        "jugador": inc.jugador.nombre_completo,
                        "dorsal": inc.jugador.dorsal,
                        "club": inc.club.nombre,
                        "minuto": inc.minuto,
                        "partido": str(inc.partido),
                        "motivo": inc.detalle,
                    }
                    for inc in amarillas
                ],
            },
            {
                "caso": "B. Jugadores Lesionados durante los Partidos",
                "sql": "SELECT * FROM futbol_incidencia WHERE tipo = 'lesion' LIMIT 5;",
                "orm": "Incidencia.objects.filter(tipo='lesion')[:5]",
                "total_lesionados": Incidencia.objects.filter(tipo="lesion").count(),
                "muestra": [
                    {
                        "jugador": inc.jugador.nombre_completo,
                        "club": inc.club.nombre,
                        "minuto": inc.minuto,
                        "diagnostico": inc.detalle,
                        "gravedad": inc.get_gravedad_lesion_display(),
                        "partido": str(inc.partido),
                    }
                    for inc in lesionados
                ],
            },
            {
                "caso": "C. Clubes de Primera División de Chile",
                "sql": "SELECT * FROM futbol_club WHERE division = 'primera';",
                "orm": "Club.objects.filter(division='primera')",
                "total_primera": clubes_primera.count(),
                "clubes": list(clubes_primera.values("id", "nombre", "nombre_corto", "ciudad", "estadio")),
            },
        ]
    }, json_dumps_params={"indent": 2, "ensure_ascii": False})


# =============================================================================
# 3. ORDER BY -> Partido.objects.order_by() / Tabla de Goleadores
# =============================================================================
def orm_order_by(request):
    """
    PASO 3: ORDER BY (Ordenar resultados)
    SQL: SELECT * FROM futbol_partido ORDER BY (goles_local + goles_visita) DESC;
    ORM: Partido.objects.annotate(total_g=F('goles_local') + F('goles_visita')).order_by('-total_g')
    """
    # 1. Partidos con mayor cantidad de goles (DESC)
    partidos_mas_goles = (
        Partido.objects.select_related("club_local", "club_visita", "campeonato")
        .annotate(total_g=F("goles_local") + F("goles_visita"))
        .order_by("-total_g", "-fecha_partido")[:5]
    )

    # 2. Partidos más recientes (DESC)
    partidos_recientes = (
        Partido.objects.select_related("club_local", "club_visita", "campeonato")
        .order_by("-fecha_partido")[:5]
    )

    return JsonResponse({
        "leccion": "Paso 3: ORDER BY con .order_by()",
        "ejemplos": [
            {
                "tipo": "Partidos con más goles convertidos (Descendente)",
                "sql": "SELECT *, (goles_local + goles_visita) AS total_g FROM futbol_partido ORDER BY total_g DESC LIMIT 5;",
                "orm": "Partido.objects.annotate(total_g=F('goles_local')+F('goles_visita')).order_by('-total_g')[:5]",
                "resultados": [partido_a_dict(p) for p in partidos_mas_goles],
            },
            {
                "tipo": "Partidos más recientes en el calendario (Descendente)",
                "sql": "SELECT * FROM futbol_partido ORDER BY fecha_partido DESC LIMIT 5;",
                "orm": "Partido.objects.order_by('-fecha_partido')[:5]",
                "resultados": [partido_a_dict(p) for p in partidos_recientes],
            },
        ]
    }, json_dumps_params={"indent": 2, "ensure_ascii": False})


# =============================================================================
# 4. JOIN -> Partido.objects.select_related('club_local', 'club_visita')
# =============================================================================
def orm_join(request):
    """
    PASO 4: JOIN (.select_related() y .prefetch_related())
    Une el partido con el club local, club visita, campeonato y sus incidencias (goles, tarjetas, lesiones).
    """
    limite = int(request.GET.get("limite", 5))

    partidos = (
        Partido.objects.select_related("club_local", "club_visita", "campeonato")
        .prefetch_related("incidencias__jugador", "incidencias__club")
        .order_by("-fecha_partido")[:limite]
    )

    return JsonResponse({
        "leccion": "Paso 4: JOIN con .select_related() y .prefetch_related()",
        "sql_equivalente": (
            "SELECT p.*, cl.nombre, cv.nombre, c.nombre "
            "FROM futbol_partido p "
            "INNER JOIN futbol_club cl ON p.club_local_id = cl.id "
            "INNER JOIN futbol_club cv ON p.club_visita_id = cv.id "
            "INNER JOIN futbol_campeonato c ON p.campeonato_id = c.id "
            f"LIMIT {limite};"
        ),
        "orm_usado": "Partido.objects.select_related('club_local', 'club_visita', 'campeonato').prefetch_related('incidencias')",
        "beneficio": "Realiza la unión en SQL en una sola consulta, precargando clubes y detalles sin consultas adicionales N+1.",
        "partidos_con_join_completo": [partido_a_dict(p, incluir_incidencias=True) for p in partidos],
    }, json_dumps_params={"indent": 2, "ensure_ascii": False})


# =============================================================================
# 5. AGGREGATIONS -> COUNT, SUM, AVG
# =============================================================================
def orm_agregaciones(request):
    """
    PASO 5: AGREGACIONES (Cálculos numéricos sobre el campeonato)
    Calcula: total partidos, total goles, promedio de goles por partido,
    máximo de goles en un partido, total tarjetas amarillas, rojas y lesionados.
    """
    # Agregación sobre partidos
    partidos_stats = Partido.objects.aggregate(
        total_partidos=Count("id"),
        suma_goles_local=Sum("goles_local"),
        suma_goles_visita=Sum("goles_visita"),
        promedio_asistencia=Avg("publico_asistente"),
        max_asistencia=Max("publico_asistente"),
    )

    total_goles = (partidos_stats["suma_goles_local"] or 0) + (partidos_stats["suma_goles_visita"] or 0)
    promedio_goles_partido = round(total_goles / (partidos_stats["total_partidos"] or 1), 2)

    # Agregación sobre incidencias (tarjetas y lesiones)
    incidencias_stats = Incidencia.objects.aggregate(
        total_incidencias=Count("id"),
        total_goles_incidencias=Count("id", filter=Q(tipo="gol")),
        total_amarillas=Count("id", filter=Q(tipo="tarjeta_amarilla")),
        total_rojas=Count("id", filter=Q(tipo="tarjeta_roja")),
        total_lesiones=Count("id", filter=Q(tipo="lesion")),
    )

    # Agregación agrupada GROUP BY División
    stats_por_division = Club.objects.values("division").annotate(
        total_clubes=Count("id"),
        total_jugadores=Count("jugadores"),
    )

    return JsonResponse({
        "leccion": "Paso 5: Agregaciones (COUNT, SUM, AVG, MIN, MAX)",
        "sql_equivalente": (
            "SELECT COUNT(id), SUM(goles_local), SUM(goles_visita), AVG(publico_asistente) "
            "FROM futbol_partido;"
        ),
        "orm_usado": "Partido.objects.aggregate(total=Count('id'), suma_local=Sum('goles_local'), ...)",
        "estadisticas_globales_campeonato": {
            "total_partidos_jugados": partidos_stats["total_partidos"],
            "total_goles_anotados": total_goles,
            "promedio_goles_por_partido": promedio_goles_partido,
            "goles_de_equipos_locales": partidos_stats["suma_goles_local"],
            "goles_de_equipos_visitantes": partidos_stats["suma_goles_visita"],
            "promedio_publico_por_partido": round(partidos_stats["promedio_asistencia"] or 0),
            "partido_con_mayor_asistencia": partidos_stats["max_asistencia"],
        },
        "estadisticas_disciplinarias_y_medicas": {
            "total_tarjetas_amarillas": incidencias_stats["total_amarillas"],
            "total_tarjetas_rojas": incidencias_stats["total_rojas"],
            "total_jugadores_lesionados": incidencias_stats["total_lesiones"],
        },
        "desglose_por_division": list(stats_por_division),
    }, json_dumps_params={"indent": 2, "ensure_ascii": False})


# =============================================================================
# CONSULTAS ESPECÍFICAS SOLICITADAS POR EL USUARIO:
# =============================================================================

# A. GOLEADAS
def orm_goleadas(request):
    """
    Muestra los partidos que fueron goleadas (4 o más goles o diferencia de 3+ goles).
    """
    goleadas_qs = (
        Partido.objects.select_related("club_local", "club_visita", "campeonato")
        .annotate(total_goles_partido=F("goles_local") + F("goles_visita"))
        .filter(
            Q(total_goles_partido__gte=4)
            | Q(goles_local__gte=F("goles_visita") + 3)
            | Q(goles_visita__gte=F("goles_local") + 3)
        )
        .order_by("-total_goles_partido", "-fecha_partido")
    )

    return JsonResponse({
        "consulta": "Partidos con Goleadas en el Campeonato",
        "criterio": "Partidos con 4 o más goles totales o con diferencia de 3 o más goles.",
        "sql_equivalente": (
            "SELECT * FROM futbol_partido "
            "WHERE (goles_local + goles_visita) >= 4 "
            "OR (goles_local - goles_visita) >= 3 "
            "OR (goles_visita - goles_local) >= 3 "
            "ORDER BY (goles_local + goles_visita) DESC;"
        ),
        "orm_usado": (
            "Partido.objects.annotate(total_goles=F('goles_local') + F('goles_visita'))"
            ".filter(Q(total_goles__gte=4) | Q(goles_local__gte=F('goles_visita')+3) | ...)"
        ),
        "total_goleadas": goleadas_qs.count(),
        "partidos_goleados": [partido_a_dict(p, incluir_incidencias=True) for p in goleadas_qs[:15]],
    }, json_dumps_params={"indent": 2, "ensure_ascii": False})


# B. LESIONADOS: ¿Quién se lesionó en el campeonato?
def orm_lesionados(request):
    """
    Muestra el reporte médico de quiénes se lesionaron, diagnóstico, gravedad y en qué partido.
    """
    lesiones = (
        Incidencia.objects.filter(tipo="lesion")
        .select_related("jugador", "club", "partido", "partido__campeonato")
        .order_by("-partido__fecha_partido")
    )

    # Agrupado por club
    lesionados_por_club = (
        Club.objects.annotate(
            total_lesionados=Count("incidencias", filter=Q(incidencias__tipo="lesion"))
        )
        .filter(total_lesionados__gt=0)
        .order_by("-total_lesionados")
    )

    return JsonResponse({
        "consulta": "Reporte Médico: ¿Quién se lesionó en el campeonato?",
        "sql_equivalente": "SELECT * FROM futbol_incidencia WHERE tipo = 'lesion' ORDER BY id DESC;",
        "orm_usado": "Incidencia.objects.filter(tipo='lesion').select_related('jugador', 'club', 'partido')",
        "total_jugadores_lesionados": lesiones.count(),
        "lesionados_detallados": [
            {
                "jugador": inc.jugador.nombre_completo,
                "rut": inc.jugador.rut,
                "posicion": inc.jugador.get_posicion_display(),
                "club": inc.club.nombre,
                "division": inc.club.get_division_display(),
                "partido": str(inc.partido),
                "minuto_lesion": inc.minuto,
                "diagnostico_medico": inc.detalle,
                "gravedad": inc.get_gravedad_lesion_display(),
            }
            for inc in lesiones
        ],
        "ranking_clubes_con_mas_lesiones": [
            {"club": c.nombre, "division": c.get_division_display(), "lesionados": c.total_lesionados}
            for c in lesionados_por_club
        ],
    }, json_dumps_params={"indent": 2, "ensure_ascii": False})


# C. SANCIONADOS: ¿Quién tuvo tarjeta amarilla o roja en el campeonato?
def orm_sancionados(request):
    """
    Muestra quién tuvo tarjeta amarilla y quién fue expulsado con tarjeta roja en el campeonato.
    """
    # Jugadores con más tarjetas amarillas
    ranking_amarillas = (
        Jugador.objects.annotate(
            total_amarillas=Count("incidencias", filter=Q(incidencias__tipo="tarjeta_amarilla"))
        )
        .filter(total_amarillas__gt=0)
        .select_related("club")
        .order_by("-total_amarillas")[:20]
    )

    # Tarjetas rojas
    expulsados = (
        Incidencia.objects.filter(tipo="tarjeta_roja")
        .select_related("jugador", "club", "partido")
        .order_by("-partido__fecha_partido")
    )

    return JsonResponse({
        "consulta": "Tribunal de Disciplina: ¿Quién tuvo amarilla o roja en el campeonato?",
        "sql_equivalente": (
            "SELECT j.nombre_completo, COUNT(i.id) as total_amarillas "
            "FROM futbol_jugador j JOIN futbol_incidencia i ON ... "
            "WHERE i.tipo = 'tarjeta_amarilla' GROUP BY j.id ORDER BY total_amarillas DESC;"
        ),
        "orm_usado": (
            "Jugador.objects.annotate(total_amarillas=Count('incidencias', filter=Q(incidencias__tipo='tarjeta_amarilla')))"
            ".filter(total_amarillas__gt=0).order_by('-total_amarillas')"
        ),
        "total_tarjetas_amarillas_torneo": Incidencia.objects.filter(tipo="tarjeta_amarilla").count(),
        "total_tarjetas_rojas_torneo": expulsados.count(),
        "jugadores_con_tarjetas_amarillas": [
            {
                "jugador": j.nombre_completo,
                "club": j.club.nombre,
                "posicion": j.get_posicion_display(),
                "total_amarillas": j.total_amarillas,
                "en_riesgo_suspension": j.total_amarillas >= 3,
            }
            for j in ranking_amarillas
        ],
        "jugadores_expulsados_con_tarjeta_roja": [
            {
                "jugador": inc.jugador.nombre_completo,
                "club": inc.club.nombre,
                "partido": str(inc.partido),
                "minuto": inc.minuto,
                "motivo_expulsion": inc.detalle,
            }
            for inc in expulsados
        ],
    }, json_dumps_params={"indent": 2, "ensure_ascii": False})


# D. TABLA DE GOLEADORES
def orm_goleadores(request):
    """
    Tabla de máximos artilleros del campeonato.
    """
    goleadores = (
        Jugador.objects.annotate(
            goles=Count("incidencias", filter=Q(incidencias__tipo="gol"))
        )
        .filter(goles__gt=0)
        .select_related("club")
        .order_by("-goles", "nombre_completo")[:20]
    )

    return JsonResponse({
        "consulta": "Tabla de Goleadores del Campeonato",
        "sql_equivalente": (
            "SELECT j.nombre_completo, c.nombre, COUNT(i.id) as goles "
            "FROM futbol_jugador j "
            "JOIN futbol_club c ON j.club_id = c.id "
            "JOIN futbol_incidencia i ON i.jugador_id = j.id "
            "WHERE i.tipo = 'gol' GROUP BY j.id ORDER BY goles DESC LIMIT 20;"
        ),
        "orm_usado": (
            "Jugador.objects.annotate(goles=Count('incidencias', filter=Q(incidencias__tipo='gol')))"
            ".filter(goles__gt=0).order_by('-goles')[:20]"
        ),
        "ranking_goleadores": [
            {
                "posicion": idx + 1,
                "jugador": j.nombre_completo,
                "club": j.club.nombre,
                "sigla": j.club.nombre_corto,
                "division": j.club.get_division_display(),
                "goles_anotados": j.goles,
            }
            for idx, j in enumerate(goleadores)
        ],
    }, json_dumps_params={"indent": 2, "ensure_ascii": False})


# E. TABLA DE POSICIONES
def orm_tabla_posiciones(request):
    """
    Calcula la tabla de posiciones real sumando puntos por victorias y empates.
    """
    division = request.GET.get("division", "primera").lower()
    clubes = Club.objects.filter(division=division)

    tabla = []
    for club in clubes:
        # Partidos de local
        locales = Partido.objects.filter(club_local=club)
        # Partidos de visita
        visitas = Partido.objects.filter(club_visita=club)

        pj = locales.count() + visitas.count()

        pg = locales.filter(goles_local__gt=F("goles_visita")).count() + visitas.filter(goles_visita__gt=F("goles_local")).count()
        pe = locales.filter(goles_local=F("goles_visita")).count() + visitas.filter(goles_visita=F("goles_local")).count()
        pp = locales.filter(goles_local__lt=F("goles_visita")).count() + visitas.filter(goles_visita__lt=F("goles_local")).count()

        gf = (locales.aggregate(s=Sum("goles_local"))["s"] or 0) + (visitas.aggregate(s=Sum("goles_visita"))["s"] or 0)
        gc = (locales.aggregate(s=Sum("goles_visita"))["s"] or 0) + (visitas.aggregate(s=Sum("goles_local"))["s"] or 0)
        dg = gf - gc
        pts = (pg * 3) + pe

        tabla.append({
            "club": club.nombre,
            "sigla": club.nombre_corto,
            "ciudad": club.ciudad,
            "pj": pj,
            "pg": pg,
            "pe": pe,
            "pp": pp,
            "gf": gf,
            "gc": gc,
            "dg": dg,
            "pts": pts,
        })

    # Ordenamos por Puntos (DESC), luego Diferencia de Gol (DESC), luego Goles a Favor (DESC)
    tabla.sort(key=lambda x: (x["pts"], x["dg"], x["gf"]), reverse=True)

    for idx, item in enumerate(tabla):
        item["posicion"] = idx + 1

    return JsonResponse({
        "consulta": f"Tabla de Posiciones Oficial - {('Primera División' if division == 'primera' else 'Primera B')}",
        "division": division,
        "total_equipos": len(tabla),
        "tabla_posiciones": tabla,
    }, json_dumps_params={"indent": 2, "ensure_ascii": False})
