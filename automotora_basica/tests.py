from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Vehiculo


class VehiculoAdminTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password",
        )
        self.client.force_login(self.admin_user)

    def test_admin_changelist_displays_vehicles(self):
        Vehiculo.objects.create(
            patente="ABCD12",
            marca="Toyota",
            modelo="Corolla",
            anio=2022,
            kilometraje=15000,
            combustible="Bencina",
        )

        response = self.client.get(
            reverse("admin:automotora_basica_vehiculo_changelist")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ABCD12")
        self.assertContains(response, "Toyota")

    def test_admin_changelist_can_search_by_patente(self):
        Vehiculo.objects.create(
            patente="ABCD12",
            marca="Toyota",
            modelo="Corolla",
            anio=2022,
            combustible="Bencina",
        )
        Vehiculo.objects.create(
            patente="WXYZ34",
            marca="Kia",
            modelo="Rio",
            anio=2021,
            combustible="Diesel",
        )

        response = self.client.get(
            reverse("admin:automotora_basica_vehiculo_changelist"),
            {"q": "ABCD12"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ABCD12")
        self.assertNotContains(response, "WXYZ34")
