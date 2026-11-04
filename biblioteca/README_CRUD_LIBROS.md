# CRUD de libros de la biblioteca

Este documento describe el CRUD web para administrar títulos bibliográficos en
la aplicación Django `biblioteca`. El código se incorporó en las vistas, rutas,
plantillas y pruebas de la app.

## Alcance

El CRUD administra registros del modelo `Libro`: título, autor, ISBN, editorial
y año de publicación. Un título bibliográfico no es lo mismo que una copia
física: los ejemplares pertenecen al modelo `Ejemplar` y se relacionan con un
libro. La página de detalle muestra los ejemplares asociados, pero no los crea
ni los modifica.

## Rutas

Las rutas de libros tienen nombres propios y no reutilizan los nombres del CRUD
de usuarios.

| Operación | URL | Nombre de ruta |
|---|---|---|
| Listar títulos | `/biblioteca/libros/` | `libro_listar` |
| Crear título | `/biblioteca/libros/crear/` | `libro_crear` |
| Ver título y ejemplares | `/biblioteca/libros/<id>/` | `libro_detalle` |
| Editar título | `/biblioteca/libros/<id>/editar/` | `libro_actualizar` |
| Eliminar título | `/biblioteca/libros/<id>/eliminar/` | `libro_eliminar` |

El catálogo también está enlazado desde el panel principal de la biblioteca.

## Cómo funciona

1. **Listar:** obtiene los libros ordenados alfabéticamente y ofrece enlaces
   para ver, editar o eliminar cada título.
2. **Crear:** muestra los campos del modelo y, al recibir un POST, toma cada
   valor directamente de `request.POST`.
3. **Ver detalle:** presenta los datos bibliográficos y los ejemplares físicos
   asociados, incluyendo código de barras, estado, ubicación y fecha de
   adquisición.
4. **Editar:** carga los valores actuales en el formulario. Los cambios se
   validan antes de guardar y, si hay errores, se conservan los datos enviados.
5. **Eliminar:** solicita confirmación y procesa la eliminación solo mediante
   POST.

## Captura y validación de datos

La implementación **no usa `LibroForm`, `forms.py` ni `ModelForm`**. La función
`_validar_libro` prepara los valores recibidos y llama a `Libro.full_clean()`
antes de guardar. Esto aplica las reglas declaradas en el modelo, entre ellas:

- El título es obligatorio.
- Se respetan las longitudes máximas de los campos.
- El ISBN, si se informa, debe ser único.
- El año de publicación, si se informa, debe ser un entero.
- Los campos opcionales vacíos se guardan como `NULL`.

Los errores de validación se muestran en la página y se mantienen los valores
que el usuario había enviado para que pueda corregirlos.

## Protección de ejemplares

No se permite eliminar un libro que todavía tenga ejemplares relacionados. La
vista comprueba si existen antes de borrar y muestra un mensaje indicando que
primero se deben eliminar o reasignar esos ejemplares. Esto protege el
inventario físico y evita perder la relación con el título.

## Archivos relacionados

- `urls.py`: declara las cinco rutas del CRUD.
- `views.py`: implementa el listado, detalle, creación, edición, eliminación y
  validación de datos.
- `templates/biblioteca/libro_list.html`: catálogo de títulos.
- `templates/biblioteca/libro_form.html`: formulario HTML de creación y edición.
- `templates/biblioteca/libro_detail.html`: ficha y tabla de ejemplares.
- `templates/biblioteca/libro_confirm_delete.html`: confirmación de borrado.
- `templates/biblioteca/index.html`: enlace de acceso al catálogo.
- `tests.py`: pruebas de rutas, operaciones y reglas de validación.

## Ejecutar y probar

Desde la raíz del proyecto, inicia el servidor:

```powershell
python manage.py runserver
```

Abre el catálogo en `http://127.0.0.1:8000/biblioteca/libros/`.

Para ejecutar las pruebas específicas del módulo:

```powershell
python manage.py test biblioteca
```

Las pruebas cubren el listado, el detalle con ejemplares, la creación, el
rechazo de ISBN duplicado, la validación del título obligatorio, la edición y
la protección al intentar eliminar un libro con ejemplares.
