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

Descarga o extrae el proyecto en una carpeta llamada `sistema`. Abre PowerShell
en esa carpeta —donde se encuentra `manage.py`— y ejecuta:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
```

Para crear un usuario administrador:

```powershell
python manage.py createsuperuser
```

## Ejecución

Inicia el servidor de desarrollo con:

```powershell
python manage.py runserver
```

Por defecto, Django sirve el proyecto en <http://127.0.0.1:8000/>.

> **Nota:** la configuración de rutas del proyecto aún requiere revisión para
> iniciar correctamente. En `sistema/urls.py` se referencia `core.urls`, pero
> ese archivo no está presente actualmente.

## Base de datos

El proyecto usa SQLite. El comando `migrate` crea o actualiza la base local
`db.sqlite3`; los datos de esa base no forman parte de la entrega.

## Dependencias

Las dependencias del proyecto están declaradas en `requirements.txt`. Si se
agregan o actualizan paquetes, activa el entorno virtual y actualiza el archivo,
por ejemplo:

```powershell
python -m pip freeze > requirements.txt
```

## Referencia

Material de los ejercicios: <https://cafeycodigo.org/challenges/database/>
