# Modelo de base de datos — ConectaVecinos

Para ConectaVecinos recomiendo utilizar una base de datos relacional en PostgreSQL, diseñada para administrar múltiples municipalidades, villas, poblaciones, condominios y barrios.

El modelo debe permitir que un vecino publique una incidencia, que un Gestor Comunitario la revise, que un concejal pueda realizar seguimiento y que la unidad municipal correspondiente gestione su resolución.

Además, debe conservar el historial completo de cada solicitud y permitir que cualquier ciudadano consulte la información pública.

## 1. Módulos de la base de datos

Propongo organizar el modelo en seis módulos:

| Módulo                   | Tablas principales                                            | Objetivo                                      |
| ------------------------ | ------------------------------------------------------------- | --------------------------------------------- |
| Usuarios y permisos      | Usuario, Rol, UsuarioRol                                      | Gestionar identidades y permisos.             |
| Organización territorial | Municipalidad, Comunidad, UsuarioComunidad                    | Identificar dónde viven los vecinos.          |
| Incidencias              | Incidencia, Categoria, Prioridad, EstadoIncidencia, Evidencia | Registrar y clasificar problemas.             |
| Gestión municipal        | UnidadMunicipal, Asignacion, Seguimiento, Decision            | Gestionar responsables, avances y decisiones. |
| Participación ciudadana  | Comentario, Apoyo, Evaluacion                                 | Permitir interacción comunitaria.             |
| Comunicación             | Notificacion                                                  | Informar sobre cambios y respuestas.          |

La tabla central será Incidencia, porque conecta al vecino, su comunidad, el problema reportado y todo el proceso de gestión.

## 2. Diagrama entidad-relación simplificado

Vista conceptual resumida. Las relaciones completas incluyen las tablas de roles, evidencias, decisiones, apoyos y notificaciones.

## 3. Tabla principal: Incidencia

| Campo                | Tipo de dato | Descripción                           |
| -------------------- | ------------ | ------------------------------------- |
| id                   | BIGINT, PK   | Identificador interno.                |
| codigo               | VARCHAR(40)  | Código público único.                 |
| autor_id             | BIGINT, FK   | Vecino que publica.                   |
| comunidad_id         | BIGINT, FK   | Comunidad afectada.                   |
| categoria_id         | BIGINT, FK   | Categoría temática.                   |
| prioridad_id         | BIGINT, FK   | Nivel de gravedad.                    |
| estado_id            | BIGINT, FK   | Estado actual.                        |
| titulo               | VARCHAR(200) | Nombre del problema.                  |
| descripcion          | TEXT         | Descripción detallada.                |
| ubicacion_referencia | VARCHAR(250) | Lugar del problema.                   |
| latitud, longitud    | NUMERIC      | Coordenadas geográficas.              |
| visibilidad          | VARCHAR(20)  | Pública o restringida.                |
| creada_en            | TIMESTAMPTZ  | Fecha de publicación.                 |
| cerrada_en           | TIMESTAMPTZ  | Fecha de cierre, si existe.           |
| duplicada_de_id      | BIGINT, FK   | Incidencia original, si es duplicada. |

## 4. Relaciones más importantes

- Una municipalidad tiene muchas comunidades.
- Una comunidad tiene muchas incidencias.
- Un usuario puede publicar muchas incidencias.
- Una incidencia pertenece a una categoría, prioridad y estado actual.
- Una incidencia puede tener múltiples asignaciones, seguimientos, evidencias, comentarios y apoyos.
- Un usuario puede tener distintos roles según la municipalidad o comunidad.
- Cada cambio importante de estado debe generar un registro de seguimiento.

Una decisión de diseño importante: no guardar directamente el concejal y el alcalde como campos obligatorios dentro de `Incidencia`. Es preferible utilizar `Asignacion`, `Seguimiento` y `Decision`, porque no todos los casos requieren la intervención de las mismas autoridades.

## 5. Archivo SQL inicial

Preparé un script de PostgreSQL con las 17 tablas, claves primarias, claves foráneas, restricciones e índices iniciales.

conectavecinos_modelo.sql

Modelo relacional inicial · PostgreSQL

Descargar script SQL

Este modelo es una base de partida. Antes de producción habría que completar las reglas de transición de estados, permisos por organización, publicación segura de evidencias y auditoría de decisiones. Si lo implementas en Django, conviene usar su modelo de usuario y sistema de autenticación en lugar de crear manualmente contraseñas.

Mi recomendación es desarrollar primero Usuario, Comunidad, Categoría, Prioridad, EstadoIncidencia, Incidencia y Seguimiento. Con estas entidades ya puedes construir el primer flujo funcional de ConectaVecinos.