from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Empleado


class EmpleadoIndexTests(TestCase):
    def test_index_shows_employees_created_by_seeder(self):
        empleado = Empleado.objects.create(
            rut="12345678-5",
            nombre_completo="Ana Ejemplo",
            cargo="Analista",
            salario=Decimal("1250000.00"),
            activo=True,
            email="ana@example.com",
            telefono="+56912345678",
        )

        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrhh/index.html")
        self.assertContains(response, empleado.rut)
        self.assertContains(response, empleado.nombre_completo)
        self.assertContains(response, empleado.cargo)
        self.assertContains(response, str(empleado.salario))
        self.assertContains(response, empleado.email)
        self.assertContains(response, empleado.telefono)

    def test_index_shows_message_when_there_are_no_employees(self):
        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No hay empleados registrados.")
