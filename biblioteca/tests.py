from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Ejemplar, Libro, Usuario


class LibroCrudTests(TestCase):
    def setUp(self):
        self.auth_user = get_user_model().objects.create_user(
            username="operador",
            password="ClaveSegura-2026",
        )
        self.client.force_login(self.auth_user)
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

    def test_login_con_credenciales_validas(self):
        client = Client()

        response = client.post(reverse("login"), {
            "username": "operador",
            "password": "ClaveSegura-2026",
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("index"))
        self.assertTrue(response.context["user"].is_authenticated)

    def test_login_regresa_a_la_ruta_protegida_solicitada(self):
        client = Client()
        ruta_destino = reverse("libro_crear")

        response = client.post(reverse("login"), {
            "username": "operador",
            "password": "ClaveSegura-2026",
            "next": ruta_destino,
        })

        self.assertRedirects(response, ruta_destino)
        self.assertTrue(client.session.get("_auth_user_id"))

    def test_login_no_redirige_a_un_host_externo(self):
        client = Client()

        response = client.post(reverse("login"), {
            "username": "operador",
            "password": "ClaveSegura-2026",
            "next": "https://sitio-malicioso.example/",
        })

        self.assertRedirects(response, reverse("index"))

    def test_login_rechaza_credenciales_invalidas(self):
        response = Client().post(reverse("login"), {
            "username": "operador",
            "password": "incorrecta",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "no son correctos")

    def test_logout_cierra_sesion_mediante_post(self):
        response = self.client.post(reverse("logout"), follow=True)

        self.assertRedirects(response, reverse("login"))
        self.assertFalse(response.context["user"].is_authenticated)

    def test_logout_no_permite_get(self):
        response = self.client.get(reverse("logout"))

        self.assertEqual(response.status_code, 405)

    def test_rutas_de_escritura_redirigen_a_login_si_no_hay_sesion(self):
        perfil = Usuario.objects.create(
            user=self.auth_user,
            rut="12345678-5",
            nombre_completo="Operador Biblioteca",
            email_institucional="operador@universidad.cl",
        )
        cliente_anonimo = Client()
        rutas_protegidas = (
            reverse("prestamo_crear"),
            reverse("usuario_crear"),
            reverse("usuario_actualizar", args=[perfil.pk]),
            reverse("usuario_eliminar", args=[perfil.pk]),
            reverse("libro_crear"),
            reverse("libro_actualizar", args=[self.libro.pk]),
            reverse("libro_eliminar", args=[self.libro.pk]),
        )

        for ruta in rutas_protegidas:
            with self.subTest(ruta=ruta):
                response = cliente_anonimo.get(ruta)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, f"{reverse('login')}?next={ruta}")

    def test_listado_y_detalle_de_libros_siguen_publicos(self):
        cliente_anonimo = Client()

        self.assertEqual(cliente_anonimo.get(reverse("libro_listar")).status_code, 200)
        self.assertEqual(
            cliente_anonimo.get(reverse("libro_detalle", args=[self.libro.pk])).status_code,
            200,
        )

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
