import random
import time
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from futbol.models import Club, Jugador, Campeonato, Partido, Incidencia


class Command(BaseCommand):
    help = "Genera clubes de Primera y Segunda División de Chile, planteles de jugadores, fixture de campeonatos y simulación de partidos con incidencias (goles, tarjetas, lesiones)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Elimina los datos previos de la app fútbol antes de sembrar.",
        )

    def handle(self, *args, **options):
        start_time = time.time()
        self.stdout.write(self.style.MIGRATE_HEADING("=== SEEDER: CAMPEONATOS DE FÚTBOL CHILENO ==="))

        if options["reset"]:
            self.stdout.write("Limpiando datos previos de la app fútbol...")
            with transaction.atomic():
                Incidencia.objects.all().delete()
                Partido.objects.all().delete()
                Campeonato.objects.all().delete()
                Jugador.objects.all().delete()
                Club.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Datos previos eliminados."))

        fake = Faker("es_CL")
        Faker.seed(777)
        random.seed(777)

        # 1. CLUBES DE CHILE (PRIMERA Y SEGUNDA DIVISIÓN)
        self.stdout.write("1. Creando clubes de Primera División y Primera B...")

        clubes_primera = [
            ("Colo-Colo", "CC", "Santiago", "Estadio Monumental David Arellano", 1925, "#ffffff", "#000000"),
            ("Universidad de Chile", "UCH", "Santiago", "Estadio Nacional Julio Martínez", 1927, "#0033a0", "#d52b1e"),
            ("Universidad Católica", "UC", "Santiago", "Estadio San Carlos de Apoquindo", 1937, "#ffffff", "#005baa"),
            ("Cobreloa", "COB", "Calama", "Estadio Zorros del Desierto", 1977, "#ff6600", "#ffffff"),
            ("Coquimbo Unido", "COQ", "Coquimbo", "Estadio Francisco Sánchez Rumoroso", 1958, "#facc15", "#000000"),
            ("Everton", "EVE", "Viña del Mar", "Estadio Sausalito", 1909, "#1e3a8a", "#f59e0b"),
            ("Palestino", "PAL", "Santiago", "Estadio Municipal de La Cisterna", 1920, "#15803d", "#b91c1c"),
            ("Unión Española", "UE", "Santiago", "Estadio Santa Laura-Universidad SEK", 1897, "#dc2626", "#eab308"),
            ("O'Higgins", "OHI", "Rancagua", "Estadio El Teniente", 1955, "#38bdf8", "#ffffff"),
            ("Audax Italiano", "AUD", "Santiago", "Estadio Bicentenario de La Florida", 1910, "#16a34a", "#ffffff"),
            ("Huachipato", "HUA", "Talcahuano", "Estadio CAP Acero", 1947, "#0284c7", "#000000"),
            ("Ñublense", "NUB", "Chillán", "Estadio Nelson Oyarzún Arenas", 1916, "#ef4444", "#ffffff"),
            ("Deportes Iquique", "CDI", "Iquique", "Estadio Tierra de Campeones", 1978, "#06b6d4", "#ffffff"),
            ("Cobresal", "CSL", "El Salvador", "Estadio El Cobre", 1979, "#f97316", "#ffffff"),
            ("Deportes Copiapó", "COP", "Copiapó", "Estadio Luis Valenzuela Hermosilla", 1999, "#ffffff", "#b91c1c"),
            ("Unión La Calera", "ULC", "La Calera", "Estadio Nicolás Chahuán Nazar", 1954, "#ef4444", "#ffffff"),
        ]

        clubes_segunda = [
            ("Santiago Wanderers", "SW", "Valparaíso", "Estadio Elías Figueroa Brander", 1892, "#15803d", "#ffffff"),
            ("Rangers de Talca", "RAN", "Talca", "Estadio Fiscal de Talca", 1902, "#dc2626", "#000000"),
            ("Deportes La Serena", "DLS", "La Serena", "Estadio La Portada", 1955, "#b91c1c", "#ffffff"),
            ("Magallanes", "MAG", "San Bernardo", "Estadio Municipal de San Bernardo", 1897, "#38bdf8", "#ffffff"),
            ("Curicó Unido", "CUR", "Curicó", "Estadio La Granja", 1973, "#dc2626", "#ffffff"),
            ("San Luis de Quillota", "SLQ", "Quillota", "Estadio Municipal Lucio Fariña", 1919, "#facc15", "#000000"),
            ("San Marcos de Arica", "SMA", "Arica", "Estadio Carlos Dittborn", 1978, "#0284c7", "#dc2626"),
            ("Deportes Antofagasta", "CDA", "Antofagasta", "Estadio Regional Calvo y Bascuñán", 1966, "#0284c7", "#ffffff"),
            ("Deportes Temuco", "TEM", "Temuco", "Estadio Germán Becker", 1960, "#16a34a", "#ffffff"),
            ("Universidad de Concepción", "UDC", "Concepción", "Estadio Municipal Ester Roa", 1994, "#eab308", "#0284c7"),
            ("Deportes Recoleta", "REC", "Santiago", "Estadio Leonel Sánchez Lineros", 2014, "#0284c7", "#ffffff"),
            ("Deportes Santa Cruz", "DSC", "Santa Cruz", "Estadio Joaquín Muñoz García", 1913, "#ffffff", "#000000"),
            ("Barnechea", "BAR", "Santiago", "Estadio Municipal de Lo Barnechea", 1929, "#0284c7", "#facc15"),
            ("Deportes Limache", "LIM", "Limache", "Estadio Gustavo Ocaranza", 2012, "#dc2626", "#000000"),
            ("Unión San Felipe", "USF", "San Felipe", "Estadio Municipal de San Felipe", 1956, "#ffffff", "#dc2626"),
            ("Santiago Morning", "SM", "Santiago", "Estadio Municipal de La Pintana", 1903, "#000000", "#ffffff"),
        ]

        clubes_creados = []
        for nom, sigla, ciudad, estadio, fund, c1, c2 in clubes_primera:
            club, _ = Club.objects.get_or_create(
                nombre=nom,
                defaults={
                    "nombre_corto": sigla,
                    "ciudad": ciudad,
                    "estadio": estadio,
                    "division": "primera",
                    "fundacion_anio": fund,
                    "color_primario": c1,
                    "color_secundario": c2,
                },
            )
            clubes_creados.append(club)

        for nom, sigla, ciudad, estadio, fund, c1, c2 in clubes_segunda:
            club, _ = Club.objects.get_or_create(
                nombre=nom,
                defaults={
                    "nombre_corto": sigla,
                    "ciudad": ciudad,
                    "estadio": estadio,
                    "division": "primera_b",
                    "fundacion_anio": fund,
                    "color_primario": c1,
                    "color_secundario": c2,
                },
            )
            clubes_creados.append(club)

        self.stdout.write(self.style.SUCCESS(f"-> {len(clubes_creados)} clubes creados (16 Primera División, 16 Primera B)."))

        # 2. PLANTELES DE JUGADORES (18 por club)
        self.stdout.write("2. Creando planteles de jugadores por cada club...")
        jugadores_a_crear = []
        rut_base = 15_000_000
        jugador_idx = 0

        posiciones_distribucion = (
            ["arquero"] * 2
            + ["defensa"] * 6
            + ["mediocampista"] * 6
            + ["delantero"] * 4
        )

        for club in clubes_creados:
            for dorsal_num in range(1, 19):
                jugador_idx += 1
                rut_str = self._calcular_rut(rut_base + jugador_idx)
                nombre = f"{fake.first_name_male()} {fake.last_name()} {fake.last_name()}"
                pos = posiciones_distribucion[dorsal_num - 1]
                edad = random.randint(18, 36)

                j = Jugador(
                    rut=rut_str,
                    nombre_completo=nombre,
                    club=club,
                    posicion=pos,
                    dorsal=dorsal_num,
                    nacionalidad="Chilena" if random.random() < 0.85 else random.choice(["Argentina", "Uruguaya", "Paraguaya", "Colombiana"]),
                    edad=edad,
                )
                jugadores_a_crear.append(j)

        with transaction.atomic():
            Jugador.objects.bulk_create(jugadores_a_crear, batch_size=500)

        self.stdout.write(self.style.SUCCESS(f"-> {len(jugadores_a_crear)} jugadores creados en los planteles."))

        # 3. CAMPEONATOS
        self.stdout.write("3. Creando Campeonatos de Primera División y Primera B...")
        camp_primera, _ = Campeonato.objects.get_or_create(
            nombre="Campeonato Nacional Itaú 2026 - Primera División",
            defaults={
                "division": "primera",
                "temporada": 2026,
                "fecha_inicio": timezone.now().date() - timedelta(days=90),
                "fecha_fin": timezone.now().date() + timedelta(days=90),
                "activo": True,
            },
        )

        camp_primera_b, _ = Campeonato.objects.get_or_create(
            nombre="Torneo Ascenso ACHS 2026 - Primera B",
            defaults={
                "division": "primera_b",
                "temporada": 2026,
                "fecha_inicio": timezone.now().date() - timedelta(days=90),
                "fecha_fin": timezone.now().date() + timedelta(days=90),
                "activo": True,
            },
        )

        # 4. SIMULACIÓN DE PARTIDOS Y FIXTURE
        self.stdout.write("4. Simulando partidos, resultados y goleadas...")
        partidos_a_crear = []
        fechas_torneo = 15  # 15 jornadas de liga
        ahora = timezone.now()

        def simular_division(campeonato, lista_clubes):
            n = len(lista_clubes)
            # Generar partidos round-robin simplificado
            for jornada in range(1, fechas_torneo + 1):
                random.shuffle(lista_clubes)
                for i in range(0, n, 2):
                    local = lista_clubes[i]
                    visita = lista_clubes[i + 1]

                    # Goles: probabilidad de goleadas (~20%)
                    es_goleada_forzada = random.random() < 0.22
                    if es_goleada_forzada:
                        goles_loc = random.choice([3, 4, 5])
                        goles_vis = random.choice([0, 1, 2])
                        if random.random() < 0.35:  # Goleada visitante
                            goles_loc, goles_vis = goles_vis, goles_loc
                    else:
                        goles_loc = random.choices([0, 1, 2, 3], weights=[20, 40, 25, 15])[0]
                        goles_vis = random.choices([0, 1, 2], weights=[35, 45, 20])[0]

                    dias_atras = (fechas_torneo - jornada) * 6
                    fecha_p = ahora - timedelta(days=dias_atras, hours=random.randint(12, 21), minutes=random.choice([0, 30]))
                    asistencia_pub = random.randint(3500, 41000) if local.division == "primera" else random.randint(1200, 16000)

                    partido = Partido(
                        campeonato=campeonato,
                        jornada=jornada,
                        club_local=local,
                        club_visita=visita,
                        fecha_partido=fecha_p,
                        estadio=local.estadio,
                        goles_local=goles_loc,
                        goles_visita=goles_vis,
                        publico_asistente=asistencia_pub,
                        estado="finalizado",
                    )
                    partidos_a_crear.append(partido)

        equipos_primera = [c for c in clubes_creados if c.division == "primera"]
        equipos_b = [c for c in clubes_creados if c.division == "primera_b"]

        simular_division(camp_primera, equipos_primera)
        simular_division(camp_primera_b, equipos_b)

        with transaction.atomic():
            partidos_db = Partido.objects.bulk_create(partidos_a_crear)

        partidos_totales = list(Partido.objects.select_related("club_local", "club_visita").order_by("id"))
        self.stdout.write(self.style.SUCCESS(f"-> {len(partidos_totales)} partidos simulados exitosamente."))

        # 5. GENERACIÓN DE INCIDENCIAS (GOLES, TARJETAS AMARILLAS/ROJAS, LESIONES)
        self.stdout.write("5. Generando incidencias de partidos (goleadores, amonestados y lesionados)...")

        # Mapeamos jugadores por club para selección rápida
        jugadores_por_club = {}
        for jug in Jugador.objects.all():
            jugadores_por_club.setdefault(jug.club_id, []).append(jug)

        incidencias_a_crear = []

        diagnosticos_lesiones = [
            ("Desgarro miofascial de isquiotibiales", "moderada"),
            ("Esguince de tobillo derecho grado 2", "leve"),
            ("Contractura severa en aductor izquierdo", "leve"),
            ("Rotura fibrilar de gemelo", "moderada"),
            ("Rotura de ligamento cruzado anterior (LCA)", "grave"),
            ("Fractura nasal por choque de cabezas", "moderada"),
            ("Sobrecarga muscular en cuádriceps", "leve"),
            ("Tendinopatía rotuliana aguda", "leve"),
            ("Luxación acromioclavicular de hombro", "grave"),
            ("Contusión costal severa", "leve"),
        ]

        motivos_amarillas = [
            "Falta táctica para cortar contraataque",
            "Infracción temeraria al disputar balón aéreo",
            "Reclamos airados al árbitro principal",
            "Demorar la reanudación del juego",
            "Simulación de penal en el área rival",
            "Reiteración de faltas en mediocampo",
            "Entrada a destiempo por detrás",
        ]

        motivos_rojas = [
            "Entrada con fuerza desmedida y plancha alta",
            "Conducta violenta y agresión física",
            "Doble amonestación (segunda tarjeta amarilla)",
            "Evitar ocasión manifiesta de gol con mano",
            "Insultos de gravedad al juez de línea",
        ]

        for p in partidos_totales:
            plantel_local = jugadores_por_club.get(p.club_local_id, [])
            plantel_visita = jugadores_por_club.get(p.club_visita_id, [])

            # Delanteros y medios tienen más chances de gol
            atacantes_local = [j for j in plantel_local if j.posicion in ["delantero", "mediocampista"]] or plantel_local
            atacantes_visita = [j for j in plantel_visita if j.posicion in ["delantero", "mediocampista"]] or plantel_visita

            # Goles Local
            for _ in range(p.goles_local):
                goleador = random.choice(atacantes_local)
                minuto = random.randint(1, 93)
                detalle_gol = random.choice(["Gol de jugada colectiva", "Gol de penal", "Gol de cabeza tras tiro de esquina", "Golazo de tiro libre fuera del área", "Remate de media distancia"])
                incidencias_a_crear.append(
                    Incidencia(
                        partido=p,
                        jugador=goleador,
                        club=p.club_local,
                        tipo="gol",
                        minuto=minuto,
                        detalle=detalle_gol,
                    )
                )

            # Goles Visita
            for _ in range(p.goles_visita):
                goleador = random.choice(atacantes_visita)
                minuto = random.randint(1, 93)
                detalle_gol = random.choice(["Gol de contragolpe", "Gol de penal", "Gol de cabeza", "Definición mano a mano"])
                incidencias_a_crear.append(
                    Incidencia(
                        partido=p,
                        jugador=goleador,
                        club=p.club_visita,
                        tipo="gol",
                        minuto=minuto,
                        detalle=detalle_gol,
                    )
                )

            # Tarjetas Amarillas (2 a 5 por partido)
            num_amarillas = random.randint(2, 5)
            jugadores_partido = random.sample(plantel_local + plantel_visita, k=min(num_amarillas, len(plantel_local + plantel_visita)))
            for amonestado in jugadores_partido:
                minuto = random.randint(10, 92)
                motivo = random.choice(motivos_amarillas)
                incidencias_a_crear.append(
                    Incidencia(
                        partido=p,
                        jugador=amonestado,
                        club=amonestado.club,
                        tipo="tarjeta_amarilla",
                        minuto=minuto,
                        detalle=motivo,
                    )
                )

            # Tarjetas Rojas (~1 cada 5 partidos)
            if random.random() < 0.22:
                expulsado = random.choice(plantel_local + plantel_visita)
                minuto = random.randint(35, 89)
                motivo_roja = random.choice(motivos_rojas)
                incidencias_a_crear.append(
                    Incidencia(
                        partido=p,
                        jugador=expulsado,
                        club=expulsado.club,
                        tipo="tarjeta_roja",
                        minuto=minuto,
                        detalle=motivo_roja,
                    )
                )

            # Lesiones (~1 cada 3 partidos)
            if random.random() < 0.35:
                lesionado = random.choice(plantel_local + plantel_visita)
                minuto = random.randint(8, 85)
                diag, grav = random.choice(diagnosticos_lesiones)
                incidencias_a_crear.append(
                    Incidencia(
                        partido=p,
                        jugador=lesionado,
                        club=lesionado.club,
                        tipo="lesion",
                        minuto=minuto,
                        detalle=diag,
                        gravedad_lesion=grav,
                    )
                )

        with transaction.atomic():
            Incidencia.objects.bulk_create(incidencias_a_crear, batch_size=1000)

        # 6. RESUMEN FINAL
        elapsed = time.time() - start_time
        total_partidos_cnt = Partido.objects.count()
        total_goles_cnt = Incidencia.objects.filter(tipo="gol").count()
        total_amarillas_cnt = Incidencia.objects.filter(tipo="tarjeta_amarilla").count()
        total_rojas_cnt = Incidencia.objects.filter(tipo="tarjeta_roja").count()
        total_lesiones_cnt = Incidencia.objects.filter(tipo="lesion").count()
        goleadas_cnt = len([p for p in partidos_totales if p.es_goleada])

        self.stdout.write(self.style.MIGRATE_LABEL("\n" + "=" * 65))
        self.stdout.write(self.style.SUCCESS("[OK] SEEDER DE FUTBOL COMPLETADO EXITOSAMENTE"))
        self.stdout.write(self.style.MIGRATE_LABEL("=" * 65))
        self.stdout.write(f"- Total Clubes de Chile creados: {len(clubes_creados)} (16 Primera, 16 Primera B)")
        self.stdout.write(f"- Total Jugadores en planteles: {len(jugadores_a_crear)}")
        self.stdout.write(f"- Total Partidos simulados: {total_partidos_cnt}")
        self.stdout.write(f"  * Partidos que fueron Goleadas: {goleadas_cnt}")
        self.stdout.write(f"- Total Goles anotados en los campeonatos: {total_goles_cnt}")
        self.stdout.write(f"- Total Tarjetas Amarillas mostradas: {total_amarillas_cnt}")
        self.stdout.write(f"- Total Tarjetas Rojas (Expulsiones): {total_rojas_cnt}")
        self.stdout.write(f"- Total Jugadores Lesionados durante el torneo: {total_lesiones_cnt}")
        self.stdout.write(f"- Tiempo total de ejecucion: {elapsed:.2f} segundos")
        self.stdout.write(self.style.MIGRATE_LABEL("=" * 65 + "\n"))

    @staticmethod
    def _calcular_rut(numero):
        suma = 0
        multiplicador = 2
        for digito in reversed(str(numero)):
            suma += int(digito) * multiplicador
            multiplicador = 2 if multiplicador == 7 else multiplicador + 1

        digito_verificador = 11 - (suma % 11)
        if digito_verificador == 11:
            dv = "0"
        elif digito_verificador == 10:
            dv = "K"
        else:
            dv = str(digito_verificador)

        return f"{numero}-{dv}"
