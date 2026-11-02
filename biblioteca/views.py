from datetime import date, timedelta
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render

from .models import Ejemplar, Libro, Prestamo, Usuario


def index(request):
    prestamos = Prestamo.objects.select_related("usuario", "id_ejemplar__id_libro").order_by("-fecha_prestamo")[:15]
    total_libros = Libro.objects.count()
    total_ejemplares = Ejemplar.objects.count()
    total_usuarios = Usuario.objects.count()
    total_prestamos = Prestamo.objects.count()

    context = {
        "prestamos": prestamos,
        "total_libros": total_libros,
        "total_ejemplares": total_ejemplares,
        "total_usuarios": total_usuarios,
        "total_prestamos": total_prestamos,
        "diapositivas_crud": range(1, 18),
    }
    return render(request, "biblioteca/index.html", context)


def prestamo_crear(request):
    """Permite registrar un nuevo préstamo de libro para un usuario."""
    User = get_user_model()
    ejemplares_disponibles = Ejemplar.objects.filter(estado="DISPONIBLE").select_related("id_libro")
    usuarios = User.objects.filter(is_active=True).select_related("perfil_biblioteca").order_by("first_name", "username")

    if request.method == "POST":
        usuario_id = request.POST.get("usuario_id")
        ejemplar_id = request.POST.get("ejemplar_id")
        fecha_prestamo_str = request.POST.get("fecha_prestamo")
        dias_prestamo = int(request.POST.get("dias_prestamo", 14))

        if not usuario_id or not ejemplar_id:
            messages.error(request, "Debe seleccionar un usuario y un ejemplar disponible.")
            return render(request, "biblioteca/prestamo_form.html", {
                "ejemplares": ejemplares_disponibles,
                "usuarios": usuarios,
                "fecha_sugerida": date.today().isoformat(),
            })

        usuario = get_object_or_404(User, pk=usuario_id)
        ejemplar = get_object_or_404(Ejemplar, pk=ejemplar_id)

        fecha_prestamo = date.fromisoformat(fecha_prestamo_str) if fecha_prestamo_str else date.today()
        fecha_devolucion_pactada = fecha_prestamo + timedelta(days=dias_prestamo)

        # Crear préstamo
        prestamo = Prestamo.objects.create(
            id_ejemplar=ejemplar,
            usuario=usuario,
            fecha_prestamo=fecha_prestamo,
            fecha_devolucion_pactada=fecha_devolucion_pactada,
            estado="ACTIVO",
        )

        # Actualizar estado del ejemplar
        ejemplar.estado = "PRESTADO"
        ejemplar.save()

        messages.success(request, f"¡Préstamo #{prestamo.id_prestamo} creado exitosamente!")
        return redirect("index")

    context = {
        "ejemplares": ejemplares_disponibles,
        "usuarios": usuarios,
        "fecha_sugerida": date.today().isoformat(),
    }
    return render(request, "biblioteca/prestamo_form.html", context)


# =============================================================================
# CRUD DE USUARIO (Directo con request.POST, sin forms de Django)
# =============================================================================

def usuario_listar(request):
    """Lista todos los usuarios registrados en el sistema."""
    usuarios = Usuario.objects.select_related("user").all().order_by("-id_usuario")
    return render(request, "biblioteca/usuario_list.html", {"usuarios": usuarios})


def usuario_detalle(request, pk):
    """Muestra el detalle del usuario y sus préstamos."""
    usuario = get_object_or_404(Usuario.objects.select_related("user"), pk=pk)
    prestamos = Prestamo.objects.filter(usuario=usuario.user).select_related("id_ejemplar__id_libro").order_by("-fecha_prestamo")
    return render(request, "biblioteca/usuario_detail.html", {
        "usuario": usuario,
        "prestamos": prestamos,
    })


def usuario_crear(request):
    """Crea un nuevo usuario de biblioteca y su cuenta Django User con request.POST puro."""
    User = get_user_model()

    if request.method == "POST":
        rut = request.POST.get("rut", "").strip()
        nombre_completo = request.POST.get("nombre_completo", "").strip()
        email_institucional = request.POST.get("email_institucional", "").strip()
        carrera_o_departamento = request.POST.get("carrera_o_departamento", "").strip()
        activo = request.POST.get("activo") == "on"

        # Validaciones básicas
        if not rut or not nombre_completo or not email_institucional:
            messages.error(request, "Por favor complete los campos obligatorios: RUT, Nombre y Correo Institucional.")
            return render(request, "biblioteca/usuario_form.html", {
                "accion": "Crear",
                "datos": request.POST,
            })

        if Usuario.objects.filter(rut=rut).exists():
            messages.error(request, f"Ya existe un usuario con el RUT {rut}.")
            return render(request, "biblioteca/usuario_form.html", {
                "accion": "Crear",
                "datos": request.POST,
            })

        if Usuario.objects.filter(email_institucional=email_institucional).exists():
            messages.error(request, f"El correo institucional {email_institucional} ya está registrado.")
            return render(request, "biblioteca/usuario_form.html", {
                "accion": "Crear",
                "datos": request.POST,
            })

        # Generar username a partir del email o rut
        username = email_institucional.split("@")[0].replace(".", "_")
        if User.objects.filter(username=username).exists():
            username = f"{username}_{Usuario.objects.count() + 1}"

        # Partir nombre en first_name y last_name
        partes = nombre_completo.split()
        first_name = partes[0] if partes else ""
        last_name = " ".join(partes[1:]) if len(partes) > 1 else ""

        # Crear cuenta User
        auth_user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email_institucional,
            is_active=activo,
        )

        # Crear Usuario de Biblioteca
        usuario = Usuario.objects.create(
            user=auth_user,
            rut=rut,
            nombre_completo=nombre_completo,
            email_institucional=email_institucional,
            carrera_o_departamento=carrera_o_departamento,
            activo=activo,
        )

        messages.success(request, f"Usuario '{usuario.nombre_completo}' creado exitosamente.")
        return redirect("usuario_listar")

    return render(request, "biblioteca/usuario_form.html", {"accion": "Crear"})


def usuario_actualizar(request, pk):
    """Actualiza los datos del usuario usando request.POST directo."""
    usuario = get_object_or_404(Usuario.objects.select_related("user"), pk=pk)

    if request.method == "POST":
        rut = request.POST.get("rut", "").strip()
        nombre_completo = request.POST.get("nombre_completo", "").strip()
        email_institucional = request.POST.get("email_institucional", "").strip()
        carrera_o_departamento = request.POST.get("carrera_o_departamento", "").strip()
        activo = request.POST.get("activo") == "on"

        if not rut or not nombre_completo or not email_institucional:
            messages.error(request, "RUT, Nombre y Correo Institucional no pueden quedar vacíos.")
            return render(request, "biblioteca/usuario_form.html", {
                "accion": "Editar",
                "usuario": usuario,
            })

        # Validar si el nuevo RUT o correo choca con otro usuario distinto
        if Usuario.objects.exclude(pk=pk).filter(rut=rut).exists():
            messages.error(request, f"El RUT {rut} ya pertenece a otro usuario.")
            return render(request, "biblioteca/usuario_form.html", {
                "accion": "Editar",
                "usuario": usuario,
            })

        if Usuario.objects.exclude(pk=pk).filter(email_institucional=email_institucional).exists():
            messages.error(request, f"El correo {email_institucional} ya está registrado por otro usuario.")
            return render(request, "biblioteca/usuario_form.html", {
                "accion": "Editar",
                "usuario": usuario,
            })

        # Actualizar Usuario
        usuario.rut = rut
        usuario.nombre_completo = nombre_completo
        usuario.email_institucional = email_institucional
        usuario.carrera_o_departamento = carrera_o_departamento
        usuario.activo = activo
        usuario.save()

        # Actualizar datos en cuenta User si existe
        if usuario.user:
            partes = nombre_completo.split()
            usuario.user.first_name = partes[0] if partes else ""
            usuario.user.last_name = " ".join(partes[1:]) if len(partes) > 1 else ""
            usuario.user.email = email_institucional
            usuario.user.is_active = activo
            usuario.user.save()

        messages.success(request, f"Usuario '{usuario.nombre_completo}' actualizado con éxito.")
        return redirect("usuario_listar")

    return render(request, "biblioteca/usuario_form.html", {
        "accion": "Editar",
        "usuario": usuario,
    })


def usuario_eliminar(request, pk):
    """Elimina el usuario si no tiene préstamos activos asociados."""
    usuario = get_object_or_404(Usuario.objects.select_related("user"), pk=pk)

    if request.method == "POST":
        # Verificar si tiene préstamos activos
        prestamos_activos = Prestamo.objects.filter(usuario=usuario.user, estado="ACTIVO").count()
        if prestamos_activos > 0:
            messages.error(
                request,
                f"No se puede eliminar a {usuario.nombre_completo} porque tiene {prestamos_activos} préstamo(s) activo(s)."
            )
            return redirect("usuario_listar")

        nombre = usuario.nombre_completo
        auth_user = usuario.user
        usuario.delete()
        if auth_user:
            auth_user.delete()

        messages.success(request, f"Usuario '{nombre}' eliminado correctamente.")
        return redirect("usuario_listar")

    return render(request, "biblioteca/usuario_confirm_delete.html", {"usuario": usuario})

