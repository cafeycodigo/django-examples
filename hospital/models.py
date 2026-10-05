from django.db import models


class Especialidad(models.Model):
    id_especialidad = models.AutoField(primary_key=True)

    nombre_especialidad = models.CharField(
        max_length=50,
        unique=True
    )

    descripcion = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    costo_consulta = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_especialidad


class Medico(models.Model):
    id_medico = models.AutoField(primary_key=True)

    id_especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,
        db_column="id_especialidad"
    )

    nombre = models.CharField(max_length=80)

    rut = models.CharField(
        max_length=12,
        unique=True,
        null=True,
        blank=True
    )

    telefono = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    email = models.EmailField(
        max_length=100,
        null=True,
        blank=True
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Paciente(models.Model):
    id_paciente = models.AutoField(primary_key=True)

    nombre = models.CharField(max_length=80)

    rut = models.CharField(
        max_length=12,
        unique=True
    )

    fecha_nacimiento = models.DateField(
        null=True,
        blank=True
    )

    telefono = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    direccion = models.CharField(
        max_length=120,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nombre


class Cita(models.Model):
    id_cita = models.AutoField(primary_key=True)

    id_paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        db_column="id_paciente"
    )

    id_medico = models.ForeignKey(
        Medico,
        on_delete=models.PROTECT,
        db_column="id_medico"
    )

    fecha_hora = models.DateTimeField()

    estado = models.CharField(
        max_length=20,
        default="AGENDADA"
    )

    motivo = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Cita #{self.id_cita}"


class Receta(models.Model):
    id_receta = models.AutoField(primary_key=True)

    id_cita = models.ForeignKey(
        Cita,
        on_delete=models.CASCADE,
        db_column="id_cita"
    )

    medicamento = models.CharField(max_length=100)

    posologia = models.CharField(max_length=150)

    dosis = models.CharField(
        max_length=60,
        null=True,
        blank=True
    )

    duracion_dias = models.IntegerField(
        null=True,
        blank=True
    )

    observaciones = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.medicamento