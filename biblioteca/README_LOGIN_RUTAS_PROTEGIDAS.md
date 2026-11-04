# Inicio de sesión y rutas protegidas

Este documento explica el inicio y cierre de sesión de la biblioteca y cómo
restringir vistas a usuarios autenticados usando el sistema integrado de Django.

## Qué quedó implementado

- Inicio de sesión en `/biblioteca/login/`, mediante una vista propia que usa
  `authenticate()` y `login()` de Django (sin `LoginView`).
- Cierre de sesión en `/biblioteca/logout/`, mediante una vista propia que usa
  `logout()` de Django y acepta únicamente solicitudes `POST` (sin `LogoutView`).
- Redirección a la pantalla de login al acceder sin sesión a una vista protegida.
- Redirección al panel de biblioteca después de iniciar sesión.
- Vistas de consulta públicas; vistas que crean, editan o eliminan información
  requieren autenticación.
- En el panel principal se muestra el enlace de login o, si hay sesión activa,
  un botón para cerrar sesión.

## Paso 1: comprobar la configuración de autenticación

El proyecto ya debe tener instaladas las aplicaciones y middleware de
autenticación de Django. En `sistema/settings.py`, verifica que estén presentes:

```python
INSTALLED_APPS = [
    # ...
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    # ...
]

MIDDLEWARE = [
    # ...
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # ...
]
```

El contexto de plantillas también incluye
`django.contrib.auth.context_processors.auth`, necesario para usar
`user.is_authenticated` en las plantillas.

## Paso 2: configurar las redirecciones

En `sistema/settings.py` se definen estos nombres de ruta:

```python
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "index"
LOGOUT_REDIRECT_URL = "login"
```

`login_required` usa `LOGIN_URL` para enviar a personas anónimas al formulario.
Luego de autenticar, Django las dirige a `LOGIN_REDIRECT_URL`, salvo que se
estuviera intentando acceder a una ruta protegida; en ese caso se conserva el
destino con el parámetro `next`.

## Paso 3: crear las vistas propias de autenticación

En `biblioteca/views.py`, implementa el login usando las funciones de bajo
nivel del sistema de autenticación:

```python
from django.contrib.auth import authenticate, login

def iniciar_sesion(request):
    if request.method == "POST":
        usuario = authenticate(
            request,
            username=request.POST.get("username", ""),
            password=request.POST.get("password", ""),
        )
        if usuario is not None:
            login(request, usuario)
            # Redirige al destino autorizado o a la página principal.
```

`authenticate()` comprueba las credenciales usando los backends configurados;
`login()` guarda el usuario autenticado en la sesión. La vista completa también
comprueba que el parámetro `next` apunte al mismo host, para no permitir
redirecciones externas.

El logout se implementa llamando `logout(request)` y restringiendo la vista a
POST. La plantilla incluye un token CSRF en ese formulario.

## Paso 4: conectar las vistas en las rutas

En `biblioteca/urls.py`, conecta las funciones propias:

```python
urlpatterns = [
    path("login/", views.iniciar_sesion, name="login"),
    path("logout/", views.cerrar_sesion, name="logout"),
    # Las demás rutas...
]
```

Como `biblioteca.urls` está incluido bajo el prefijo `biblioteca/`, las URLs
completas son `/biblioteca/login/` y `/biblioteca/logout/`.

## Paso 5: crear la plantilla de login

La página `templates/biblioteca/login.html` envía los campos `username` y
`password` por POST e incluye `{% csrf_token %}`. El token CSRF es necesario
para aceptar el formulario de forma segura. El campo oculto `next` permite
regresar a la página protegida que el usuario solicitó antes de autenticarse.

La vista propia pasa el nombre de usuario y contraseña a `authenticate()`; no
se deben comparar contraseñas directamente ni guardar contraseñas en texto
plano.

## Paso 6: proteger una vista

### ¿Qué es un decorador?

Un decorador es una función que recibe otra función y devuelve una versión
modificada de ella. En Django, las vistas son funciones; un decorador puede
ejecutar una comprobación antes de que la vista atienda la solicitud.

La sintaxis `@decorador` es equivalente a envolver la función manualmente. Por
ejemplo:

```python
@mi_decorador
def crear_recurso(request):
    ...
```

Es la forma corta de escribir:

```python
def crear_recurso(request):
    ...

crear_recurso = mi_decorador(crear_recurso)
```

El decorador puede decidir si llama a la vista original, por ejemplo, después
de comprobar que el usuario inició sesión. Si no pasa la comprobación, puede
redirigirlo o devolver una respuesta de acceso denegado.

### Usar el decorador de Django

Para exigir que el usuario tenga una sesión iniciada, importa y aplica el
decorador incluido en Django:

```python
from django.contrib.auth.decorators import login_required

@login_required
def crear_recurso(request):
    # Esta lógica solo se ejecuta después de iniciar sesión.
    ...
```

Si una persona anónima visita esa ruta, `login_required` la redirige a la URL
definida en `LOGIN_URL` y agrega el destino solicitado en `next`. Al completar
el login, la vista `iniciar_sesion` vuelve a esa ruta si el destino es seguro.
El decorador protege todos los métodos de esa vista: por ejemplo, tanto GET
para mostrar un formulario como POST para guardar requieren sesión.

### Crear un decorador propio

Si necesitas una regla adicional que no ofrece directamente un decorador
integrado, puedes escribir uno propio. Este ejemplo reutiliza
`login_required` y añade la condición de que el usuario sea personal
administrador de la biblioteca:

```python
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def solo_personal_biblioteca(vista):
    @wraps(vista)
    @login_required
    def vista_protegida(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return vista(request, *args, **kwargs)

    return vista_protegida
```

Luego aplica el decorador sobre la vista:

```python
@solo_personal_biblioteca
def crear_recurso(request):
    ...
```

El orden importa cuando se combinan decoradores. En este ejemplo,
`@login_required` envuelve la verificación de `is_staff`: primero se exige una
sesión y después se comprueba el permiso. `@wraps` conserva el nombre y los
metadatos de la vista original, algo útil para herramientas y diagnósticos.

Este es un ejemplo de aprendizaje: `is_staff` es la regla elegida aquí; en una
aplicación real conviene modelar los permisos según los roles y políticas que
requiera el proyecto.

En esta implementación se protegen las operaciones de creación, edición y
eliminación de libros y usuarios, además de la creación de préstamos. El panel,
los listados y las fichas de libros y usuarios permanecen públicos.

### Autenticación no es autorización

`login_required` comprueba que exista una sesión, pero no distingue permisos.
Por lo tanto, cualquier usuario autenticado puede acceder a las vistas
protegidas actuales. Para limitar una acción a administradores o a usuarios con
permisos específicos, usa además `user_passes_test`, `permission_required` o
comprueba los permisos dentro de la vista. No confíes en ocultar un botón en la
plantilla como control de acceso.

## Paso 7: mostrar login y logout en una plantilla

El contexto de autenticación permite escoger qué acción mostrar:

```django
{% if user.is_authenticated %}
  <form method="post" action="{% url 'logout' %}">
    {% csrf_token %}
    <button type="submit">Cerrar sesión</button>
  </form>
{% else %}
  <a href="{% url 'login' %}">Iniciar sesión</a>
{% endif %}
```

El logout se envía por POST para evitar cerrar una sesión al visitar un enlace
accidentalmente.

## Paso 8: crear una cuenta para probar

Desde la raíz del proyecto, crea un superusuario de desarrollo:

```powershell
python manage.py createsuperuser
```

Sigue las indicaciones para definir el nombre de usuario, correo y contraseña.
Inicia el servidor y abre:

```text
http://127.0.0.1:8000/biblioteca/login/
```

Después de autenticarte, prueba una operación protegida, por ejemplo
`/biblioteca/libros/crear/`. Para probar el control sin sesión, cierra sesión y
visita esa misma dirección: Django debe redirigir a login con un parámetro
`next`.

Las cuentas de perfil que se crean desde el CRUD de usuarios de biblioteca no
reciben una contraseña en ese formulario. Para permitir que una de esas cuentas
inicie sesión, un administrador debe asignarle una contraseña desde Django
Admin; alternativamente, crea usuarios con contraseña mediante un flujo de
registro separado que valide la contraseña con las herramientas de Django.

## Paso 9: ejecutar las pruebas

Desde la raíz del proyecto:

```powershell
python manage.py test biblioteca
```

Las pruebas verifican credenciales válidas e inválidas, la redirección después
del login, el rechazo de destinos externos, el logout solo por POST, las
redirecciones de rutas protegidas y el acceso anónimo a páginas públicas.
