# Sistema

Proyecto académico desarrollado con Django para aprender y practicar ejercicios
de bases de datos. El proyecto reúne varias aplicaciones; solo algunas están
activadas en la configuración actual de `sistema/settings.py`.

## Ruta de aprendizaje

Sigue las guías en este orden para entender cómo se construye y utiliza el
proyecto:

1. **Instalar y ejecutar:** prepara el entorno, aplica las migraciones, carga
   datos de ejemplo y levanta el servidor con las instrucciones de esta página.
2. **Entender las migraciones:** [README_MIGRACIONES.md](./README_MIGRACIONES.md)
   explica cómo los cambios en los modelos se reflejan en la base de datos.
3. **Poblar datos de prueba:** [README_SEEDER.md](./README_SEEDER.md) explica
   los comandos existentes y presenta una propuesta de catálogo de biblioteca
   con Faker.
4. **Administrar registros:** [README_ADMIN.md](./README_ADMIN.md) explica el
   panel Django y cómo configurarlo con código.

## Aplicaciones y ejercicios

El proyecto contiene estos ejercicios del bloque 21–30:

| Ejercicio | Aplicación |
| --- | --- |
| 21 | `ecommerce` |
| 24 | `seguridad_rbac` |
| 25 | `hospital` |
| 27 | `streaming` |
| 28 | `biblioteca` |

También contiene `automotora_basica`, `core` y `rrhh`. La lista de aplicaciones
activas puede consultarse en [`sistema/settings.py`](./sistema/settings.py).
Que una aplicación exista en el código no significa necesariamente que esté
activada o disponible en el sitio.

## Requisitos

- Python
- Django y Faker, instalados desde `requirements.txt`

## Instalación y primer inicio en Windows

Abre PowerShell en la carpeta del proyecto donde está `manage.py`. Si todavía
no tienes el proyecto, clónalo y entra en su carpeta:

```powershell
git clone https://github.com/cafeycodigo/django-examples.git sistema
cd sistema
```

Crea y activa un entorno virtual e instala las dependencias:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

En una instalación nueva, crea las tablas aplicando las migraciones incluidas:

```powershell
python manage.py migrate
```

El comando `makemigrations` se necesita cuando se cambian los modelos; no es
parte obligatoria de la instalación inicial. Consulta
[README_MIGRACIONES.md](./README_MIGRACIONES.md) para aprender el flujo completo.

Genera los empleados de prueba con el comando disponible:

```powershell
python manage.py seed_empleado
```

Este comando crea o actualiza 120 empleados y sus cargos. Consulta
[README_SEEDER.md](./README_SEEDER.md) para conocer los datos que genera, qué
ocurre al repetirlo y cómo se propone poblar una biblioteca con Faker.

Inicia el servidor:

```powershell
python manage.py runserver
```

- RRHH: <http://127.0.0.1:8000/rrhh/>
- Automotora: <http://127.0.0.1:8000/automotora/>
- Administración: <http://127.0.0.1:8000/admin/>

Para ingresar al admin, crea una cuenta de administración si aún no tienes una:

```powershell
python manage.py createsuperuser
```

Luego abre `/admin/` e inicia sesión. La guía
[README_ADMIN.md](./README_ADMIN.md) explica permisos y personalización.

## Material de referencia

Las dependencias están declaradas en [`requirements.txt`](./requirements.txt).
Material complementario de los ejercicios:
<https://cafeycodigo.org/challenges/database/>.
