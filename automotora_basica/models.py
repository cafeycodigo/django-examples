from django.db import models


class Vehiculo(models.Model):
  # Identificador numérico principal de cada vehículo.
  id_vehiculo = models.AutoField(primary_key=True)
  # Patente única que identifica al vehículo.
  patente = models.CharField(max_length=8, unique=True)
  # Marca y modelo comercial del vehículo.
  marca = models.CharField(max_length=40)
  modelo = models.CharField(max_length=40)
  # Año de fabricación y kilometraje actual.
  anio = models.IntegerField()
  kilometraje = models.IntegerField(default=0)
  # Tipo de combustible utilizado por el vehículo.
  combustible = models.CharField(max_length=15)
  # Características opcionales del vehículo.
  color = models.CharField(max_length=20,null=True,blank=True)
  capacidad_pasajeros = models.IntegerField(null=True,blank=True)
  # Fecha y hora asignadas automáticamente al registrar el vehículo.
  fecha_registro = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      # Representación breve para identificarlo en el admin y otras vistas.
      return f"{self.patente} - {self.marca} {self.modelo}"