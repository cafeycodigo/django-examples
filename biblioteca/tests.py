from django.test import TestCase
from django.urls import reverse

from .models import Ejemplar, Libro


class LibroCrudTests(TestCase):
    def setUp(self):
        self.libro = Libro.objects.create(
            titulo="El principito",
            autor="Antoine de Saint-Exupéry",
            isbn="9780156012195",
            editorial="Reynal & Hitchcock",
            anio_publicacion=1943,
        )

    def test_listado_muestra_libros_y_rutas_son_distintas_de_usuarios(self):
        response = self.client.get(reverse("libro_listar"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.libro.titulo)
        self.assertEqual(reverse("libro_listar"), "/biblioteca/libros/")
        self.assertEqual(reverse("usuario_listar"), "/biblioteca/usuarios/")

    def test_detalle_muestra_libro_y_ejemplares(self):
        Ejemplar.objects.create(id_libro=self.libro, codigo_barra="BC-001")

        response = self.client.get(reverse("libro_detalle", args=[self.libro.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.libro.titulo)
        self.assertContains(response, "BC-001")

    def test_crear_libro_valido(self):
        response = self.client.post(reverse("libro_crear"), {
            "titulo": "Django para principiantes",
            "autor": "Ada Lovelace",
            "isbn": "9780000000001",
            "editorial": "Editorial Ejemplo",
            "anio_publicacion": 2024,
        })

        libro = Libro.objects.get(isbn="9780000000001")
        self.assertRedirects(response, reverse("libro_detalle", args=[libro.pk]))
        self.assertEqual(libro.titulo, "Django para principiantes")

    def test_formulario_rechaza_isbn_duplicado(self):
        response = self.client.post(reverse("libro_crear"), {
            "titulo": "Otro título",
            "isbn": self.libro.isbn,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ya existe un libro con este ISBN")
        self.assertEqual(Libro.objects.count(), 1)

    def test_formulario_muestra_error_si_falta_el_titulo(self):
        response = self.client.post(reverse("libro_crear"), {})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "El título es obligatorio")
        self.assertEqual(Libro.objects.count(), 1)

    def test_actualizar_libro(self):
        response = self.client.post(
            reverse("libro_actualizar", args=[self.libro.pk]),
            {
                "titulo": "El principito (edición revisada)",
                "autor": self.libro.autor,
                "isbn": self.libro.isbn,
                "editorial": self.libro.editorial,
                "anio_publicacion": self.libro.anio_publicacion,
            },
        )

        self.libro.refresh_from_db()
        self.assertRedirects(response, reverse("libro_detalle", args=[self.libro.pk]))
        self.assertEqual(self.libro.titulo, "El principito (edición revisada)")

    def test_eliminar_libro_sin_ejemplares(self):
        response = self.client.post(reverse("libro_eliminar", args=[self.libro.pk]))

        self.assertRedirects(response, reverse("libro_listar"))
        self.assertFalse(Libro.objects.filter(pk=self.libro.pk).exists())

    def test_no_eliminar_libro_con_ejemplares(self):
        Ejemplar.objects.create(id_libro=self.libro, codigo_barra="BC-002")

        response = self.client.post(
            reverse("libro_eliminar", args=[self.libro.pk]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Libro.objects.filter(pk=self.libro.pk).exists())
        self.assertContains(
            response,
            "No se puede eliminar este libro mientras tenga ejemplares asociados",
        )
