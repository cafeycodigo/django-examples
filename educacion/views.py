from django.db.models import Avg, Count
from django.http import JsonResponse

from .models import Alumno, Asignatura, Carrera, DetalleAsignatura, Docente, Institucion, Nota


MAX_REGISTROS = 100


def _limite(request):
    raw = request.GET.get("limite", "50")
    try:
        limite = int(raw)
    except ValueError:
        return None, JsonResponse(
            {"error": "El parámetro 'limite' debe ser un número entero."},
            status=400,
        )

    if not 1 <= limite <= MAX_REGISTROS:
        return None, JsonResponse(
            {"error": f"El parámetro 'limite' debe estar entre 1 y {MAX_REGISTROS}."},
            status=400,
        )
    return limite, None


def index(request):
    promedios = (
        Nota.objects.values("detalle_asignatura__carrera__nombre")
        .annotate(promedio=Avg("valor"), total_notas=Count("id"))
        .order_by("detalle_asignatura__carrera__nombre")
    )
    return JsonResponse(
        {
            "modulo": "Gestión de Educación Superior",
            "datos_de_demo": (
                "Instituciones, sedes y datos de estudiantes ficticios; "
                "no representan registros oficiales de instituciones reales."
            ),
            "totales": {
                "instituciones": Institucion.objects.count(),
                "carreras": Carrera.objects.count(),
                "docentes": Docente.objects.count(),
                "alumnos": Alumno.objects.count(),
                "asignaturas": Asignatura.objects.count(),
                "detalles_asignatura": DetalleAsignatura.objects.count(),
                "notas": Nota.objects.count(),
            },
            "promedios_por_carrera": [
                {
                    "carrera": fila["detalle_asignatura__carrera__nombre"],
                    "promedio": round(fila["promedio"], 2),
                    "cantidad_notas": fila["total_notas"],
                }
                for fila in promedios
            ],
            "rutas": {
                "alumnos": "/educacion/alumnos/",
                "carreras": "/educacion/carreras/",
                "asignaturas": "/educacion/asignaturas/",
                "notas": "/educacion/notas/",
            },
        },
        json_dumps_params={"ensure_ascii": False, "indent": 2},
    )


def alumnos(request):
    limite, error = _limite(request)
    if error:
        return error

    queryset = Alumno.objects.select_related("carrera", "carrera__sede", "carrera__sede__institucion")
    return JsonResponse(
        {
            "total": queryset.count(),
            "alumnos": [
                {
                    "rut": alumno.rut,
                    "nombre": f"{alumno.nombres} {alumno.apellidos}",
                    "email": alumno.email,
                    "carrera": alumno.carrera.nombre,
                    "institucion": alumno.carrera.sede.institucion.sigla,
                    "sede": alumno.carrera.sede.ciudad,
                    "cohorte": alumno.cohorte,
                    "estado": alumno.get_estado_display(),
                }
                for alumno in queryset[:limite]
            ],
        },
        json_dumps_params={"ensure_ascii": False},
    )


def carreras(request):
    limite, error = _limite(request)
    if error:
        return error

    queryset = Carrera.objects.select_related("sede", "sede__institucion").annotate(
        total_alumnos=Count("alumnos")
    )
    return JsonResponse(
        {
            "carreras": [
                {
                    "codigo": carrera.codigo,
                    "nombre": carrera.nombre,
                    "area": carrera.get_area_display(),
                    "institucion": carrera.sede.institucion.sigla,
                    "sede": carrera.sede.ciudad,
                    "duracion_semestres": carrera.duracion_semestres,
                    "total_alumnos": carrera.total_alumnos,
                }
                for carrera in queryset[:limite]
            ]
        },
        json_dumps_params={"ensure_ascii": False},
    )


def asignaturas(request):
    limite, error = _limite(request)
    if error:
        return error

    queryset = Asignatura.objects.annotate(total_ofertas=Count("ofertas"))
    return JsonResponse(
        {
            "asignaturas": [
                {
                    "codigo": asignatura.codigo,
                    "nombre": asignatura.nombre,
                    "area": asignatura.area,
                    "creditos": asignatura.creditos,
                    "total_ofertas": asignatura.total_ofertas,
                }
                for asignatura in queryset[:limite]
            ]
        },
        json_dumps_params={"ensure_ascii": False},
    )


def notas(request):
    limite, error = _limite(request)
    if error:
        return error

    queryset = Nota.objects.select_related(
        "alumno",
        "detalle_asignatura",
        "detalle_asignatura__asignatura",
        "detalle_asignatura__carrera",
    )
    return JsonResponse(
        {
            "total": queryset.count(),
            "notas": [
                {
                    "alumno": f"{nota.alumno.nombres} {nota.alumno.apellidos}",
                    "carrera": nota.detalle_asignatura.carrera.nombre,
                    "asignatura": nota.detalle_asignatura.asignatura.nombre,
                    "evaluacion": nota.get_evaluacion_display(),
                    "nota": float(nota.valor),
                    "fecha": nota.fecha.isoformat(),
                }
                for nota in queryset[:limite]
            ],
        },
        json_dumps_params={"ensure_ascii": False},
    )
