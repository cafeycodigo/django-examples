# Guía de migraciones de Django

Esta guía explica cómo mantener sincronizados los modelos del proyecto y la
base de datos SQLite. Ejecuta los comandos desde la carpeta del proyecto donde
está `manage.py`.

## ¿Qué es una migración?

Una migración es un archivo que describe un cambio en la estructura de la base
de datos, por ejemplo crear una tabla, agregar una columna o establecer una
relación entre dos modelos. Django genera o aplica estos archivos según el
comando utilizado.

Las migraciones están versionadas junto al código:

- `automotora_basica/migrations/`: crea la tabla `Vehiculo`.
- `rrhh/migrations/`: crea las tablas `Empleado` y `Cargo`, y registra la
  relación entre ellas.

Los archivos de migración deben compartirse con el equipo. La base local
(`db.sqlite3`) no los reemplaza.

## Flujo habitual al cambiar un modelo

1. Edita el modelo correspondiente, por ejemplo
   [`rrhh/models.py`](./rrhh/models.py).
2. Genera una migración para la aplicación modificada:

   ```powershell
   python manage.py makemigrations rrhh
   ```

   Para que Django revise todas las aplicaciones:

   ```powershell
   python manage.py makemigrations
   ```

3. Revisa el archivo nuevo en `rrhh/migrations/`. Confirma que las operaciones
   representan el cambio esperado.
4. Aplica las migraciones pendientes:

   ```powershell
   python manage.py migrate
   ```

5. Comprueba cuáles se aplicaron:

   ```powershell
   python manage.py showmigrations rrhh
   ```

`makemigrations` crea archivos; `migrate` ejecuta los cambios en la base de
datos. Ejecutar uno no reemplaza al otro.

## Ejemplo RRHH: convertir el cargo en una relación

Antes, `Empleado.cargo` era texto. Eso permitía diferencias como `Analista`,
`analista` o `Analista `, aunque se tratara del mismo cargo. Ahora `Cargo` es un
modelo independiente y cada empleado tiene una clave foránea:

```python
class Cargo(models.Model):
    nombre = models.CharField(max_length=50, unique=True)


class Empleado(models.Model):
    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.PROTECT,
        related_name="empleados",
    )
```

La migración
[`rrhh/migrations/0002_cargo_empleado.py`](./rrhh/migrations/0002_cargo_empleado.py)
no descarta el texto anterior. Crea la tabla de cargos, genera un registro por
cada nombre de cargo existente, convierte el valor de cada empleado a la clave
de ese registro y cambia el campo a una clave foránea. `PROTECT` evita borrar
un cargo que todavía tenga empleados asociados.

Para actualizar una base que ya aplicó `rrhh.0001_initial`, ejecuta:

```powershell
python manage.py migrate rrhh
python manage.py showmigrations rrhh
```

La lista debería mostrar `[X]` tanto en `0001_initial` como en
`0002_cargo_empleado`. En la migración de RRHH el esquema queda así:

```text
Cargo
  id
  nombre (único)

Empleado
  ...
  cargo_id -> Cargo.id
```

También se puede revertir la relación a la migración inicial:

```powershell
python manage.py migrate rrhh 0001
```

La migración inversa vuelve a guardar en el campo de texto el nombre del cargo.
Para regresar al esquema más nuevo:

```powershell
python manage.py migrate rrhh
```

No reviertas migraciones en una base compartida o de producción sin copia de
seguridad y autorización: cada migración puede modificar o eliminar datos.

## Revisar el SQL y el estado

Para inspeccionar el SQL de la migración de relación:

```powershell
python manage.py sqlmigrate rrhh 0002
```

El número corresponde al prefijo del archivo de migración. El traspaso de los
nombres existentes a `Cargo` es una operación de datos de Django y no siempre
se representa como SQL en esta salida.

`showmigrations` muestra `[X]` junto a las migraciones aplicadas y `[ ]` junto
a las pendientes.

## Primera instalación

Las migraciones del proyecto ya están incluidas. En una base nueva, crea las
tablas con:

```powershell
python manage.py migrate
```

No es necesario ejecutar `makemigrations` si no cambiaste los modelos.

## Migraciones y datos de prueba

Los seeders agregan registros de ejemplo; no cambian la estructura de las
tablas ni sustituyen las migraciones. Para ejecutarlos después de migrar:

```powershell
python manage.py seed_empleado
python manage.py seed_vehiculos
```

Consulta [README_SEEDER.md](./README_SEEDER.md) para ver los datos creados y el
comportamiento al volver a ejecutar cada comando.

## Buenas prácticas

- Genera una migración cada vez que cambies un modelo.
- Conserva y comparte los archivos generados.
- No edites ni borres una migración que ya se aplicó en otros entornos; crea
  otra que haga el cambio correctivo.
- Antes de migrar una base con información importante, respáldala y revisa las
  operaciones.
- En producción, planifica y respalda la base antes de aplicar migraciones.
- No uses `migrate <aplicación> zero` para resolver problemas en una base con
  información importante: revierte todas las migraciones de esa aplicación y
  puede eliminar sus tablas.
