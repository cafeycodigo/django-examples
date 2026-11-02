# Modelo Django de ConectaVecinos

La aplicación utiliza `settings.AUTH_USER_MODEL` para las cuentas existentes.
No es necesario cambiar el usuario del proyecto ni crear contraseñas propias.

## Entidades

- Territorio: Municipalidad, Comunidad y UsuarioComunidad (membresía única).
- Roles territoriales: Rol y UsuarioRol, con ámbito municipal o comunitario.
- Catálogos: Categoria, Prioridad y EstadoIncidencia.
- Solicitudes: Incidencia, con tipo, código único, ubicación, visibilidad y duplicados.
- Gestión: UnidadMunicipal, Asignacion, Seguimiento y Decision.
- Participación: Evidencia, Comentario, Apoyo y Evaluacion.
- Comunicación: Notificacion, con fecha de lectura.

Las referencias de gestión usan PROTECT para impedir borrados accidentales del
historial. Los apoyos y evaluaciones son únicos por usuario e incidencia.
Las coordenadas se guardan juntas y tienen límites geográficos; las evaluaciones
aceptan puntuaciones de 1 a 5. Las incidencias y evidencias son privadas inicialmente.

## Instalación y administración

```powershell
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py createsuperuser
.\venv\Scripts\python.exe manage.py runserver
```

En `/admin/`, crear primero municipalidades, comunidades y los catálogos de
categorías, prioridades y estados. Un nivel mayor de prioridad representa mayor
gravedad. Los estados tienen un código estable (por ejemplo `recibida`, `resuelta`,
`cerrada`, `rechazada`) y el indicador `es_final` determina el cierre del caso.
Los catálogos quedan configurables y no se cargan datos ficticios automáticamente.

## Cambios de estado

```python
from conectavecinos.models import Incidencia, EstadoIncidencia

incidencia = Incidencia.objects.get(codigo=codigo)
estado = EstadoIncidencia.objects.get(codigo="resuelta")
incidencia.cambiar_estado(estado, responsable=usuario, observacion="Luminarias reparadas")
```

Este método bloquea el registro durante la transacción y guarda el estado,
la fecha de cierre, el seguimiento y una notificación interna. Un cambio a un
estado no final limpia la fecha de cierre para permitir la reapertura.
El administrador también utiliza este método al modificar el estado.
El historial de seguimiento es de solo lectura en el administrador.
No usar `QuerySet.update()` ni asignar el estado con `save()` para este flujo:
esas operaciones omiten el historial. La creación inicial no genera un cambio
de estado; su fecha y autor quedan registrados en la incidencia.

## Validación y alcance

Los ModelForms y el administrador ejecutan la validación del modelo. Si se usa
el ORM directamente, llamar a `full_clean()` antes de guardar asignaciones,
roles, evaluaciones o duplicados para validar sus relaciones. Django no ejecuta
`full_clean()` automáticamente en `save()`.

Los roles territoriales almacenan permisos, pero aún no hay un backend de
autorización territorial: no sustituyen los permisos del administrador de Django.
La política de transiciones autorizadas entre estados queda pendiente de definir.
Las notificaciones son registros internos; no se envían correos.
Los archivos usan el almacenamiento de Django y no se exponen mediante rutas
públicas aquí; su descarga con autorización y configuración de almacenamiento
privado corresponde a la futura capa de aplicación.
La vista `/vecinos/` solo devuelve la identificación del proyecto, sin datos ciudadanos.

## Verificación

```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py test conectavecinos
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

Las pruebas cubren códigos, privacidad inicial, historial y reapertura,
notificaciones, motivos obligatorios, apoyos únicos, coordenadas, ciclos de
duplicados, consistencia territorial y evaluaciones de casos finalizados.
