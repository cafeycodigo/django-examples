from django.test import TestCase, Client
from django.urls import reverse
from eventos.models import Categoria, Persona, Evento, Asistencia


class EventosModelTestCase(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nombre="Tecnología Test",
            descripcion="Eventos tecnológicos",
            color="#6366f1",
        )
        self.evento_free = Evento.objects.create(
            titulo="Conferencia Gratuita",
            descripcion="Evento de acceso libre",
            categoria=self.categoria,
            valor=0.00,
            fecha_inicio="2026-11-01 10:00:00+00:00",
            ubicacion="Online",
        )
        self.evento_pago = Evento.objects.create(
            titulo="Masterclass Avanzada",
            descripcion="Evento premium de pago",
            categoria=self.categoria,
            valor=25000.00,
            fecha_inicio="2026-11-05 14:00:00+00:00",
            ubicacion="Centro de Convenciones",
        )
        self.persona = Persona.objects.create(
            rut="12345678-5",
            nombre_completo="Juan Pérez González",
            email="juan.perez@test.cl",
            telefono="+56912345678",
            ciudad="Santiago",
        )

    def test_evento_free_property(self):
        self.assertTrue(self.evento_free.es_free)
        self.assertTrue(self.evento_free.es_gratuito)
        self.assertEqual(self.evento_free.valor, 0.00)

    def test_evento_pago_property(self):
        self.assertFalse(self.evento_pago.es_free)
        self.assertFalse(self.evento_pago.es_gratuito)
        self.assertEqual(self.evento_pago.valor, 25000.00)

    def test_asistencia_creacion(self):
        asistencia = Asistencia.objects.create(
            evento=self.evento_free,
            persona=self.persona,
            asistio=True,
            precio_pagado=0.00,
        )
        self.assertTrue(asistencia.asistio)
        self.assertIsNotNone(asistencia.codigo_ticket)
        self.assertEqual(self.persona.asistencias.count(), 1)


class EventosViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.categoria = Categoria.objects.create(nombre="Música", color="#ec4899")
        self.evento = Evento.objects.create(
            titulo="Festival de Jazz",
            descripcion="Música en vivo",
            categoria=self.categoria,
            valor=15000.00,
            fecha_inicio="2026-12-01 19:00:00+00:00",
            ubicacion="Teatro Caupolicán",
        )
        self.persona = Persona.objects.create(
            rut="11111111-1",
            nombre_completo="María Paz Soto",
            email="maria.paz@test.cl",
        )
        self.asistencia = Asistencia.objects.create(
            evento=self.evento,
            persona=self.persona,
            asistio=True,
            precio_pagado=15000.00,
        )

    def test_eventos_list_view(self):
        response = self.client.get(reverse("eventos:eventos_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Festival de Jazz")
        self.assertContains(response, "Total Eventos")

    def test_evento_detalle_view(self):
        response = self.client.get(reverse("eventos:evento_detalle", args=[self.evento.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Festival de Jazz")
        self.assertContains(response, "María Paz Soto")

    def test_personas_list_view(self):
        response = self.client.get(reverse("eventos:personas_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "María Paz Soto")

    def test_persona_detalle_view(self):
        response = self.client.get(reverse("eventos:persona_detalle", args=[self.persona.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "María Paz Soto")
        self.assertContains(response, "Festival de Jazz")

    def test_categorias_dashboard_view(self):
        response = self.client.get(reverse("eventos:categorias_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Música")

    def test_api_stats_view(self):
        response = self.client.get(reverse("eventos:api_stats"))
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data["status"], "success")
        self.assertIn("total_eventos", json_data["data"])
        self.assertIn("total_personas", json_data["data"])
