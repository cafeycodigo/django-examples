from django.db import models

class Cliente(models.Model):
  id_cliente = models.AutoField(primary_key=True)
  nombre = models.CharField(max_length=80)
  email = models.EmailField(max_length=100, unique=True)
  telefono = models.CharField(max_length=20, null=True, blank=True)
  direccion = models.CharField(max_length=120, null=True, blank=True)
  fecha_registro = models.DateTimeField(auto_now_add=True)
  activo = models.BooleanField(default=True)

  def __str__(self):
      return self.nombre


class Producto(models.Model):
  id_producto = models.AutoField(primary_key=True)
  nombre_producto = models.CharField(max_length=80)
  precio_actual = models.DecimalField(
      max_digits=10,
      decimal_places=2
  )
  categoria = models.CharField(
      max_length=50,
      null=True,
      blank=True
  )
  stock = models.IntegerField(default=0)
  descripcion = models.CharField(
      max_length=200,
      null=True,
      blank=True
  )

  def __str__(self):
      return self.nombre_producto


class Pedido(models.Model):
  id_pedido = models.AutoField(primary_key=True)

  id_cliente = models.ForeignKey(
      Cliente,
      on_delete=models.CASCADE,
      db_column="id_cliente",
      related_name="pedidos"
  )

  fecha_pedido = models.DateTimeField(auto_now_add=True)

  estado = models.CharField(
      max_length=20,
      default="PAGADO"
  )

  metodo_pago = models.CharField(
      max_length=30,
      null=True,
      blank=True
  )

  direccion_envio = models.CharField(
      max_length=120,
      null=True,
      blank=True
  )

  observaciones = models.CharField(
      max_length=200,
      null=True,
      blank=True
  )

  def __str__(self):
      return f"Pedido #{self.id_pedido}"


class DetallePedido(models.Model):
  id_detalle = models.AutoField(primary_key=True)

  id_pedido = models.ForeignKey(
      Pedido,
      on_delete=models.CASCADE,
      db_column="id_pedido",
      related_name="detalles"
  )

  id_producto = models.ForeignKey(
      Producto,
      on_delete=models.PROTECT,
      db_column="id_producto",
      related_name="detalles"
  )

  cantidad = models.IntegerField()

  precio_unitario_historico = models.DecimalField(
      max_digits=10,
      decimal_places=2
  )

  descuento = models.DecimalField(
      max_digits=5,
      decimal_places=2,
      default=0
  )

  class Meta:
      constraints = [
          models.UniqueConstraint(
              fields=["id_pedido", "id_producto"],
              name="unique_pedido_producto"
          )
      ]

  def __str__(self):
      return f"Detalle #{self.id_detalle}"