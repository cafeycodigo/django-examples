from django.db import models


class Vehiculo(models.Model):
  id_vehiculo = models.AutoField(primary_key=True)
  patente = models.CharField(max_length=8, unique=True)
  marca = models.CharField(max_length=40)
  modelo = models.CharField(max_length=40)
  anio = models.IntegerField()
  kilometraje = models.IntegerField(default=0)
  combustible = models.CharField(max_length=15)
  color = models.CharField(max_length=20,null=True,blank=True)
  capacidad_pasajeros = models.IntegerField(null=True,blank=True)
  fecha_registro = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return f"{self.patente} - {self.marca} {self.modelo}"