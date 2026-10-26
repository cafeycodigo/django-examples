from decimal import Decimal
from django.db.models import Avg, Count, Max, Min, Sum, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .models import Cargo, Empleado


# =============================================================================
# FUNCIÓN AUXILIAR: Convierte un Empleado en Diccionario para JSON
# =============================================================================
def empleado_a_dict(e):
    """Pasa los datos del modelo a un diccionario de Python fácil de serializar."""
    return {
        "id": e.id,
        "rut": e.rut,
        "nombre_completo": e.nombre_completo,
        "cargo": e.cargo.nombre if e.cargo else None,
        "salario": float(e.salario),
        "fecha_ingreso": str(e.fecha_ingreso),
        "activo": e.activo,
        "email": e.email,
        "telefono": e.telefono,
    }


# =============================================================================
# PARTE 1: EL CRUD (Create, Read, Update, Delete)
# =============================================================================

# 1. READ (Listar todos)
def index(request):
    # Paso 1: Consultar la base de datos con el ORM
    empleados = Empleado.objects.select_related("cargo").all().order_by("nombre_completo")

    # Paso 2: OPCIÓN WEB (HTML) - Comentada
    # return render(request, "rrhh/index.html", {"empleados": empleados})

    # (Extra pedagógico: Si abres con ?format=html en el navegador, ves la web)
    if request.GET.get("format") == "html":
        return render(request, "rrhh/index.html", {"empleados": empleados})

    # Paso 3: OPCIÓN JSON (Activa)
    data = [empleado_a_dict(e) for e in empleados]
    return JsonResponse({"total": len(data), "empleados": data}, safe=False)


# 2. READ (Ver detalle de uno solo por ID)
def empleado_detalle(request, pk):
    # Paso 1: Buscar el empleado o dar error 404 si no existe
    empleado = get_object_or_404(Empleado, pk=pk)

    # Paso 2: OPCIÓN WEB (HTML) - Comentada
    # return render(request, "rrhh/empleado_detail.html", {"empleado": empleado})

    if request.GET.get("format") == "html":
        return render(request, "rrhh/empleado_detail.html", {"empleado": empleado})

    # Paso 3: OPCIÓN JSON (Activa)
    return JsonResponse({"empleado": empleado_a_dict(empleado)})


# 3. CREATE (Crear un nuevo empleado)
@csrf_exempt
def empleado_crear(request):
    if request.method == "POST":
        # Paso 1: Obtener los datos enviados (POST tradicional o JSON)
        rut = request.POST.get("rut")
        nombre = request.POST.get("nombre_completo")
        salario = request.POST.get("salario")
        cargo_id = request.POST.get("cargo_id")

        # Paso 2: Obtener o asignar el Cargo
        cargo = get_object_or_404(Cargo, pk=cargo_id) if cargo_id else Cargo.objects.first()

        # Paso 3: Guardar en la base de datos con el ORM
        nuevo_empleado = Empleado.objects.create(
            rut=rut,
            nombre_completo=nombre,
            cargo=cargo,
            salario=Decimal(salario or 0),
            email=request.POST.get("email", ""),
            telefono=request.POST.get("telefono", ""),
        )

        # Paso 4: OPCIÓN WEB (HTML) - Comentada
        # return redirect("index")

        # Paso 5: OPCIÓN JSON (Activa)
        return JsonResponse({
            "mensaje": "Empleado creado con éxito",
            "empleado": empleado_a_dict(nuevo_empleado)
        }, status=201)

    # Si es GET:
    # OPCIÓN WEB: Mostrar formulario HTML
    # return render(request, "rrhh/empleado_form.html", {"cargos": Cargo.objects.all(), "accion": "Crear"})

    if request.GET.get("format") == "html":
        return render(request, "rrhh/empleado_form.html", {"cargos": Cargo.objects.all(), "accion": "Crear"})

    # OPCIÓN JSON: Explicar qué datos enviar
    return JsonResponse({
        "info": "Envía una petición POST con: rut, nombre_completo, salario, cargo_id",
        "cargos_disponibles": list(Cargo.objects.values("id", "nombre"))
    })


# 4. UPDATE (Actualizar datos de un empleado)
@csrf_exempt
def empleado_actualizar(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)

    if request.method == "POST":
        # Paso 1: Actualizar los campos que vengan en la petición
        if "nombre_completo" in request.POST:
            empleado.nombre_completo = request.POST.get("nombre_completo")
        if "salario" in request.POST:
            empleado.salario = Decimal(request.POST.get("salario"))
        if "cargo_id" in request.POST:
            empleado.cargo_id = request.POST.get("cargo_id")

        # Paso 2: Guardar los cambios con el ORM
        empleado.save()

        # Paso 3: OPCIÓN WEB (HTML) - Comentada
        # return redirect("empleado_detalle", pk=empleado.id)

        # Paso 4: OPCIÓN JSON (Activa)
        return JsonResponse({
            "mensaje": "Empleado actualizado",
            "empleado": empleado_a_dict(empleado)
        })

    # Si es GET:
    # OPCIÓN WEB: Mostrar formulario con datos cargados
    # return render(request, "rrhh/empleado_form.html", {"empleado": empleado, "cargos": Cargo.objects.all(), "accion": "Actualizar"})

    if request.GET.get("format") == "html":
        return render(request, "rrhh/empleado_form.html", {"empleado": empleado, "cargos": Cargo.objects.all(), "accion": "Actualizar"})

    return JsonResponse({
        "info": f"Envía un POST para modificar el empleado {pk}",
        "empleado_actual": empleado_a_dict(empleado)
    })


# 5. DELETE (Eliminar empleado)
@csrf_exempt
def empleado_eliminar(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)

    if request.method == "POST":
        # Paso 1: Borrar del modelo con el ORM
        nombre = empleado.nombre_completo
        empleado.delete()

        # Paso 2: OPCIÓN WEB (HTML) - Comentada
        # return redirect("index")

        # Paso 3: OPCIÓN JSON (Activa)
        return JsonResponse({"mensaje": f"Empleado '{nombre}' eliminado correctamente"})

    # Si es GET:
    # OPCIÓN WEB: Mostrar pantalla de confirmación
    # return render(request, "rrhh/empleado_confirm_delete.html", {"empleado": empleado})

    if request.GET.get("format") == "html":
        return render(request, "rrhh/empleado_confirm_delete.html", {"empleado": empleado})

    return JsonResponse({
        "advertencia": f"¿Seguro que deseas eliminar a {empleado.nombre_completo}? Envía un POST para confirmar."
    })


# =============================================================================
# PARTE 2: CONSULTAS DEL ORM ("Preguntas Frecuentes / Random")
# =============================================================================

# Pregunta A: ¿Cuántos empleados tienen un salario mayor a $X?
# Prueba: /rrhh/consultas/salario-mayor/?monto=1000000
def consulta_salario_mayor(request):
    monto = Decimal(request.GET.get("monto", "1000000"))

    # Consulta con filter y operador __gt (greater than / mayor que)
    empleados = Empleado.objects.filter(salario__gt=monto)
    cantidad = empleados.count()

    contexto = {
        "pregunta": f"¿Cuántos empleados ganan más de ${monto:,.2f}?",
        "cantidad": cantidad,
        "empleados": empleados,
    }

    # OPCIÓN WEB (HTML) - Comentada:
    # return render(request, "rrhh/consulta_resultado.html", contexto)

    if request.GET.get("format") == "html":
        return render(request, "rrhh/consulta_resultado.html", contexto)

    # OPCIÓN JSON (Activa):
    return JsonResponse({
        "pregunta": f"¿Cuántos empleados ganan más de ${float(monto):,.2f}?",
        "total_encontrados": cantidad,
        "empleados": [empleado_a_dict(e) for e in empleados]
    })


# Pregunta B: ¿Quién o quiénes tienen el salario más alto?
# Prueba: /rrhh/consultas/salario-maximo/
def consulta_salario_maximo(request):
    # 1. Obtenemos el monto más alto usando Max()
    max_salario = Empleado.objects.aggregate(Max("salario"))["salario__max"]

    # 2. Buscamos al empleado o empleados que ganan ese monto máximo
    empleados_top = Empleado.objects.filter(salario=max_salario) if max_salario else []

    contexto = {
        "pregunta": "¿Quién tiene el salario más alto?",
        "salario_maximo": max_salario,
        "cantidad": empleados_top.count() if max_salario else 0,
        "empleados": empleados_top,
    }

    # OPCIÓN WEB (HTML) - Comentada:
    # return render(request, "rrhh/consulta_resultado.html", contexto)

    if request.GET.get("format") == "html":
        return render(request, "rrhh/consulta_resultado.html", contexto)

    # OPCIÓN JSON (Activa):
    return JsonResponse({
        "pregunta": "¿Quién tiene el salario más alto?",
        "salario_maximo": float(max_salario) if max_salario else 0,
        "empleados": [empleado_a_dict(e) for e in empleados_top]
    })


# Pregunta C: ¿Cuántos empleados pertenecen al cargo X?
# Prueba: /rrhh/consultas/por-cargo/?cargo=Analista
def consulta_por_cargo(request):
    nombre_cargo = request.GET.get("cargo", "Analista")

    # Filtramos por el nombre del cargo relacionado (__icontains no distingue mayúsculas)
    empleados = Empleado.objects.filter(cargo__nombre__icontains=nombre_cargo)

    contexto = {
        "pregunta": f"¿Cuántos empleados tienen el cargo '{nombre_cargo}'?",
        "cargo_buscado": nombre_cargo,
        "cantidad": empleados.count(),
        "empleados": empleados,
    }

    # OPCIÓN WEB (HTML) - Comentada:
    # return render(request, "rrhh/consulta_resultado.html", contexto)

    if request.GET.get("format") == "html":
        return render(request, "rrhh/consulta_resultado.html", contexto)

    # OPCIÓN JSON (Activa):
    return JsonResponse({
        "cargo": nombre_cargo,
        "total_empleados": empleados.count(),
        "empleados": [empleado_a_dict(e) for e in empleados]
    })


# Pregunta D: Métricas globales (promedio, suma, mínimo y máximo de salarios)
# Prueba: /rrhh/consultas/estadisticas/
def consulta_estadisticas_globales(request):
    stats = Empleado.objects.aggregate(
        total=Count("id"),
        promedio=Avg("salario"),
        maximo=Max("salario"),
        minimo=Min("salario"),
        planilla_total=Sum("salario"),
    )

    datos = {
        "total_empleados": stats["total"] or 0,
        "salario_promedio": float(stats["promedio"] or 0),
        "salario_maximo": float(stats["maximo"] or 0),
        "salario_minimo": float(stats["minimo"] or 0),
        "planilla_total": float(stats["planilla_total"] or 0),
    }

    # OPCIÓN WEB (HTML) - Comentada:
    # return render(request, "rrhh/consulta_estadisticas.html", {"metricas": datos})

    if request.GET.get("format") == "html":
        return render(request, "rrhh/consulta_estadisticas.html", {"metricas": datos})

    # OPCIÓN JSON (Activa):
    return JsonResponse({"estadisticas_empresa": datos})


# Pregunta E: Resumen por cada Cargo (Group By en SQL con annotate)
# Prueba: /rrhh/consultas/resumen-cargos/
def consulta_resumen_cargos(request):
    # annotate agrega cálculos a cada fila de Cargo
    cargos = Cargo.objects.annotate(
        total_empleados=Count("empleados"),
        promedio_salario=Avg("empleados__salario"),
    )

    lista = [
        {
            "cargo": c.nombre,
            "total_empleados": c.total_empleados,
            "promedio_salario": float(c.promedio_salario or 0),
        }
        for c in cargos
    ]

    # OPCIÓN WEB (HTML) - Comentada:
    # return render(request, "rrhh/consulta_resumen_cargos.html", {"resumen": lista})

    if request.GET.get("format") == "html":
        return render(request, "rrhh/consulta_resumen_cargos.html", {"resumen": lista})

    # OPCIÓN JSON (Activa):
    return JsonResponse({"cargos": lista})


# =============================================================================
# NUEVAS PROPUESTAS DE CONSULTAS CON EL ORM DE DJANGO
# =============================================================================

# Propuesta 1: Rango Salarial (BETWEEN en SQL usando __range)
# Prueba: /rrhh/consultas/rango-salarios/?min=800000&max=1500000
def consulta_rango_salarial(request):
    min_salario = Decimal(request.GET.get("min", "800000"))
    max_salario = Decimal(request.GET.get("max", "1500000"))

    # ORM: filter(salario__range=(min, max))
    empleados = Empleado.objects.filter(salario__range=(min_salario, max_salario)).order_by("salario")

    contexto = {
        "pregunta": f"¿Qué empleados ganan entre ${min_salario:,.2f} y ${max_salario:,.2f}?",
        "cantidad": empleados.count(),
        "empleados": empleados,
    }

    # OPCIÓN WEB (HTML) - Comentada:
    # return render(request, "rrhh/consulta_resultado.html", contexto)

    if request.GET.get("format") == "html":
        return render(request, "rrhh/consulta_resultado.html", contexto)

    # OPCIÓN JSON (Activa):
    return JsonResponse({
        "pregunta": f"Empleados con salario entre {float(min_salario)} y {float(max_salario)}",
        "total": empleados.count(),
        "empleados": [empleado_a_dict(e) for e in empleados]
    })


# Propuesta 2: Búsqueda por texto (ILIKE '%texto%' con __icontains)
# Prueba: /rrhh/consultas/buscar/?q=ana
def consulta_buscar_nombre(request):
    termino = request.GET.get("q", "ana")

    # ORM: filter(nombre_completo__icontains=termino)
    empleados = Empleado.objects.filter(nombre_completo__icontains=termino)

    contexto = {
        "pregunta": f"Búsqueda de empleados que contengan '{termino}'",
        "cantidad": empleados.count(),
        "empleados": empleados,
    }

    # OPCIÓN WEB (HTML) - Comentada:
    # return render(request, "rrhh/consulta_resultado.html", contexto)

    if request.GET.get("format") == "html":
        return render(request, "rrhh/consulta_resultado.html", contexto)

    # OPCIÓN JSON (Activa):
    return JsonResponse({
        "termino_busqueda": termino,
        "coincidencias": empleados.count(),
        "empleados": [empleado_a_dict(e) for e in empleados]
    })


# Propuesta 3: Top N con salarios más altos (order_by y LIMIT [:N])
# Prueba: /rrhh/consultas/top/?limite=3
def consulta_top_salarios(request):
    limite = int(request.GET.get("limite", "3"))

    # ORM: order_by("-salario")[:limite]  ('-' significa orden descendente)
    top_empleados = Empleado.objects.select_related("cargo").order_by("-salario")[:limite]

    contexto = {
        "pregunta": f"Top {limite} empleados con mayores salarios",
        "cantidad": len(top_empleados),
        "empleados": top_empleados,
    }

    # OPCIÓN WEB (HTML) - Comentada:
    # return render(request, "rrhh/consulta_resultado.html", contexto)

    if request.GET.get("format") == "html":
        return render(request, "rrhh/consulta_resultado.html", contexto)

    # OPCIÓN JSON (Activa):
    return JsonResponse({
        "ranking": f"Top {limite} mejores salarios",
        "empleados": [empleado_a_dict(e) for e in top_empleados]
    })


# Propuesta 4: Exclusión y verificación de existencia (exclude() y exists())
# Prueba: /rrhh/consultas/inactivos/
def consulta_inactivos(request):
    # ORM: exclude(activo=True) es equivalente a filter(activo=False)
    inactivos = Empleado.objects.exclude(activo=True)

    # ORM: .exists() devuelve True o False de forma rápida sin cargar registros a memoria
    hay_inactivos = inactivos.exists()

    contexto = {
        "pregunta": "¿Hay empleados dados de baja o inactivos?",
        "cantidad": inactivos.count(),
        "empleados": inactivos,
    }

    # OPCIÓN WEB (HTML) - Comentada:
    # return render(request, "rrhh/consulta_resultado.html", contexto)

    if request.GET.get("format") == "html":
        return render(request, "rrhh/consulta_resultado.html", contexto)

    # OPCIÓN JSON (Activa):
    return JsonResponse({
        "hay_inactivos": hay_inactivos,
        "total_inactivos": inactivos.count(),
        "empleados": [empleado_a_dict(e) for e in inactivos]
    })


# Propuesta 5: Consulta combinada con OR usando objetos Q
# Pregunta: Empleados inactivos O que ganen menos de $600.000
# Prueba: /rrhh/consultas/alerta-sueldos/
def consulta_avanzada_q(request):
    # ORM: Q(...) | Q(...) genera un operador SQL OR
    filtro_alerta = Q(activo=False) | Q(salario__lt=600000)
    empleados_alerta = Empleado.objects.filter(filtro_alerta)

    contexto = {
        "pregunta": "Empleados inactivos O con salario menor a $600.000 (Operador Q)",
        "cantidad": empleados_alerta.count(),
        "empleados": empleados_alerta,
    }

    # OPCIÓN WEB (HTML) - Comentada:
    # return render(request, "rrhh/consulta_resultado.html", contexto)

    if request.GET.get("format") == "html":
        return render(request, "rrhh/consulta_resultado.html", contexto)

    # OPCIÓN JSON (Activa):
    return JsonResponse({
        "criterio": "Inactivos O salario menor a 600000",
        "total_encontrados": empleados_alerta.count(),
        "empleados": [empleado_a_dict(e) for e in empleados_alerta]
    })



# Panel visual general para ver todos los resultados en una sola pantalla
def panel_consultas_web(request):
    return render(request, "rrhh/consultas_dashboard.html", {
        "metricas": Empleado.objects.aggregate(
            total_activos=Count("id"),
            promedio=Avg("salario"),
            maximo=Max("salario"),
            total_planilla=Sum("salario"),
        ),
        "empleados_top": Empleado.objects.order_by("-salario")[:3],
        "mayores_millon": Empleado.objects.filter(salario__gt=1000000),
        "monto_filtro": 1000000,
        "resumen_cargos": Cargo.objects.annotate(
            total_empleados=Count("empleados"),
            salario_promedio=Avg("empleados__salario"),
        ),
    })
