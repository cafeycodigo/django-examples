import uuid
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    color = models.CharField(max_length=20, default="#6366f1", verbose_name="Color distintivo")
    icono = models.CharField(max_length=50, default="bi-calendar-event", verbose_name="Ícono")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Persona(models.Model):
    rut = models.CharField(max_length=15, unique=True, db_index=True, verbose_name="RUT / Identificación")
    nombre_completo = models.CharField(max_length=150, db_index=True, verbose_name="Nombre completo")
    email = models.EmailField(max_length=150, unique=True, db_index=True, verbose_name="Correo electrónico")
    telefono = models.CharField(max_length=25, blank=True, verbose_name="Teléfono")
    ciudad = models.CharField(max_length=100, blank=True, verbose_name="Ciudad")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        ordering = ["nombre_completo"]

    def __str__(self):
        return f"{self.nombre_completo} ({self.rut})"


class Evento(models.Model):
    ESTADO_CHOICES = [
        ("programado", "Programado"),
        ("en_curso", "En Curso"),
        ("finalizado", "Finalizado"),
        ("cancelado", "Cancelado"),
    ]

    titulo = models.CharField(max_length=200, db_index=True, verbose_name="Título del evento")
    descripcion = models.TextField(verbose_name="Descripción")
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="eventos",
        verbose_name="Categoría",
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        db_index=True,
        verbose_name="Valor de entrada",
    )
    es_gratuito = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="¿Es gratuito (Free)?",
        help_text="Indica si el evento es gratuito (sin costo de entrada)",
    )
    fecha_inicio = models.DateTimeField(db_index=True, verbose_name="Fecha y hora de inicio")
    fecha_fin = models.DateTimeField(blank=True, null=True, verbose_name="Fecha y hora de término")
    ubicacion = models.CharField(max_length=200, verbose_name="Ubicación o Lugar")
    es_online = models.BooleanField(default=False, verbose_name="Modalidad Online")
    capacidad_maxima = models.PositiveIntegerField(default=100, verbose_name="Capacidad máxima")
    organizador = models.CharField(max_length=150, blank=True, verbose_name="Organizador")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="finalizado",
        verbose_name="Estado",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["-fecha_inicio"]

    def __str__(self):
        tipo = "FREE" if self.es_free else f"${self.valor:,.0f}"
        return f"{self.titulo} [{tipo}] ({self.categoria.nombre})"

    @property
    def es_free(self):
        return self.es_gratuito or self.valor == 0

    def save(self, *args, **kwargs):
        if self.valor == 0:
            self.es_gratuito = True
        elif self.es_gratuito:
            self.valor = 0
        super().save(*args, **kwargs)


class Asistencia(models.Model):
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="asistencias",
        verbose_name="Evento",
    )
    persona = models.ForeignKey(
        Persona,
        on_delete=models.CASCADE,
        related_name="asistencias",
        verbose_name="Persona asistente",
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de inscripción")
    asistio = models.BooleanField(
        default=True,
        verbose_name="¿Asistió efectivamente?",
        help_text="Indica si la persona asistió al evento",
    )
    precio_pagado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Precio pagado",
    )
    codigo_ticket = models.CharField(
        max_length=36,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Código de ticket",
    )

    class Meta:
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        constraints = [
            models.UniqueConstraint(
                fields=["evento", "persona"],
                name="unique_asistencia_evento_persona",
            )
        ]
        indexes = [
            models.Index(fields=["evento", "asistio"]),
            models.Index(fields=["persona", "asistio"]),
        ]

    def __str__(self):
        return f"{self.persona.nombre_completo} en {self.evento.titulo}"

    def save(self, *args, **kwargs):
        if not self.codigo_ticket:
            self.codigo_ticket = str(uuid.uuid4()).replace("-", "").upper()[:12]
        super().save(*args, **kwargs)
