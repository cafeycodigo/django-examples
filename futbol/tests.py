from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from futbol.models import Club, Jugador, Campeonato, Partido, Incidencia


class FutbolModelTestCase(TestCase):
    def setUp(self):
        self.club_local = Club.objects.create(
            nombre="Colo-Colo",
            nombre_corto="CC",
            ciudad="Santiago",
            estadio="Monumental",
            division="primera",
        )
        self.club_visita = Club.objects.create(
            nombre="Universidad de Chile",
            nombre_corto="UCH",
            ciudad="Santiago",
            estadio="Nacional",
            division="primera",
        )
        self.campeonato = Campeonato.objects.create(
            nombre="Campeonato Nacional 2026",
            division="primera",
            temporada=2026,
            fecha_inicio="2026-02-01",
            fecha_fin="2026-11-30",
        )
        self.jugador = Jugador.objects.create(
            rut="12345678-5",
            nombre_completo="Carlos Palacios",
            club=self.club_local,
            posicion="delantero",
            dorsal=7,
        )
        self.partido_goleada = Partido.objects.create(
            campeonato=self.campeonato,
            jornada=1,
            club_local=self.club_local,
            club_visita=self.club_visita,
            fecha_partido=timezone.now(),
            estadio="Monumental",
            goles_local=4,
            goles_visita=1,
            publico_asistente=40000,
        )

    def test_club_division(self):
        self.assertTrue(self.club_local.es_primera)
        self.assertEqual(self.club_local.nombre_corto, "CC")

    def test_partido_goleada_property(self):
        self.assertEqual(self.partido_goleada.total_goles, 5)
        self.assertTrue(self.partido_goleada.es_goleada)
        self.assertEqual(self.partido_goleada.resultado, "gana_local")

    def test_incidencia_lesion_y_amarilla(self):
        amarilla = Incidencia.objects.create(
            partido=self.partido_goleada,
            jugador=self.jugador,
            club=self.club_local,
            tipo="tarjeta_amarilla",
            minuto=32,
            detalle="Falta táctica",
        )
        lesion = Incidencia.objects.create(
            partido=self.partido_goleada,
            jugador=self.jugador,
            club=self.club_local,
            tipo="lesion",
            minuto=75,
            detalle="Desgarro isquiotibial",
            gravedad_lesion="moderada",
        )
        self.assertEqual(amarilla.tipo, "tarjeta_amarilla")
        self.assertEqual(lesion.gravedad_lesion, "moderada")


class FutbolViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.club1 = Club.objects.create(nombre="Everton", nombre_corto="EVE", ciudad="Viña del Mar", estadio="Sausalito", division="primera")
        self.club2 = Club.objects.create(nombre="Santiago Wanderers", nombre_corto="SW", ciudad="Valparaíso", estadio="Elías Figueroa", division="primera_b")
        self.camp = Campeonato.objects.create(nombre="Torneo 2026", division="primera", temporada=2026, fecha_inicio="2026-02-01", fecha_fin="2026-11-30")
        self.jug1 = Jugador.objects.create(rut="11111111-1", nombre_completo="Lucas Assadi", club=self.club1, posicion="mediocampista", dorsal=10)
        self.partido = Partido.objects.create(
            campeonato=self.camp,
            jornada=1,
            club_local=self.club1,
            club_visita=self.club2,
            fecha_partido=timezone.now(),
            estadio="Sausalito",
            goles_local=3,
            goles_visita=0,
            publico_asistente=12000,
        )
        Incidencia.objects.create(partido=self.partido, jugador=self.jug1, club=self.club1, tipo="gol", minuto=14, detalle="Gol de jugada")
        Incidencia.objects.create(partido=self.partido, jugador=self.jug1, club=self.club1, tipo="tarjeta_amarilla", minuto=40, detalle="Reclamos")
        Incidencia.objects.create(partido=self.partido, jugador=self.jug1, club=self.club1, tipo="lesion", minuto=65, detalle="Contractura aductor", gravedad_lesion="leve")

    def test_index_view(self):
        response = self.client.get(reverse("futbol:index"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("menu_lecciones_orm", data)

    def test_select_all_view(self):
        response = self.client.get(reverse("futbol:orm_select_all"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["leccion"], "Paso 1: SELECT *")
        self.assertGreaterEqual(len(data["partidos"]), 1)

    def test_where_view(self):
        response = self.client.get(reverse("futbol:orm_where"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["leccion"], "Paso 2: Cláusula WHERE con .filter()")

    def test_order_by_view(self):
        response = self.client.get(reverse("futbol:orm_order_by"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["leccion"], "Paso 3: ORDER BY con .order_by()")

    def test_join_view(self):
        response = self.client.get(reverse("futbol:orm_join"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["leccion"], "Paso 4: JOIN con .select_related() y .prefetch_related()")

    def test_agregaciones_view(self):
        response = self.client.get(reverse("futbol:orm_agregaciones"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["leccion"], "Paso 5: Agregaciones (COUNT, SUM, AVG, MIN, MAX)")

    def test_goleadas_view(self):
        response = self.client.get(reverse("futbol:orm_goleadas"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("partidos_goleados", data)

    def test_lesionados_view(self):
        response = self.client.get(reverse("futbol:orm_lesionados"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("lesionados_detallados", data)

    def test_sancionados_view(self):
        response = self.client.get(reverse("futbol:orm_sancionados"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("jugadores_con_tarjetas_amarillas", data)

    def test_goleadores_view(self):
        response = self.client.get(reverse("futbol:orm_goleadores"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("ranking_goleadores", data)

    def test_tabla_posiciones_view(self):
        response = self.client.get(reverse("futbol:orm_tabla_posiciones"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("tabla_posiciones", data)
