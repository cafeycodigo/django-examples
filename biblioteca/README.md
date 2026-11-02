# Módulo de Biblioteca

Módulo Django para la gestión integral de libros, ejemplares físicos, préstamos, multas y usuarios con correo institucional vinculados al sistema de autenticación de Django (`User`).

---

## 📋 Requisitos Previos

- Python 3.10 o superior (con entorno virtual configurado en `venv/`).
- Dependencias del proyecto instaladas:
  ```powershell
  pip install -r requirements.txt
  ```
  *(Incluye Django, Faker, entre otros).*

---

## 🚀 Guía de Instalación y Configuración

### 1. Activar el Entorno Virtual

En PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

O en CMD:
```cmd
venv\Scripts\activate.bat
```

---

### 2. Verificar Configuración en `settings.py`

Asegúrate de que `'biblioteca'` esté en la lista `INSTALLED_APPS` en `sistema/settings.py`:

```python
INSTALLED_APPS = [
    ...
    'biblioteca',
]
```

---

### 3. Verificar Rutas en `urls.py`

Asegúrate de que las URLs de biblioteca estén enlazadas en `sistema/urls.py`:

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('biblioteca/', include('biblioteca.urls')),
    ...
]
```

---

### 4. Generar y Aplicar Migraciones

Aplica las migraciones correspondientes a la base de datos SQLite:

```powershell
python manage.py makemigrations biblioteca
python manage.py migrate
```

---

### 5. Poblar la Base de Datos con el Seeder

Ejecuta el seeder para generar registros de prueba (usuarios institucionales, libros, ejemplares, préstamos y multas con Faker):

```powershell
python manage.py seed_biblioteca
```

#### Opciones personalizadas del Seeder:
Puedes especificar las cantidades a generar con los siguientes parámetros:

```powershell
python manage.py seed_biblioteca --usuarios 100 --libros 120 --ejemplares 200 --prestamos 150
```

---

### 6. Iniciar el Servidor de Desarrollo

Levanta el servidor local de Django:

```powershell
python manage.py runserver
```

---

## 🌐 Enlaces y Vistas Disponibles

| Sección | URL | Descripción |
| :--- | :--- | :--- |
| **Panel Web Principal** | [http://127.0.0.1:8000/biblioteca/](http://127.0.0.1:8000/biblioteca/) | Dashboard responsivo con Bootstrap 5, tarjetas de métricas y tabla interactiva de préstamos con correo institucional. |
| **Administración Django** | [http://127.0.0.1:8000/admin/biblioteca/](http://127.0.0.1:8000/admin/biblioteca/) | Gestión de Libros, Ejemplares, Usuarios, Préstamos y Multas con filtros y búsquedas avanzadas. |

---

## 📦 Estructura del Módulo

```text
biblioteca/
├── admin.py                      # Registro en Django Admin con filtros y búsquedas
├── apps.py                       # Configuración de la App Biblioteca
├── models.py                     # Modelos Libro, Ejemplar, Usuario (con User), Prestamo, Multa
├── urls.py                       # Rutas internas de la app
├── views.py                      # Vistas y métricas para el dashboard
├── management/
│   └── commands/
│       └── seed_biblioteca.py    # Comando de generación masiva con Faker
├── migrations/                   # Historial de migraciones
└── templates/
    └── index.html                # Interfaz web responsiva con Bootstrap 5 y CDN
```

---

## 👤 Modelo de Usuario y Correo Institucional

Cada registro de usuario de biblioteca se vincula mediante `OneToOneField` al modelo de autenticación `auth.User`:
- **Usuario Django (`auth_user`)**: `username`, `first_name`, `last_name`, `email`.
- **Perfil de Biblioteca (`Usuario`)**:
  - `rut`: RUT chileno con dígito verificador.
  - `email_institucional`: Formato `nombre.apellido@universidad.cl`.
  - `carrera_o_departamento`: Carrera académica o departamento asignado.
  - `activo`: Estado de vigencia.
- **Préstamo (`Prestamo`)**:
  - Relacionado directamente con el usuario solicitante (`settings.AUTH_USER_MODEL`).
