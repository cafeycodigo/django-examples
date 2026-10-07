from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Vehiculo


class VehiculoCrudTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="staff",
            is_staff=True,
        )
        self.client.force_login(self.staff_user)
        self.vehiculo = Vehiculo.objects.create(
            patente="ABCD12",
            marca="Toyota",
            modelo="Corolla",
            anio=2022,
            kilometraje=15000,
            combustible="Bencina",
        )
        Vehiculo.objects.create(
            patente="WXYZ34",
            marca="Kia",
            modelo="Rio",
            anio=2021,
            combustible="Diesel",
        )

    def test_list_shows_vehicle_and_searches_by_query(self):
        response = self.client.get(
            reverse("automotora_basica:vehiculo_list"),
            {"q": "Toyota"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ABCD12")
        self.assertContains(response, "Toyota")
        self.assertNotContains(response, "WXYZ34")
        self.assertContains(response, "vehículos en total")

    def test_create_adds_vehicle(self):
        response = self.client.post(
            reverse("automotora_basica:vehiculo_create"),
            {
                "patente": "LMNO56",
                "marca": "Kia",
                "modelo": "Rio",
                "anio": 2021,
                "kilometraje": 25000,
                "combustible": "Bencina",
                "color": "Azul",
                "capacidad_pasajeros": 5,
            },
        )

        self.assertRedirects(
            response,
            reverse("automotora_basica:vehiculo_list"),
        )
        self.assertTrue(Vehiculo.objects.filter(patente="LMNO56").exists())

    def test_create_renders_validation_error_for_duplicate_patente(self):
        response = self.client.post(
            reverse("automotora_basica:vehiculo_create"),
            {
                "patente": "ABCD12",
                "marca": "Kia",
                "modelo": "Rio",
                "anio": 2021,
                "kilometraje": 25000,
                "combustible": "Bencina",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Patente")
        self.assertContains(response, "Ya existe un vehículo con esta patente.")
        self.assertEqual(Vehiculo.objects.count(), 2)

    def test_empty_post_shows_required_field_errors(self):
        response = self.client.post(
            reverse("automotora_basica:vehiculo_create"),
            {},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'aria-invalid="true"')
        self.assertContains(response, "Este campo es obligatorio.")

    def test_update_changes_vehicle(self):
        response = self.client.post(
            reverse(
                "automotora_basica:vehiculo_update",
                args=[self.vehiculo.pk],
            ),
            {
                "patente": "ABCD12",
                "marca": "Toyota",
                "modelo": "Yaris",
                "anio": 2023,
                "kilometraje": 10000,
                "combustible": "Híbrido",
            },
        )

        self.assertRedirects(
            response,
            reverse("automotora_basica:vehiculo_list"),
        )
        self.vehiculo.refresh_from_db()
        self.assertEqual(self.vehiculo.modelo, "Yaris")
        self.assertEqual(self.vehiculo.anio, 2023)

    def test_delete_requires_post_confirmation(self):
        url = reverse(
            "automotora_basica:vehiculo_delete",
            args=[self.vehiculo.pk],
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Vehiculo.objects.filter(pk=self.vehiculo.pk).exists())

        response = self.client.post(url)
        self.assertRedirects(
            response,
            reverse("automotora_basica:vehiculo_list"),
        )
        self.assertFalse(Vehiculo.objects.filter(pk=self.vehiculo.pk).exists())

    def test_crud_requires_staff_login(self):
        self.client.logout()

        response = self.client.get(
            reverse("automotora_basica:vehiculo_list")
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])


class VehiculoAdminTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password=None,
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
