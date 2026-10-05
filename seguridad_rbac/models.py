from django.db import models


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=40, unique=True)
    descripcion = models.CharField(
        max_length=120,
        null=True,
        blank=True
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_rol


class Permiso(models.Model):
    id_permiso = models.AutoField(primary_key=True)
    codigo_permiso = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(
        max_length=120,
        null=True,
        blank=True
    )
    categoria = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.codigo_permiso


class RolPermiso(models.Model):
    id_rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        db_column="id_rol"
    )

    id_permiso = models.ForeignKey(
        Permiso,
        on_delete=models.CASCADE,
        db_column="id_permiso"
    )

    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    asignado_por = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["id_rol", "id_permiso"],
                name="unique_rol_permiso"
            )
        ]

    def __str__(self):
        return f"{self.id_rol} - {self.id_permiso}"


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)

    username = models.CharField(
        max_length=40,
        unique=True
    )

    email = models.EmailField(
        max_length=100,
        unique=True
    )

    id_rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        db_column="id_rol"
    )

    password_hash = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.username


class Perfil(models.Model):
    id_perfil = models.AutoField(primary_key=True)

    id_usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        db_column="id_usuario"
    )

    avatar_url = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    telefono = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    nombres = models.CharField(
        max_length=80,
        null=True,
        blank=True
    )

    fecha_nacimiento = models.DateField(
        null=True,
        blank=True
    )

    direccion = models.CharField(
        max_length=120,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nombres or self.id_usuario.username