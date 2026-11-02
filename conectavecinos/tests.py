from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import (
    Apoyo, Asignacion, Categoria, Comunidad, EstadoIncidencia, Evaluacion,
    Incidencia, Municipalidad, Notificacion, Prioridad, Rol, UnidadMunicipal, UsuarioRol,
)


class ModeloVecinalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(username="vecino")
        cls.municipalidad = Municipalidad.objects.create(nombre="Municipalidad", comuna="Santiago", region="Metropolitana")
        cls.comunidad = Comunidad.objects.create(nombre="Los Aromos", municipalidad=cls.municipalidad)
        cls.categoria = Categoria.objects.create(nombre="Iluminación")
        cls.prioridad = Prioridad.objects.create(nombre="Grave", nivel=3)
        cls.recibida = EstadoIncidencia.objects.create(nombre="Recibida", codigo="recibida")
        cls.resuelta = EstadoIncidencia.objects.create(nombre="Resuelta", codigo="resuelta", es_final=True)

    def incidencia(self, **cambios):
        datos = dict(autor=self.usuario, comunidad=self.comunidad, categoria=self.categoria,
                     prioridad=self.prioridad, estado=self.recibida, titulo="Luminarias apagadas",
                     descripcion="Cinco luminarias sin funcionar", ubicacion_referencia="Plaza central")
        datos.update(cambios)
        return Incidencia.objects.create(**datos)

    def test_codigos_unicos_y_privacidad_inicial(self):
        primera, segunda = self.incidencia(), self.incidencia()
        self.assertNotEqual(primera.codigo, segunda.codigo)
        self.assertEqual(primera.visibilidad, "restringida")

    def test_cambio_estado_historial_notificacion_y_reapertura(self):
        incidencia = self.incidencia()
        seguimiento = incidencia.cambiar_estado(self.resuelta, self.usuario, "Reparación completada")
        incidencia.refresh_from_db()
        self.assertEqual(incidencia.estado, self.resuelta)
        self.assertIsNotNone(incidencia.cerrada_en)
        self.assertEqual(seguimiento.estado_anterior, self.recibida)
        self.assertEqual(Notificacion.objects.get().usuario, self.usuario)
        incidencia.cambiar_estado(self.recibida, self.usuario, "El problema persiste")
        incidencia.refresh_from_db()
        self.assertIsNone(incidencia.cerrada_en)
        self.assertEqual(incidencia.seguimientos.count(), 2)

    def test_cambio_sin_motivo_no_modifica_estado(self):
        incidencia = self.incidencia()
        with self.assertRaises(ValidationError):
            incidencia.cambiar_estado(self.resuelta, self.usuario, " ")
        incidencia.refresh_from_db()
        self.assertEqual(incidencia.estado, self.recibida)
        self.assertFalse(incidencia.seguimientos.exists())

    def test_apoyo_unico_en_base_de_datos(self):
        incidencia = self.incidencia()
        Apoyo.objects.create(incidencia=incidencia, usuario=self.usuario)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Apoyo.objects.create(incidencia=incidencia, usuario=self.usuario)

    def test_coordenadas_completas_en_base_de_datos(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.incidencia(latitud=-33)

    def test_ciclo_duplicadas_invalido(self):
        primera = self.incidencia()
        segunda = self.incidencia(duplicada_de=primera)
        primera.duplicada_de = segunda
        with self.assertRaises(ValidationError):
            primera.full_clean()

    def test_organizaciones_deben_coincidir(self):
        otra = Municipalidad.objects.create(nombre="Otra", comuna="Otra", region="Otra")
        unidad = UnidadMunicipal.objects.create(nombre="Obras", municipalidad=otra)
        asignacion = Asignacion(incidencia=self.incidencia(), unidad=unidad, asignada_por=self.usuario)
        with self.assertRaises(ValidationError):
            asignacion.full_clean()
        rol = Rol.objects.create(nombre="Gestor")
        with self.assertRaises(ValidationError):
            UsuarioRol(usuario=self.usuario, rol=rol, municipalidad=otra, comunidad=self.comunidad).full_clean()

    def test_evaluacion_requiere_finalizacion_y_puntuacion_valida(self):
        incidencia = self.incidencia()
        evaluacion = Evaluacion(incidencia=incidencia, usuario=self.usuario, puntuacion=5)
        with self.assertRaises(ValidationError):
            evaluacion.full_clean()
        incidencia.cambiar_estado(self.resuelta, self.usuario, "Solucionada")
        evaluacion.full_clean()
        evaluacion.save()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Evaluacion.objects.create(incidencia=incidencia, usuario=self.usuario, puntuacion=0)
