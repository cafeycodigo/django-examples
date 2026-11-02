"""Modelo territorial y de gestión ciudadana de ConectaVecinos."""

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.utils import timezone


def codigo_incidencia():
    return f"CV-{timezone.now():%Y}-{uuid.uuid4().hex[:24].upper()}"


class Registro(models.Model):
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Municipalidad(Registro):
    nombre = models.CharField(max_length=180)
    comuna = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    direccion = models.CharField(max_length=250, blank=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Comunidad(Registro):
    class Tipo(models.TextChoices):
        BARRIO = "barrio", "Barrio"
        VILLA = "villa", "Villa"
        POBLACION = "poblacion", "Población"
        EDIFICIO = "edificio", "Edificio"
        CONDOMINIO = "condominio", "Condominio"

    municipalidad = models.ForeignKey(Municipalidad, on_delete=models.PROTECT, related_name="comunidades")
    nombre = models.CharField(max_length=180)
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.BARRIO)
    direccion = models.CharField(max_length=250, blank=True)
    activa = models.BooleanField(default=True)
    miembros = models.ManyToManyField(settings.AUTH_USER_MODEL, through="UsuarioComunidad", related_name="comunidades_vecinales")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["municipalidad", "nombre"], name="cv_comunidad_nombre_unico")]

    def __str__(self):
        return self.nombre


class UsuarioComunidad(Registro):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    verificado = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["usuario", "comunidad"], name="cv_membresia_unica")]


class Rol(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True)
    permisos = models.ManyToManyField("auth.Permission", blank=True, related_name="roles_vecinales")

    def __str__(self):
        return self.nombre


class UsuarioRol(Registro):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="roles_vecinales")
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT)
    municipalidad = models.ForeignKey(Municipalidad, on_delete=models.CASCADE)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["usuario", "rol", "municipalidad", "comunidad"], condition=models.Q(comunidad__isnull=False), name="cv_rol_comunitario_unico"),
            models.UniqueConstraint(fields=["usuario", "rol", "municipalidad"], condition=models.Q(comunidad__isnull=True), name="cv_rol_municipal_unico"),
        ]

    def clean(self):
        if self.comunidad_id and self.municipalidad_id and self.comunidad.municipalidad_id != self.municipalidad_id:
            raise ValidationError({"comunidad": "La comunidad debe pertenecer a la municipalidad."})


class Catalogo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        abstract = True
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Categoria(Catalogo):
    activa = models.BooleanField(default=True)


class Prioridad(Catalogo):
    nivel = models.PositiveSmallIntegerField(unique=True, validators=[MinValueValidator(1)])


class EstadoIncidencia(Catalogo):
    codigo = models.SlugField(max_length=40, unique=True)
    es_final = models.BooleanField(default=False)


class Incidencia(Registro):
    class Visibilidad(models.TextChoices):
        PUBLICA = "publica", "Pública"
        RESTRINGIDA = "restringida", "Restringida"

    class Tipo(models.TextChoices):
        PROBLEMA = "problema", "Problema"
        SOLICITUD = "solicitud", "Solicitud de intervención"
        INICIATIVA = "iniciativa", "Iniciativa comunitaria"

    codigo = models.CharField(max_length=40, unique=True, default=codigo_incidencia, editable=False)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="incidencias")
    comunidad = models.ForeignKey(Comunidad, on_delete=models.PROTECT, related_name="incidencias")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="incidencias")
    prioridad = models.ForeignKey(Prioridad, on_delete=models.PROTECT, related_name="incidencias")
    estado = models.ForeignKey(EstadoIncidencia, on_delete=models.PROTECT, related_name="incidencias")
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.PROBLEMA)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    ubicacion_referencia = models.CharField(max_length=250)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, validators=[MinValueValidator(-180), MaxValueValidator(180)])
    visibilidad = models.CharField(max_length=20, choices=Visibilidad.choices, default=Visibilidad.RESTRINGIDA)
    cerrada_en = models.DateTimeField(null=True, blank=True)
    duplicada_de = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, related_name="duplicadas")

    class Meta:
        ordering = ["-creada_en"]
        indexes = [models.Index(fields=["comunidad", "estado"]), models.Index(fields=["visibilidad", "-creada_en"])]
        constraints = [
            models.CheckConstraint(condition=models.Q(latitud__isnull=True, longitud__isnull=True) | models.Q(latitud__isnull=False, longitud__isnull=False), name="cv_coordenadas_completas"),
            models.CheckConstraint(condition=models.Q(latitud__isnull=True) | models.Q(latitud__gte=-90, latitud__lte=90), name="cv_latitud_valida"),
            models.CheckConstraint(condition=models.Q(longitud__isnull=True) | models.Q(longitud__gte=-180, longitud__lte=180), name="cv_longitud_valida"),
            models.CheckConstraint(condition=~models.Q(duplicada_de=models.F("pk")), name="cv_no_autoduplicada"),
            models.CheckConstraint(condition=models.Q(cerrada_en__isnull=True) | models.Q(cerrada_en__gte=models.F("creada_en")), name="cv_cierre_posterior"),
        ]

    def __str__(self):
        return f"{self.codigo}: {self.titulo}"

    def clean(self):
        if self.duplicada_de_id:
            visitadas = {self.pk} if self.pk else set()
            original = self.duplicada_de
            while original:
                if original.pk in visitadas:
                    raise ValidationError({"duplicada_de": "No se permiten ciclos de incidencias duplicadas."})
                visitadas.add(original.pk)
                if original.comunidad_id != self.comunidad_id:
                    raise ValidationError({"duplicada_de": "La incidencia original debe pertenecer a la misma comunidad."})
                original = original.duplicada_de

    def cambiar_estado(self, nuevo_estado, responsable, observacion):
        """Actualiza el estado y su historial en una misma transacción."""
        if not observacion.strip():
            raise ValidationError("Debe indicar el motivo del cambio de estado.")
        with transaction.atomic():
            actual = type(self).objects.select_for_update().get(pk=self.pk)
            if actual.estado_id == nuevo_estado.pk:
                raise ValidationError("La incidencia ya tiene ese estado.")
            seguimiento = Seguimiento.objects.create(
                incidencia=actual, responsable=responsable, descripcion=observacion,
                estado_anterior_id=actual.estado_id, estado_nuevo=nuevo_estado,
            )
            actual.estado = nuevo_estado
            actual.cerrada_en = timezone.now() if nuevo_estado.es_final else None
            actual.save(update_fields=["estado", "cerrada_en", "actualizada_en"])
            Notificacion.objects.create(usuario=actual.autor, incidencia=actual, mensaje=f"{actual.codigo}: {nuevo_estado.nombre}")
        self.estado = actual.estado
        self.cerrada_en = actual.cerrada_en
        return seguimiento


class UnidadMunicipal(Registro):
    municipalidad = models.ForeignKey(Municipalidad, on_delete=models.PROTECT, related_name="unidades")
    nombre = models.CharField(max_length=150)
    correo = models.EmailField(blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["municipalidad", "nombre"], name="cv_unidad_nombre_unico")]

    def __str__(self):
        return self.nombre


class Asignacion(Registro):
    incidencia = models.ForeignKey(Incidencia, on_delete=models.PROTECT, related_name="asignaciones")
    unidad = models.ForeignKey(UnidadMunicipal, on_delete=models.PROTECT, related_name="asignaciones")
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="asignaciones_vecinales")
    asignada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="derivaciones_vecinales")
    observacion = models.TextField(blank=True)
    plazo = models.DateTimeField(null=True, blank=True)
    finalizada_en = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.incidencia_id and self.unidad_id and self.incidencia.comunidad.municipalidad_id != self.unidad.municipalidad_id:
            raise ValidationError({"unidad": "La unidad debe pertenecer a la municipalidad de la incidencia."})


class Seguimiento(Registro):
    incidencia = models.ForeignKey(Incidencia, on_delete=models.PROTECT, related_name="seguimientos")
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    descripcion = models.TextField()
    estado_anterior = models.ForeignKey(EstadoIncidencia, on_delete=models.PROTECT, null=True, blank=True, related_name="seguimientos_salientes")
    estado_nuevo = models.ForeignKey(EstadoIncidencia, on_delete=models.PROTECT, null=True, blank=True, related_name="seguimientos_entrantes")
    publico = models.BooleanField(default=False)

    class Meta:
        ordering = ["creada_en", "pk"]


class Decision(Registro):
    class Resultado(models.TextChoices):
        APROBADA = "aprobada", "Aprobada"
        RECHAZADA = "rechazada", "Rechazada"
        ANTECEDENTES = "antecedentes", "Solicitar antecedentes"

    incidencia = models.ForeignKey(Incidencia, on_delete=models.PROTECT, related_name="decisiones")
    autoridad = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    resultado = models.CharField(max_length=20, choices=Resultado.choices)
    fundamento = models.TextField()


class Evidencia(Registro):
    incidencia = models.ForeignKey(Incidencia, on_delete=models.PROTECT, related_name="evidencias")
    subida_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    archivo = models.FileField(upload_to="conectavecinos/evidencias/%Y/%m/")
    descripcion = models.CharField(max_length=250, blank=True)
    publica = models.BooleanField(default=False)


class Comentario(Registro):
    incidencia = models.ForeignKey(Incidencia, on_delete=models.CASCADE, related_name="comentarios")
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    contenido = models.TextField()
    publico = models.BooleanField(default=False)


class Apoyo(Registro):
    incidencia = models.ForeignKey(Incidencia, on_delete=models.CASCADE, related_name="apoyos")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["incidencia", "usuario"], name="cv_apoyo_unico")]


class Evaluacion(Registro):
    incidencia = models.ForeignKey(Incidencia, on_delete=models.PROTECT, related_name="evaluaciones")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    puntuacion = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True)
    solucion_confirmada = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["incidencia", "usuario"], name="cv_evaluacion_unica"),
            models.CheckConstraint(condition=models.Q(puntuacion__gte=1, puntuacion__lte=5), name="cv_puntuacion_valida"),
        ]

    def clean(self):
        if self.incidencia_id and not self.incidencia.estado.es_final:
            raise ValidationError({"incidencia": "Solo se pueden evaluar incidencias finalizadas."})


class Notificacion(Registro):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notificaciones_vecinales")
    incidencia = models.ForeignKey(Incidencia, on_delete=models.CASCADE, related_name="notificaciones")
    mensaje = models.CharField(max_length=250)
    leida_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-creada_en"]
        indexes = [models.Index(fields=["usuario", "leida_en"])]
