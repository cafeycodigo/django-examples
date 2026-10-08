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
