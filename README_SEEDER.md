# Guía de seeders

Un seeder es un comando que carga datos de ejemplo para desarrollo y pruebas.
No reemplaza las migraciones: primero crea las tablas con `migrate` y después
ejecuta el seeder desde la carpeta donde está `manage.py`.

```powershell
python manage.py migrate
```

## Seed de empleados y cargos

Ejecuta:

```powershell
python manage.py seed_empleado
```

El comando usa Faker en español de Chile y genera 120 empleados con RUT, nombre,
cargo, salario, estado, correo electrónico y teléfono. Los cargos ahora son
registros del modelo `Cargo`: por cada nombre generado, el seeder lo busca o
crea y guarda la relación en `Empleado.cargo`.

Un empleado puede relacionarse con un cargo existente, por ejemplo:

```python
from rrhh.models import Cargo, Empleado

analista, _ = Cargo.objects.get_or_create(nombre="Analista de RRHH")
empleado = Empleado.objects.create(
    rut="12345678-5",
    nombre_completo="Ana Ejemplo",
    cargo=analista,
    salario=1250000,
)
```

Así varios empleados pueden compartir el mismo cargo, y el nombre del cargo se
mantiene en un único lugar.

### Volver a ejecutar el seeder de RRHH

`seed_empleado` está preparado para ejecutarse repetidamente:

- Busca cada empleado por su RUT y lo crea o actualiza.
- Busca cada cargo por su nombre y solo lo crea si todavía no existe.
- En ejecuciones posteriores no duplica esos 120 empleados ni los cargos
  generados.
- Actualiza los campos de los empleados correspondientes a esos RUT con los
  valores de prueba del seeder. No lo uses para refrescar datos de prueba que
  quieras conservar.

El resultado informa cuántos empleados se crearon, cuántos se actualizaron y
cuántos cargos nuevos se añadieron. Por ejemplo:

```text
Seeder finalizado: 120 empleados creados, 0 actualizados y 14 cargos creados.
```

La cantidad de cargos depende de los nombres que Faker genere en la ejecución.
En la ejecución siguiente, si ya existen los datos del seeder, aparecerán como
empleados actualizados y no debería añadir cargos duplicados.

## Seed de vehículos

Para generar vehículos de prueba de `automotora_basica`:

```powershell
python manage.py seed_vehiculos
```

Este comando crea 20 vehículos con patente, marca, modelo, año, kilometraje,
combustible, color y capacidad de pasajeros. A diferencia del seeder de RRHH,
el comando de vehículos usa `create()` y no comprueba si ya existe un vehículo
equivalente. Ejecútalo una sola vez en una base vacía o de pruebas: repetirlo
puede producir registros adicionales o un error si se genera una patente que
ya existe.

## Propuesta: generar datos masivos para una biblioteca con Faker

Faker ya está incluido en `requirements.txt`. Permite crear nombres, correos,
fechas y otros valores sintéticos de forma rápida y reproducible; para los
valores propios del negocio, como las categorías y los estados de préstamo, es
mejor usar listas definidas por el proyecto. Así se genera un conjunto grande
de datos de prueba sin ingresar cada registro a mano.

### Estado actual y alcance de la propuesta

La app `biblioteca` ya tiene modelos `Libro`, `Ejemplar`, `Prestamo` y `Multa`,
pero todavía no está incluida en `INSTALLED_APPS`, no registra esos modelos en
`biblioteca/admin.py` y no cuenta con un comando seeder. Tampoco tiene modelos
`Categoria` ni `Usuario`: hoy el préstamo guarda el RUT como texto en
`Prestamo.rut_usuario`. Por eso, el ejemplo siguiente es una propuesta que
requiere adaptar los modelos y habilitar la app antes de poder ejecutarse; no
es un comando que ya exista.

### Modelo de datos propuesto

Se pueden añadir `Categoria` y `Usuario`, asociar cada libro a una categoría y
reemplazar el RUT de texto del préstamo por una relación al usuario. En forma
resumida, los campos nuevos o modificados serían:

```python
# biblioteca/models.py
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.nombre


# Añadir a Libro:
categoria = models.ForeignKey(
    Categoria,
    on_delete=models.PROTECT,
    related_name="libros",
)

# En Prestamo, sustituir rut_usuario (CharField) por:
usuario = models.ForeignKey(
    Usuario,
    on_delete=models.PROTECT,
    related_name="prestamos",
)
```

El modelo actual `Libro` ya contiene título, autor, ISBN, editorial y año de
publicación; `Ejemplar` representa cada copia física, y `Prestamo` se relaciona
con un ejemplar. Separar `Libro` de `Ejemplar` permite tener, por ejemplo,
varias copias del mismo título. `PROTECT` conserva la integridad: Django no
dejará eliminar una categoría, usuario o ejemplar que siga relacionado.

Al cambiar `rut_usuario` por una clave foránea hay que planificar la migración:
si ya existen préstamos, primero se deben crear usuarios y asociarles esos
préstamos. No se debe borrar la columna ni sus datos sin una migración de datos
o una estrategia de respaldo.

### Flujo para preparar la app y las tablas

1. Añade `'biblioteca'` a `INSTALLED_APPS` en `sistema/settings.py`.
2. Define los modelos y campos propuestos, adaptándolos a los modelos actuales.
3. Genera y revisa la migración:

   ```powershell
   python manage.py makemigrations biblioteca
   python manage.py showmigrations biblioteca
   ```

4. Aplica la migración a la base de datos:

   ```powershell
   python manage.py migrate
   ```

Las migraciones crean o modifican tablas; no generan datos de ejemplo. El
seeder se ejecuta después de aplicar las migraciones.

### Ejemplo de generación con Faker

Este es el núcleo ilustrativo de un comando llamado
`biblioteca/management/commands/seed_biblioteca.py`. Supone que ya existen los
modelos propuestos y que `Prestamo.usuario` es una relación a `Usuario`. En una
versión completa, este código iría dentro de `handle()` de un comando Django.

```python
from datetime import timedelta

from faker import Faker

from biblioteca.models import Categoria, Ejemplar, Libro, Prestamo, Usuario


fake = Faker("es_CL")
fake.seed_instance(42)  # Misma secuencia de valores de prueba en cada ejecución.

nombres_categorias = [
    "Ciencia ficción",
    "Historia",
    "Infantil",
    "Misterio",
    "Tecnología",
]
categorias = [
    Categoria.objects.get_or_create(nombre=nombre)[0]
    for nombre in nombres_categorias
]

usuarios = []
for _ in range(100):
    rut = fake.unique.numerify(text="########-#")
    usuario, _ = Usuario.objects.get_or_create(
        rut=rut,
        defaults={
            "nombre": fake.name()[:100],
            "email": fake.unique.safe_email(),
        },
    )
    usuarios.append(usuario)

libros = []
for _ in range(300):
    isbn = fake.unique.numerify(text="978##########")
    libro, _ = Libro.objects.get_or_create(
        isbn=isbn,
        defaults={
            "titulo": fake.sentence(nb_words=4)[:120],
            "autor": fake.name()[:100],
            "editorial": fake.company()[:60],
            "anio_publicacion": fake.random_int(min=1950, max=2025),
            "categoria": fake.random_element(elements=categorias),
        },
    )
    libros.append(libro)

ejemplares = []
for numero in range(500):
    ejemplar, _ = Ejemplar.objects.get_or_create(
        codigo_barra=f"DEMO-{numero + 1:06d}",
        defaults={
            "id_libro": fake.random_element(elements=libros),
            "estado": "DISPONIBLE",
            "fecha_adquisicion": fake.date_between(
                start_date="-5y",
                end_date="today",
            ),
            "ubicacion": f"Estante {fake.random_int(min=1, max=20)}",
        },
    )
    ejemplares.append(ejemplar)

# Cada préstamo usa un ejemplar distinto en esta muestra.
for numero, ejemplar in enumerate(ejemplares[:400]):
    fecha = fake.date_between(start_date="-2y", end_date="-60d")
    fecha_pactada = fecha + timedelta(days=14)
    fecha_real = (
        fecha_pactada + timedelta(days=fake.random_int(min=1, max=15))
        if numero % 3 == 0
        else None
    )
    Prestamo.objects.get_or_create(
        id_ejemplar=ejemplar,
        usuario=fake.random_element(elements=usuarios),
        fecha_prestamo=fecha,
        defaults={
            "fecha_devolucion_pactada": fecha_pactada,
            "fecha_devolucion_real": fecha_real,
            "estado": "DEVUELTO" if fecha_real else "ACTIVO",
        },
    )
```

En esta muestra se crean cinco categorías, 100 usuarios, 300 títulos, hasta
500 ejemplares y hasta 400 préstamos. Los números son ejemplos: un comando
real debería aceptarlos como opciones, por ejemplo `--usuarios 1000` y
`--libros 5000`, y validar que sean positivos. Faker genera los datos variados;
los bucles determinan cuántos registros se intentan crear, y las claves
foráneas asignan cada ejemplar, libro y préstamo a registros relacionados.

`get_or_create()` ayuda a que las categorías, usuarios, libros y ejemplares
identificados por una clave estable no se dupliquen al repetir el comando. En
los préstamos, el ejemplo busca por ejemplar, usuario y fecha. Para entornos
con ejecuciones simultáneas o reglas de unicidad estrictas, también conviene
definir restricciones apropiadas en los modelos y envolver la carga en una
transacción (`transaction.atomic`). Para cargar cientos de miles de filas se
pueden crear lotes con `bulk_create()`, midiendo antes su comportamiento con
las relaciones y la base de datos usadas por el proyecto.

El RUT y el ISBN de este ejemplo son valores sintéticos con formato plausible,
no necesariamente válidos según sus algoritmos oficiales. Úsalos solo en
desarrollo y pruebas; nunca cargues datos personales reales en un seeder.
También revisa las reglas del dominio: este ejemplo permite que un ejemplar
tenga préstamos históricos y evita repetir el préstamo exacto, pero un sistema
real debería impedir dos préstamos activos simultáneos del mismo ejemplar.

Por último, crear las tablas y los datos no hace que aparezcan en el admin. Hay
que registrar `Categoria`, `Libro`, `Ejemplar`, `Prestamo` y `Usuario` en
`biblioteca/admin.py` y conceder permisos a la cuenta que los administrará.

## Consultar los datos generados

- Empleados: <http://127.0.0.1:8000/rrhh/>.
- Vehículos: <http://127.0.0.1:8000/automotora/>.
- Los cargos y empleados también se administran desde `/admin/` con los
  permisos apropiados.

Consulta [README_ADMIN.md](./README_ADMIN.md) para ejemplos de administración.
Los comandos implementados están en
[`rrhh/management/commands/seed_empleado.py`](./rrhh/management/commands/seed_empleado.py)
y
[`automotora_basica/management/commands/seed_vehiculos.py`](./automotora_basica/management/commands/seed_vehiculos.py).
