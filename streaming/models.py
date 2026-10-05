from django.db import models


class Artista(models.Model):
    id_artista = models.AutoField(primary_key=True)

    nombre_artista = models.CharField(
        max_length=80
    )

    nacionalidad = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    descripcion = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    pagina_web = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_artista


class Album(models.Model):
    id_album = models.AutoField(primary_key=True)

    id_artista = models.ForeignKey(
        Artista,
        on_delete=models.CASCADE,
        db_column="id_artista"
    )

    titulo_album = models.CharField(
        max_length=100
    )

    anio = models.IntegerField()

    fecha_lanzamiento = models.DateField(
        null=True,
        blank=True
    )

    sello = models.CharField(
        max_length=60,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.titulo_album


class Cancion(models.Model):
    id_cancion = models.AutoField(primary_key=True)

    id_album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        db_column="id_album"
    )

    titulo = models.CharField(
        max_length=100
    )

    duracion_segundos = models.IntegerField()

    numero_pista = models.IntegerField(
        null=True,
        blank=True
    )

    explicito = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.titulo


class Playlist(models.Model):
    id_playlist = models.AutoField(primary_key=True)

    nombre_lista = models.CharField(
        max_length=80
    )

    descripcion = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    creada_por = models.CharField(
        max_length=60,
        null=True,
        blank=True
    )

    es_publica = models.BooleanField(
        default=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.nombre_lista


class PlaylistCancion(models.Model):
    id_playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        db_column="id_playlist"
    )

    id_cancion = models.ForeignKey(
        Cancion,
        on_delete=models.CASCADE,
        db_column="id_cancion"
    )

    orden = models.IntegerField()

    fecha_agregado = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["id_playlist", "id_cancion"],
                name="unique_playlist_cancion"
            )
        ]

    def __str__(self):
        return f"{self.id_playlist} - {self.id_cancion}"