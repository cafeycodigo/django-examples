# Educación Superior (`educacion`)

Ejemplo de gestión académica con datos de demostración ficticios, inspirado en
la educación técnico-profesional chilena. Los nombres de instituciones y los
registros generados no representan datos oficiales ni implican afiliación con
Duoc UC, INACAP u otra institución.

## Modelo de datos

- **Institución y sede:** organización y campus.
- **Carrera:** programa técnico o profesional en una sede, con área, título,
  duración y modalidad.
- **Docente:** identificación, especialidad y sede.
- **Alumno:** datos de contacto, cohorte y carrera vigente.
- **Asignatura:** catálogo común de materias.
- **Detalle de asignatura:** asignatura impartida en una carrera, periodo,
  semestre y sección, a cargo de un docente.
- **Nota:** evaluación de un alumno en un detalle de asignatura, en escala de
  1,0 a 7,0.

Incluye carreras de informática, programación, ciberseguridad, redes,
enfermería, electricidad, automatización, administración y construcción.

## Instalación y datos de prueba

Desde la carpeta del proyecto:

```powershell
python manage.py migrate
python manage.py seed_educacion
```

El comando crea o completa **4.500 alumnos como mínimo**, junto con
instituciones, sedes, carreras, docentes, asignaturas, secciones y notas.
Puede repetirse sin duplicar esos registros. Para una muestra pequeña:

```powershell
python manage.py seed_educacion --cantidad 100 --seed 10
```

La cantidad es un mínimo y el comando no elimina datos existentes. Los datos
se generan con Faker y se guardan en la base de datos configurada para Django.

## Consultas

- Panel JSON: `/educacion/`
- Alumnos: `/educacion/alumnos/?limite=50`
- Carreras: `/educacion/carreras/`
- Asignaturas: `/educacion/asignaturas/`
- Notas: `/educacion/notas/?limite=50`

Las listas aceptan un parámetro `limite` entre 1 y 100. El panel de Django
Admin permite consultar y editar las entidades.
