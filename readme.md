# Sistema

Proyecto académico desarrollado con Django para trabajar ejercicios de bases de
datos. El repositorio contiene aplicaciones y módulos de distintos ejercicios;
la configuración actual del proyecto está en `sistema/`.

## Contenido

Ejercicios del bloque 21–30 incluidos en el proyecto:

| Ejercicio | Aplicación |
| --- | --- |
| 21 | `ecommerce` |
| 24 | `seguridad_rbac` |
| 25 | `hospital` |
| 27 | `streaming` |
| 28 | `biblioteca` |

También se incluyen los módulos `automotora_basica`, `core` y `rrhh`. Consulta
`sistema/settings.py` para ver cuáles están activados en la configuración actual.

## Requisitos

- Python
- Django y dependencias indicadas en `requirements.txt`

## Instalación en Windows



```cmd
git clone https://github.com/cafeycodigo/django-examples.git sistema
```

Descarga o extrae el proyecto en una carpeta llamada `sistema`. Abre PowerShell
en esa carpeta —donde se encuentra `manage.py`— y ejecuta:

```cmd
cd sistema

py -m venv venv

.\venv\Scripts\Activate

(env) pip install -r requirements.txt

```

Luego de instalar las dependencias, crea las tablas de la base de datos:

```powershell

python manage.py makemigrations
python manage.py migrate
```

Para cargar los 20 empleados de prueba:

```powershell
python manage.py seed_empleado
```

El seeder se puede volver a ejecutar sin duplicar empleados.

Los empleados cargados se pueden consultar en el índice de RRHH:
<http://127.0.0.1:8000/rrhh/>.

## Inventario de automotora

La página de Automotora permite buscar, registrar, editar y eliminar vehículos
en <http://127.0.0.1:8000/automotora/>. Requiere iniciar sesión con una cuenta
de personal (`is_staff`); se puede ingresar desde el inicio de sesión del
administrador en `/admin/`.

## Dependencias

Las dependencias del proyecto están declaradas en `requirements.txt`. Si se
agregan o actualizan paquetes, activa el entorno virtual y actualiza el archivo,
por ejemplo:

```powershell
python -m pip freeze > requirements.txt
```

## Referencia

Material de los ejercicios: <https://cafeycodigo.org/challenges/database/>
