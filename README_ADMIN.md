# Guía del administrador de Django

El panel de administración permite gestionar vehículos y los registros de RRHH.
Abre <http://127.0.0.1:8000/admin/> e inicia sesión con una cuenta autorizada.

## Iniciar el panel

Desde la carpeta donde está `manage.py`, aplica primero las migraciones y luego
inicia el servidor:

```powershell
python manage.py migrate
python manage.py runserver
```

Si todavía no tienes un superusuario, crea uno desde la terminal:

```powershell
python manage.py createsuperuser
```

Responde las preguntas de Django y usa esas credenciales para ingresar. No
compartas la contraseña de administración.

## Configurar el admin con código

La presentación y el comportamiento de los listados se definen en `admin.py`,
dentro de cada aplicación. En este proyecto, RRHH se configura en
`rrhh/admin.py` y los vehículos en `automotora_basica/admin.py`. La clase
`ModelAdmin` conecta esas opciones con un modelo; por ejemplo:

```python
@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("rut", "nombre_completo", "cargo", "salario", "activo")
    list_filter = ("cargo", "activo")
    search_fields = ("rut", "nombre_completo", "cargo__nombre", "email")
    ordering = ("nombre_completo",)
    readonly_fields = ("fecha_ingreso", "fecha_creacion")
    list_per_page = 25
```

Cada opción controla una parte del admin:

- `@admin.register(Empleado)` registra el modelo y aplica esta configuración.
- `list_display` elige las columnas del listado. Se pueden añadir campos del
  modelo, como `telefono`, para mostrarlos allí.
- `list_filter` añade filtros laterales; aquí permite acotar por cargo o estado
  activo.
- `search_fields` indica qué campos busca el buscador. `cargo__nombre` busca
  por el nombre del cargo relacionado.
- `ordering` establece el orden inicial; un prefijo `-`, como
  `("-fecha_ingreso",)`, ordena de más reciente a más antiguo.
- `readonly_fields` muestra campos en el formulario sin permitir editarlos.
- `list_per_page` define cuántos registros se muestran por página.

Para añadir el teléfono del empleado tanto al listado como al buscador, por
ejemplo, se modifica la clase así:

```python
list_display = (
    "rut", "nombre_completo", "cargo", "salario", "activo", "telefono",
)
search_fields = ("rut", "nombre_completo", "cargo__nombre", "email", "telefono")
```

En Vehículos, `fieldsets` permite organizar los campos del formulario en
secciones y filas. La configuración actual separa los datos editables del
registro automático:

```python
readonly_fields = ("id_vehiculo", "fecha_registro")
fieldsets = (
    ("Datos del vehículo", {
        "fields": (
            "patente",
            ("marca", "modelo"),
            ("anio", "combustible"),
            ("kilometraje", "color", "capacidad_pasajeros"),
        ),
    }),
    ("Registro", {"fields": ("id_vehiculo", "fecha_registro")}),
)
```

Estas opciones cambian cómo se presentan y gestionan los modelos; para
agregar o modificar campos de la base de datos también hay que cambiar el
modelo y crear/aplicar una migración. Para cambiar columnas, filtros o secciones
del formulario normalmente basta con editar `admin.py`; Django recarga esos
cambios al ejecutar `runserver`.

## Mini tutorial: catálogo de libros y préstamos

Este ejemplo didáctico inventa un catálogo con categorías, libros, usuarios y
préstamos. Los modelos describen los datos y sus relaciones; no crean por sí
solos las tablas ni hacen que aparezcan en el admin.

```python
# biblioteca/models.py
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.nombre


class Libro(models.Model):
    titulo = models.CharField(max_length=120)
    isbn = models.CharField(max_length=17, unique=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="libros",
    )
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo


class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)

    def __str__(self):
        return self.nombre


class Prestamo(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.PROTECT)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    fecha_prestamo = models.DateField(auto_now_add=True)
    fecha_devolucion = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.libro} - {self.usuario}"
```

En este diseño, una categoría puede agrupar varios libros; cada préstamo
relaciona un libro con un usuario. `on_delete=models.PROTECT` evita borrar un
libro o usuario mientras tenga préstamos relacionados. `null=True, blank=True`
permite que la devolución todavía no tenga fecha.

### ¿Qué es una migración?

Una migración es un archivo versionado que describe un cambio en la estructura
de la base de datos a partir de los modelos: por ejemplo, crear las tablas
`Categoria`, `Libro`, `Usuario` y `Prestamo`, o agregar una columna. Crear la
migración y aplicarla son pasos separados:

1. Asegúrate de que `biblioteca` esté en `INSTALLED_APPS` en
   `sistema/settings.py`. En este proyecto actualmente no está incluida.
2. Desde la carpeta con `manage.py`, genera el archivo de migración:

   ```powershell
   python manage.py makemigrations biblioteca
   ```

3. Opcionalmente, revisa el SQL que Django ejecutaría. Usa el nombre real del
   archivo generado, por ejemplo `0001_initial`:

   ```powershell
   python manage.py sqlmigrate biblioteca 0001_initial
   ```

4. Aplica los cambios pendientes a la base de datos:

   ```powershell
   python manage.py migrate
   ```

5. Comprueba el estado de las migraciones:

   ```powershell
   python manage.py showmigrations biblioteca
   ```

`makemigrations` no modifica por sí solo la base de datos: crea el archivo de
cambio en `biblioteca/migrations/`. `migrate` sí ejecuta esos cambios en la
base de datos. Ninguno de los dos comandos registra automáticamente modelos
en el panel ni crea registros de ejemplo.

### Hacer que los modelos aparezcan en el admin

Una vez que la aplicación esté habilitada, los modelos también deben registrarse
en `biblioteca/admin.py`. Por ejemplo:

```python
from django.contrib import admin

from .models import Categoria, Libro, Prestamo, Usuario


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "isbn", "disponible")
    list_filter = ("categoria", "disponible")
    search_fields = ("titulo", "isbn", "categoria__nombre")


admin.site.register((Categoria, Usuario, Prestamo))
```

Después de guardar el archivo y ejecutar el servidor, los modelos registrados
aparecen en el índice del admin. Este código es un ejemplo conceptual: el
proyecto ya tiene modelos propios `Libro`, `Ejemplar`, `Prestamo` y `Multa` en
`biblioteca/models.py`, con una estructura distinta. No pegues encima de esos
modelos el ejemplo alternativo sin adaptarlo. Además, el `Usuario` del ejemplo
es un registro de lector de biblioteca, no una cuenta de acceso de Django.

## Empleados y cargos de RRHH

El modelo `Cargo` contiene el nombre único de cada cargo. `Empleado.cargo` es
una relación a ese modelo, por lo que el admin permite elegir un cargo existente
al crear o editar una persona. No hace falta escribir de nuevo el nombre de
cargo en cada ficha.

### Ejemplo: crear un cargo y asignarlo a un empleado

1. En el índice del admin, abre **Cargos** y selecciona **Añadir cargo**.
2. Escribe un nombre, por ejemplo `Analista de RRHH`, y guarda.
3. Abre **Empleados** y selecciona **Añadir empleado**.
4. Completa los datos del empleado y elige `Analista de RRHH` en el selector
   **Cargo**.
5. Guarda el empleado. En su listado se verá el nombre del cargo relacionado.

El nombre de cada cargo es único. Si intentas crear uno que ya existe, Django
rechaza el duplicado. Tampoco se puede eliminar un cargo mientras esté asignado
a uno o más empleados; primero hay que reasignar esos empleados a otro cargo.

### Qué puedes hacer en cada listado

**Cargos**

- Consultar los nombres de cargo y la cantidad de empleados asociados.
- Buscar por nombre.
- Crear y editar los cargos disponibles.
- Eliminar cargos que no estén asociados a empleados.

**Empleados**

- Consultar RUT, nombre, cargo, salario, estado activo e ingreso.
- Buscar por RUT, nombre, cargo o correo electrónico.
- Filtrar por cargo y estado activo.
- Crear, editar y eliminar fichas de empleado.
- Ver las fechas de ingreso y creación, que no se pueden editar.

El RUT es único. El listado muestra hasta 25 registros por página.

## Ejemplo: buscar y actualizar un empleado

Supongamos que se registró a `Ana Ejemplo` con el cargo `Analista de RRHH`:

1. Abre **Empleados** y busca su nombre o RUT.
2. Selecciona la ficha encontrada.
3. Cambia su salario o el cargo mediante el selector de cargos.
4. Guarda los cambios.

Si Ana deja de trabajar en la empresa, desactiva **Activo** en lugar de borrar
la ficha si se necesita conservar su historial. El borrado es permanente y
depende de los permisos de la cuenta.

## Vehículos de Automotora

En **Vehículos** puedes consultar, buscar por patente/marca/modelo, filtrar por
marca/combustible/año y crear, editar o eliminar registros. El formulario
organiza los datos del vehículo y los de registro. El ID y la fecha de registro
son de solo lectura, la patente debe ser única y se muestran 25 registros por
página.

## Usuarios y permisos

Para iniciar sesión en el admin, una cuenta debe tener acceso al panel
(`is_staff` activo). Un superusuario tiene todos los permisos. A otras cuentas
se les pueden asignar permisos desde **Autenticación y autorización**.

Por ejemplo, quien solo consulta fichas de RRHH necesita permisos de
visualización para Empleado y Cargo, no de edición o borrado. Quien administra
la plantilla puede necesitar permisos para añadir y cambiar Empleado y Cargo.
Limita los permisos de borrado a quienes los requieran. Para administrar un
modelo relacionado también deben concederse los permisos del modelo
correspondiente.

El admin es distinto de las páginas de consulta de cada aplicación. Los
empleados también se muestran en <http://127.0.0.1:8000/rrhh/> y el inventario
de vehículos en <http://127.0.0.1:8000/automotora/>.
