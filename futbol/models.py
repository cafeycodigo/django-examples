from django.db import models


class Club(models.Model):
    DIVISION_CHOICES = [
        ("primera", "Primera División"),
        ("primera_b", "Primera B (Segunda División)"),
    ]

    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Club")
    nombre_corto = models.CharField(max_length=30, verbose_name="Nombre Corto / Sigla")
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad")
    estadio = models.CharField(max_length=120, verbose_name="Estadio Principal")
    division = models.CharField(
        max_length=20,
        choices=DIVISION_CHOICES,
        default="primera",
        db_index=True,
        verbose_name="División",
    )
    fundacion_anio = models.PositiveIntegerField(default=1925, verbose_name="Año de Fundación")
    color_primario = models.CharField(max_length=20, default="#1e3a8a", verbose_name="Color Primario")
    color_secundario = models.CharField(max_length=20, default="#ffffff", verbose_name="Color Secundario")

    class Meta:
        verbose_name = "Club"
        verbose_name_plural = "Clubes"
        ordering = ["division", "nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.get_division_display()})"

    @property
    def es_primera(self):
        return self.division == "primera"


class Jugador(models.Model):
    POSICION_CHOICES = [
        ("arquero", "Arquero"),
        ("defensa", "Defensa"),
        ("mediocampista", "Mediocampista"),
        ("delantero", "Delantero"),
    ]

    rut = models.CharField(max_length=15, unique=True, db_index=True, verbose_name="RUT")
    nombre_completo = models.CharField(max_length=150, db_index=True, verbose_name="Nombre Completo")
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="jugadores",
        verbose_name="Club Actual",
    )
    posicion = models.CharField(
        max_length=20,
        choices=POSICION_CHOICES,
        default="mediocampista",
        verbose_name="Posición",
    )
    dorsal = models.PositiveIntegerField(default=10, verbose_name="Número de Camiseta")
    nacionalidad = models.CharField(max_length=50, default="Chilena", verbose_name="Nacionalidad")
    edad = models.PositiveIntegerField(default=25, verbose_name="Edad")

    class Meta:
        verbose_name = "Jugador"
        verbose_name_plural = "Jugadores"
        ordering = ["club", "dorsal"]

    def __str__(self):
        return f"#{self.dorsal} {self.nombre_completo} ({self.club.nombre_corto})"


class Campeonato(models.Model):
    DIVISION_CHOICES = [
        ("primera", "Primera División"),
        ("primera_b", "Primera B (Segunda División)"),
    ]

    nombre = models.CharField(max_length=120, verbose_name="Nombre del Campeonato")
    division = models.CharField(
        max_length=20,
        choices=DIVISION_CHOICES,
        default="primera",
        verbose_name="División",
    )
    temporada = models.PositiveIntegerField(default=2026, verbose_name="Temporada / Año")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Término")
    activo = models.BooleanField(default=True, verbose_name="En Disputa")

    class Meta:
        verbose_name = "Campeonato"
        verbose_name_plural = "Campeonatos"
        ordering = ["-temporada", "division"]

    def __str__(self):
        return f"{self.nombre} ({self.temporada})"


class Partido(models.Model):
    ESTADO_CHOICES = [
        ("programado", "Programado"),
        ("en_curso", "En Curso"),
        ("finalizado", "Finalizado"),
    ]

    campeonato = models.ForeignKey(
        Campeonato,
        on_delete=models.CASCADE,
        related_name="partidos",
        verbose_name="Campeonato",
    )
    jornada = models.PositiveIntegerField(default=1, verbose_name="Fecha / Jornada")
    club_local = models.ForeignKey(
        Club,
        on_delete=models.PROTECT,
        related_name="partidos_local",
        verbose_name="Equipo Local",
    )
    club_visita = models.ForeignKey(
        Club,
        on_delete=models.PROTECT,
        related_name="partidos_visita",
        verbose_name="Equipo Visitante",
    )
    fecha_partido = models.DateTimeField(db_index=True, verbose_name="Fecha y Hora")
    estadio = models.CharField(max_length=120, verbose_name="Estadio")
    goles_local = models.PositiveIntegerField(default=0, verbose_name="Goles Local")
    goles_visita = models.PositiveIntegerField(default=0, verbose_name="Goles Visita")
    publico_asistente = models.PositiveIntegerField(default=0, verbose_name="Público Asistente")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="finalizado",
        verbose_name="Estado",
    )

    class Meta:
        verbose_name = "Partido"
        verbose_name_plural = "Partidos"
        ordering = ["-fecha_partido"]

    def __str__(self):
        return f"Fecha {self.jornada}: {self.club_local.nombre_corto} {self.goles_local} - {self.goles_visita} {self.club_visita.nombre_corto}"

    @property
    def total_goles(self):
        return self.goles_local + self.goles_visita

    @property
    def es_goleada(self):
        """Se considera goleada si hay 4 o más goles totales o diferencia de 3 o más goles."""
        return abs(self.goles_local - self.goles_visita) >= 3 or self.total_goles >= 4

    @property
    def resultado(self):
        if self.goles_local > self.goles_visita:
            return "gana_local"
        elif self.goles_visita > self.goles_local:
            return "gana_visita"
        return "empate"


class Incidencia(models.Model):
    TIPO_CHOICES = [
        ("gol", "Gol"),
        ("tarjeta_amarilla", "Tarjeta Amarilla"),
        ("tarjeta_roja", "Tarjeta Roja"),
        ("lesion", "Lesión"),
    ]

    GRAVEDAD_CHOICES = [
        ("leve", "Leve (1-2 semanas)"),
        ("moderada", "Moderada (3-6 semanas)"),
        ("grave", "Grave (2+ meses)"),
    ]

    partido = models.ForeignKey(
        Partido,
        on_delete=models.CASCADE,
        related_name="incidencias",
        verbose_name="Partido",
    )
    jugador = models.ForeignKey(
        Jugador,
        on_delete=models.CASCADE,
        related_name="incidencias",
        verbose_name="Jugador Involucrado",
    )
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="incidencias",
        verbose_name="Club del Jugador",
    )
    tipo = models.CharField(
        max_length=25,
        choices=TIPO_CHOICES,
        db_index=True,
        verbose_name="Tipo de Incidencia",
    )
    minuto = models.PositiveIntegerField(default=45, verbose_name="Minuto del Partido")
    detalle = models.CharField(max_length=200, blank=True, verbose_name="Detalle de la jugada / diagnóstico")
    gravedad_lesion = models.CharField(
        max_length=20,
        choices=GRAVEDAD_CHOICES,
        blank=True,
        null=True,
        verbose_name="Gravedad (si fue lesión)",
    )

    class Meta:
        verbose_name = "Incidencia de Partido"
        verbose_name_plural = "Incidencias de Partidos"
        ordering = ["partido", "minuto"]
        indexes = [
            models.Index(fields=["partido", "tipo"]),
            models.Index(fields=["jugador", "tipo"]),
            models.Index(fields=["club", "tipo"]),
        ]

    def __str__(self):
        return f"Min {self.minuto}' [{self.get_tipo_display()}] {self.jugador.nombre_completo} ({self.club.nombre_corto})"
