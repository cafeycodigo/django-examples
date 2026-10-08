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

El comando usa Faker en español de Chile y genera 20 empleados con RUT, nombre,
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
- En ejecuciones posteriores no duplica esos 20 empleados ni los cargos
  generados.
- Actualiza los campos de los empleados correspondientes a esos RUT con los
  valores de prueba del seeder. No lo uses para refrescar datos de prueba que
  quieras conservar.

El resultado informa cuántos empleados se crearon, cuántos se actualizaron y
cuántos cargos nuevos se añadieron. Por ejemplo:

```text
Seeder finalizado: 20 empleados creados, 0 actualizados y 14 cargos creados.
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
