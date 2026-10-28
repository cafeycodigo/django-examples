from django.test import TestCase
from django.urls import reverse

from .models import Categoria, Evento


class EventoIndexTests(TestCase):
    def test_index_devuelve_todos_los_eventos(self):
        categoria = Categoria.objects.create(nombre="Tecnología")
        evento = Evento.objects.create(
            titulo="Feria de programación",
            descripcion="Muestra académica",
            categoria=categoria,
            fecha_inicio="2026-11-01T10:00:00Z",
            ubicacion="Santiago",
        )

        response = self.client.get(reverse("eventos:index"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], evento.id)
        self.assertEqual(response.json()[0]["titulo"], evento.titulo)
        self.assertEqual(response.json()[0]["categoria_id"], categoria.id)

    def test_index_devuelve_lista_vacia_sin_eventos(self):
        response = self.client.get(reverse("eventos:index"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
