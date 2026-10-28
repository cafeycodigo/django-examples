from datetime import date
from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .models import (
    Alumno,
    Asignatura,
    Carrera,
    DetalleAsignatura,
    Docente,
    Institucion,
    Nota,
    Sede,
)


class EducacionModelTests(TestCase):
    def setUp(self):
        self.institucion = Institucion.objects.create(
            nombre="Instituto de Prueba",
            sigla="IPT",
        )
        self.sede = Sede.objects.create(
            institucion=self.institucion,
            nombre="Sede Central",
            ciudad="Santiago",
        )
        self.carrera = Carrera.objects.create(
            codigo="INF-T",
            sede=self.sede,
            nombre="Técnico en Informática",
            area="informatica",
            titulo="Técnico de Nivel Superior",
        )
        self.docente = Docente.objects.create(
            rut="15.000.000-5",
            nombres="Ana",
            apellidos="Docente",
            email="ana@prueba.cl",
            especialidad="Programación",
            sede=self.sede,
        )
        self.asignatura = Asignatura.objects.create(
            codigo="PROG-1",
            nombre="Programación I",
            area="Informática",
        )
        self.detalle = DetalleAsignatura.objects.create(
            carrera=self.carrera,
            asignatura=self.asignatura,
            docente=self.docente,
            periodo=2026,
            semestre=1,
        )
        self.alumno = Alumno.objects.create(
            rut="20.000.001-1",
            nombres="Camila",
            apellidos="Estudiante",
            email="camila@prueba.cl",
            comuna="Santiago",
            fecha_nacimiento=date(2004, 5, 12),
            carrera=self.carrera,
            cohorte=2026,
        )

    def test_nota_se_relaciona_con_alumno_y_detalle(self):
        nota = Nota.objects.create(
            alumno=self.alumno,
            detalle_asignatura=self.detalle,
            evaluacion="control_1",
            valor=Decimal("6.2"),
            fecha=date(2026, 4, 10),
        )
        self.assertEqual(self.alumno.notas.get(), nota)
        self.assertEqual(self.detalle.notas.get(), nota)

    def test_nota_fuera_de_escala_es_rechazada_por_base_de_datos(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Nota.objects.create(
                alumno=self.alumno,
                detalle_asignatura=self.detalle,
                evaluacion="control_1",
                valor=Decimal("7.1"),
                fecha=date(2026, 4, 10),
            )


class EducacionViewsTests(TestCase):
    def setUp(self):
        self.institucion = Institucion.objects.create(
            nombre="Instituto Demo",
            sigla="ID",
        )
        self.sede = Sede.objects.create(
            institucion=self.institucion,
            nombre="Sede Centro",
            ciudad="Santiago",
        )
        self.carrera = Carrera.objects.create(
            codigo="INF-1",
            sede=self.sede,
            nombre="Ingeniería en Informática",
            area="informatica",
            titulo="Ingeniero en Informática",
        )

    def test_dashboard_muestra_totales_y_enlaces(self):
        response = self.client.get(reverse("educacion:index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["totales"]["carreras"], 1)
        self.assertIn("alumnos", response.json()["rutas"])

    def test_alumnos_rechaza_limite_invalido(self):
        response = self.client.get(reverse("educacion:alumnos"), {"limite": "muchos"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())


class SeedEducacionTests(TestCase):
    def test_seed_crea_alumnos_y_se_puede_repetir(self):
        salida = StringIO()
        call_command("seed_educacion", "--cantidad=12", "--seed=7", stdout=salida)
        self.assertEqual(Alumno.objects.count(), 12)
        self.assertGreater(Nota.objects.count(), 0)

        call_command("seed_educacion", "--cantidad=12", "--seed=7", stdout=StringIO())
        self.assertEqual(Alumno.objects.count(), 12)
