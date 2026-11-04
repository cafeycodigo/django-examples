from datetime import date, timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Ejemplar, Libro, Prestamo, Usuario


def iniciar_sesion(request):
    """Autentica con el backend de Django sin usar LoginView."""
    destino = request.POST.get("next") or request.GET.get("next", "")
    destino_seguro = url_has_allowed_host_and_scheme(
        destino,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    )

    if request.user.is_authenticated:
        return redirect(destino if destino_seguro else "index")

    error = ""
    if request.method == "POST":
        usuario = authenticate(
            request,
            username=request.POST.get("username", ""),
            password=request.POST.get("password", ""),
        )
        if usuario is not None:
            login(request, usuario)
            return redirect(destino if destino_seguro else "index")
        error = "El usuario o la contraseña no son correctos."

    return render(request, "biblioteca/login.html", {
        "error": error,
        "next": destino if destino_seguro else "",
    })


def cerrar_sesion(request):
    """Cierra la sesión activa únicamente mediante POST."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    logout(request)
    return redirect("login")


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


@login_required
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


@login_required
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


@login_required
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


@login_required
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


# =============================================================================
# CRUD DE LIBROS
# =============================================================================

def _validar_libro(libro, datos):
    """Carga los campos recibidos y devuelve errores de validación por campo."""
    libro.titulo = datos.get("titulo", "").strip()
    libro.autor = datos.get("autor", "").strip() or None
    libro.isbn = datos.get("isbn", "").strip() or None
    libro.editorial = datos.get("editorial", "").strip() or None

    anio_publicacion = datos.get("anio_publicacion", "").strip()
    libro.anio_publicacion = anio_publicacion or None

    try:
        libro.full_clean()
    except ValidationError as error:
        errores = {}
        for campo, errores_campo in error.error_dict.items():
            errores[campo] = []
            for error_campo in errores_campo:
                if campo == "titulo" and error_campo.code == "blank":
                    mensaje = "El título es obligatorio."
                elif campo == "isbn" and error_campo.code == "unique":
                    mensaje = "Ya existe un libro con este ISBN."
                elif campo == "anio_publicacion" and error_campo.code == "invalid":
                    mensaje = "El año de publicación debe ser un número entero."
                else:
                    mensaje = error_campo.messages[0]
                errores[campo].append(mensaje)
        return errores

    return {}


def libro_listar(request):
    """Muestra todos los títulos registrados en orden alfabético."""
    libros = Libro.objects.all().order_by("titulo")
    return render(request, "biblioteca/libro_list.html", {"libros": libros})


def libro_detalle(request, pk):
    """Muestra la ficha de un libro y los ejemplares físicos asociados."""
    libro = get_object_or_404(Libro, pk=pk)
    ejemplares = Ejemplar.objects.filter(id_libro=libro).order_by("codigo_barra")
    return render(request, "biblioteca/libro_detail.html", {
        "libro": libro,
        "ejemplares": ejemplares,
    })


@login_required
def libro_crear(request):
    """Crea un libro leyendo directamente los campos enviados en request.POST."""
    errores = {}
    if request.method == "POST":
        libro = Libro()
        errores = _validar_libro(libro, request.POST)
        if not errores:
            libro.save()
            messages.success(request, f"El libro «{libro.titulo}» se creó correctamente.")
            return redirect("libro_detalle", pk=libro.pk)

    return render(request, "biblioteca/libro_form.html", {
        "datos": request.POST if request.method == "POST" else {},
        "errores": errores,
        "accion": "Crear",
    })


@login_required
def libro_actualizar(request, pk):
    """Edita un libro leyendo los datos directamente desde request.POST."""
    libro = get_object_or_404(Libro, pk=pk)
    errores = {}
    if request.method == "POST":
        errores = _validar_libro(libro, request.POST)
        if not errores:
            libro.save()
            messages.success(request, f"El libro «{libro.titulo}» se actualizó correctamente.")
            return redirect("libro_detalle", pk=libro.pk)
        datos = request.POST
    else:
        datos = {
            "titulo": libro.titulo,
            "autor": libro.autor or "",
            "isbn": libro.isbn or "",
            "editorial": libro.editorial or "",
            "anio_publicacion": libro.anio_publicacion or "",
        }

    return render(request, "biblioteca/libro_form.html", {
        "datos": datos,
        "errores": errores,
        "accion": "Editar",
        "libro": libro,
    })


@login_required
def libro_eliminar(request, pk):
    """Elimina un título solo cuando no tiene ejemplares físicos asociados."""
    libro = get_object_or_404(Libro, pk=pk)

    if request.method == "POST":
        if Ejemplar.objects.filter(id_libro=libro).exists():
            messages.error(
                request,
                "No se puede eliminar este libro mientras tenga ejemplares asociados. "
                "Elimine o reasigne primero esos ejemplares.",
            )
            return redirect("libro_detalle", pk=libro.pk)

        titulo = libro.titulo
        libro.delete()
        messages.success(request, f"El libro «{titulo}» se eliminó correctamente.")
        return redirect("libro_listar")

    return render(request, "biblioteca/libro_confirm_delete.html", {"libro": libro})
