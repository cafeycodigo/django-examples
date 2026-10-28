from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


class Institucion(models.Model):
    nombre = models.CharField(max_length=150, unique=True, verbose_name="Institución")
    sigla = models.CharField(max_length=20, unique=True, verbose_name="Sigla")
    tipo = models.CharField(max_length=60, default="Instituto profesional")

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Institución"
        verbose_name_plural = "Instituciones"

    def __str__(self):
        return f"{self.sigla} - {self.nombre}"


class Sede(models.Model):
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.CASCADE,
        related_name="sedes",
        verbose_name="Institución",
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la sede")
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad")

    class Meta:
        ordering = ["institucion", "ciudad", "nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["institucion", "nombre", "ciudad"],
                name="unique_sede_institucion_ciudad",
            )
        ]
        verbose_name = "Sede"
        verbose_name_plural = "Sedes"

    def __str__(self):
        return f"{self.nombre}, {self.ciudad} ({self.institucion.sigla})"


class Carrera(models.Model):
    AREA_CHOICES = [
        ("informatica", "Informática y tecnología"),
        ("salud", "Salud"),
        ("electricidad", "Electricidad y automatización"),
        ("administracion", "Administración y negocios"),
        ("construccion", "Construcción"),
    ]
    MODALIDAD_CHOICES = [
        ("presencial", "Presencial"),
        ("hibrida", "Híbrida"),
        ("online", "Online"),
    ]

    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")
    sede = models.ForeignKey(
        Sede,
        on_delete=models.PROTECT,
        related_name="carreras",
        verbose_name="Sede",
    )
    nombre = models.CharField(max_length=150, verbose_name="Nombre de la carrera")
    area = models.CharField(max_length=30, choices=AREA_CHOICES, db_index=True)
    titulo = models.CharField(max_length=150, verbose_name="Título que otorga")
    duracion_semestres = models.PositiveSmallIntegerField(default=5)
    modalidad = models.CharField(
        max_length=15,
        choices=MODALIDAD_CHOICES,
        default="presencial",
    )

    class Meta:
        ordering = ["nombre", "sede"]
        constraints = [
            models.UniqueConstraint(
                fields=["sede", "nombre"],
                name="unique_carrera_sede",
            )
        ]
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"

    def __str__(self):
        return f"{self.nombre} - {self.sede.ciudad}"


class Docente(models.Model):
    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT")
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")
    especialidad = models.CharField(max_length=120)
    sede = models.ForeignKey(
        Sede,
        on_delete=models.PROTECT,
        related_name="docentes",
        verbose_name="Sede",
    )

    class Meta:
        ordering = ["apellidos", "nombres"]
        verbose_name = "Docente"
        verbose_name_plural = "Docentes"

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


class Asignatura(models.Model):
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=120, unique=True, verbose_name="Asignatura")
    area = models.CharField(max_length=80, verbose_name="Área")
    creditos = models.PositiveSmallIntegerField(default=5)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Asignatura"
        verbose_name_plural = "Asignaturas"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Alumno(models.Model):
    ESTADO_CHOICES = [
        ("regular", "Regular"),
        ("egresado", "Egresado"),
        ("suspendido", "Suspendido"),
    ]

    rut = models.CharField(max_length=12, unique=True, db_index=True, verbose_name="RUT")
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")
    telefono = models.CharField(max_length=25, blank=True)
    comuna = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    carrera = models.ForeignKey(
        Carrera,
        on_delete=models.PROTECT,
        related_name="alumnos",
        verbose_name="Carrera",
    )
    cohorte = models.PositiveSmallIntegerField(verbose_name="Año de ingreso")
    semestre_actual = models.PositiveSmallIntegerField(default=1)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default="regular")

    class Meta:
        ordering = ["apellidos", "nombres"]
        verbose_name = "Alumno"
        verbose_name_plural = "Alumnos"

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.rut})"


class DetalleAsignatura(models.Model):
    MODALIDAD_CHOICES = Carrera.MODALIDAD_CHOICES

    carrera = models.ForeignKey(
        Carrera,
        on_delete=models.CASCADE,
        related_name="detalle_asignaturas",
        verbose_name="Carrera",
    )
    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.PROTECT,
        related_name="ofertas",
        verbose_name="Asignatura",
    )
    docente = models.ForeignKey(
        Docente,
        on_delete=models.PROTECT,
        related_name="asignaturas_dictadas",
        verbose_name="Docente",
    )
    periodo = models.PositiveSmallIntegerField(verbose_name="Año académico")
    semestre = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(2)],
    )
    seccion = models.CharField(max_length=10, default="A")
    modalidad = models.CharField(
        max_length=15,
        choices=MODALIDAD_CHOICES,
        default="presencial",
    )
    cupos = models.PositiveSmallIntegerField(default=40)

    class Meta:
        ordering = ["carrera", "semestre", "asignatura"]
        constraints = [
            models.UniqueConstraint(
                fields=["carrera", "asignatura", "periodo", "semestre", "seccion"],
                name="unique_detalle_asignatura_periodo",
            )
        ]
        verbose_name = "Detalle de asignatura"
        verbose_name_plural = "Detalles de asignaturas"

    def __str__(self):
        return (
            f"{self.asignatura.nombre} - {self.carrera.nombre} "
            f"(S{self.semestre}, {self.periodo}, sección {self.seccion})"
        )


class Nota(models.Model):
    EVALUACION_CHOICES = [
        ("control_1", "Control 1"),
        ("evaluacion_1", "Evaluación 1"),
        ("evaluacion_2", "Evaluación 2"),
    ]

    alumno = models.ForeignKey(
        Alumno,
        on_delete=models.CASCADE,
        related_name="notas",
        verbose_name="Alumno",
    )
    detalle_asignatura = models.ForeignKey(
        DetalleAsignatura,
        on_delete=models.CASCADE,
        related_name="notas",
        verbose_name="Detalle de asignatura",
    )
    evaluacion = models.CharField(max_length=20, choices=EVALUACION_CHOICES)
    valor = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("1.0")), MaxValueValidator(Decimal("7.0"))],
        verbose_name="Nota",
    )
    fecha = models.DateField(verbose_name="Fecha de evaluación")

    class Meta:
        ordering = ["alumno", "detalle_asignatura", "fecha"]
        constraints = [
            models.UniqueConstraint(
                fields=["alumno", "detalle_asignatura", "evaluacion"],
                name="unique_nota_por_evaluacion",
            ),
            models.CheckConstraint(
                condition=Q(valor__gte=Decimal("1.0"), valor__lte=Decimal("7.0")),
                name="nota_en_escala_chilena",
            ),
        ]
        verbose_name = "Nota"
        verbose_name_plural = "Notas"

    def __str__(self):
        return f"{self.alumno} - {self.detalle_asignatura.asignatura}: {self.valor}"
