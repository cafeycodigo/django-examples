from django.conf import settings
from django.db import models


class Libro(models.Model):
    id_libro = models.AutoField(primary_key=True)

    titulo = models.CharField(
        max_length=120
    )

    autor = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    isbn = models.CharField(
        max_length=17,
        unique=True,
        null=True,
        blank=True
    )

    editorial = models.CharField(
        max_length=60,
        null=True,
        blank=True
    )

    anio_publicacion = models.IntegerField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.titulo


class Ejemplar(models.Model):
    id_ejemplar = models.AutoField(primary_key=True)

    id_libro = models.ForeignKey(
        Libro,
        on_delete=models.PROTECT,
        db_column="id_libro"
    )

    codigo_barra = models.CharField(
        max_length=20,
        unique=True
    )

    estado = models.CharField(
        max_length=20,
        default="DISPONIBLE"
    )

    fecha_adquisicion = models.DateField(
        null=True,
        blank=True
    )

    ubicacion = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.codigo_barra


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_biblioteca",
        null=True,
        blank=True
    )
    rut = models.CharField(max_length=12, unique=True)
    nombre_completo = models.CharField(max_length=100)
    email_institucional = models.EmailField(
        max_length=100,
        unique=True,
        help_text="Correo institucional del usuario"
    )
    carrera_o_departamento = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre_completo} ({self.rut})"


class Prestamo(models.Model):
    id_prestamo = models.AutoField(primary_key=True)

    id_ejemplar = models.ForeignKey(
        Ejemplar,
        on_delete=models.PROTECT,
        db_column="id_ejemplar"
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="prestamos_biblioteca",
        db_column="id_usuario"
    )

    fecha_prestamo = models.DateField()

    fecha_devolucion_pactada = models.DateField()

    fecha_devolucion_real = models.DateField(
        null=True,
        blank=True
    )

    estado = models.CharField(
        max_length=20,
        default="ACTIVO"
    )

    def __str__(self):
        nombre = getattr(self.usuario, "get_full_name", lambda: "")() or self.usuario.username
        return f"Préstamo #{self.id_prestamo} - {nombre}"


class Multa(models.Model):
    id_multa = models.AutoField(primary_key=True)

    id_prestamo = models.OneToOneField(
        Prestamo,
        on_delete=models.CASCADE,
        db_column="id_prestamo"
    )

    dias_retraso = models.IntegerField()

    monto_multa = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    pagada = models.BooleanField(
        default=False
    )

    fecha_generacion = models.DateTimeField(
        auto_now_add=True
    )

    motivo = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Multa #{self.id_multa}"