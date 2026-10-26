import random
import time
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from eventos.models import Categoria, Persona, Evento, Asistencia


class Command(BaseCommand):
    help = "Genera más de 500 eventos con categorías, valores (incluyendo gratuitos) y 30,000 personas diferentes asistentes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Elimina los datos previos de la app eventos antes de sembrar.",
        )
        parser.add_argument(
            "--eventos",
            type=int,
            default=520,
            help="Cantidad de eventos a generar (por defecto: 520).",
        )
        parser.add_argument(
            "--personas",
            type=int,
            default=30000,
            help="Cantidad de personas diferentes que asisten a los eventos (por defecto: 30000).",
        )

    def handle(self, *args, **options):
        start_time = time.time()
        reset = options["reset"]
        total_eventos = max(options["eventos"], 501)
        total_personas = max(options["personas"], 30000)

        self.stdout.write(self.style.MIGRATE_HEADING("=== SEEDER DE LA APLICACIÓN EVENTOS ==="))
        self.stdout.write(f"Configuración: {total_eventos} eventos, {total_personas} personas asistentes.")

        if reset:
            self.stdout.write("Limpiando datos existentes de la aplicación eventos...")
            with transaction.atomic():
                Asistencia.objects.all().delete()
                Evento.objects.all().delete()
                Persona.objects.all().delete()
                Categoria.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Datos previos eliminados exitosamente."))

        # 1. Crear Categorías
        self.stdout.write("1. Creando categorías temáticas...")
        categorias_data = [
            ("Tecnología & IA", "Congresos, bootcamps y cumbres sobre inteligencia artificial, programación y cloud.", "#6366f1", "bi-cpu"),
            ("Música & Conciertos", "Festivales en vivo, recitales, jazz, rock y música clásica.", "#ec4899", "bi-music-note-beamed"),
            ("Negocios & Emprendimiento", "Ruedas de negocios, networking, startups e inversión ángel.", "#f59e0b", "bi-briefcase"),
            ("Diseño & Creatividad", "Workshops de UX/UI, animación digital, branding y diseño industrial.", "#8b5cf6", "bi-palette"),
            ("Gastronomía & Vinos", "Degustaciones, ferias culinarias, catas de vino y masterclasses de chefs.", "#ef4444", "bi-cup-hot"),
            ("Salud & Bienestar", "Jornadas de medicina preventiva, yoga, mindfulness y salud mental.", "#10b981", "bi-heart-pulse"),
            ("Ciencia & Innovación", "Simposios astronómicos, biotecnología, robótica y física aplicada.", "#06b6d4", "bi-lightbulb"),
            ("Cultura & Teatro", "Obras teatrales, exposiciones de museos, literatura y poesía.", "#d946ef", "bi-mask"),
            ("Educación & Talleres", "Capacitaciones docentes, e-learning y talleres prácticos certificados.", "#3b82f6", "bi-book"),
            ("Deportes & Fitness", "Maratones, torneos de crossfit, campeonatos de fútbol y ciclismo.", "#14b8a6", "bi-trophy"),
            ("Medio Ambiente & Sostenibilidad", "Cumbres climáticas, energías renovables, reciclaje y biodiversidad.", "#84cc16", "bi-tree"),
            ("Cine & Fotografía", "Festivales de cortometrajes, proyecciones independientes y clínicas de fotografía.", "#f97316", "bi-camera-reels"),
        ]

        categorias_map = {}
        for nombre, descripcion, color, icono in categorias_data:
            cat, _ = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={"descripcion": descripcion, "color": color, "icono": icono},
            )
            categorias_map[nombre] = cat

        categorias_list = list(categorias_map.values())
        self.stdout.write(self.style.SUCCESS(f"-> {len(categorias_list)} categorías listas."))

        # 2. Generar Eventos (> 500)
        self.stdout.write(f"2. Generando {total_eventos} eventos...")
        fake = Faker("es_CL")
        Faker.seed(12345)
        random.seed(12345)

        prefijos_titulos = [
            "Cumbre Internacional de", "Congreso Anual de", "Festival Nacional de",
            "Masterclass Avanzada:", "Simposio Latinoamericano de", "Expo & Feria de",
            "Encuentro Global de", "Workshop Práctico de", "Jornadas Universitarias de",
            "Foro Abierto de", "Torneo y Competencia de", "Seminario Estratégico de",
            "Ciclo Exclusivo de", "Conferencia Magistral de", "Hackathon & Challenge de",
        ]

        subtemas_por_categoria = {
            "Tecnología & IA": ["Inteligencia Artificial Generativa", "Python & Django Moderno", "Ciberseguridad Ofensiva", "Cloud Native & DevOps", "Big Data y Analítica", "Blockchain y Web3", "Arquitectura de Microservicios"],
            "Música & Conciertos": ["Rock Progresivo", "Jazz & Blues Fusion", "Música Electrónica Underground", "Orquestas Filarmónicas", "Indie Pop Latino", "Canto Lírico", "Festival Sonoro Urbano"],
            "Negocios & Emprendimiento": ["Venture Capital & Rondas Serie A", "Scaleups y Expansión Global", "Marketing Digital & Growth", "Fintech y Pagos Digitales", "E-Commerce de Alto Rendimiento", "Liderazgo y Gestión de Equipos"],
            "Diseño & Creatividad": ["Design Systems a Gran Escala", "Diseño de Experiencia de Usuario UX", "Tipografía Editorial y Caligrafía", "Modelado 3D y VFX", "Branding Estratégico", "Diseño Sostenible"],
            "Gastronomía & Vinos": ["Alta Cocina Molecular", "Ruta de Vinos Tintos del Valle", "Pastelería Francesa Artesanal", "Maridaje y Coctelería de Autor", "Cocina Patrimonial y de Origen", "Cafetería de Especialidad"],
            "Salud & Bienestar": ["Medicina de Vanguardia", "Mindfulness y Manejo del Estrés", "Nutrición Deportiva y Rendimiento", "Salud Mental Comunitaria", "Yoga Restaurativo y Respiración", "Neurociencias Aplicadas"],
            "Ciencia & Innovación": ["Exploración Espacial y Satélites", "Biotecnología y Genómica", "Energía Solar y Baterías de Litio", "Nanomateriales y Grafeno", "Inteligencia Cuántica", "Oceanografía y Cambio Climático"],
            "Cultura & Teatro": ["Teatro Clásico Contemporáneo", "Poesía y Narrativa Latinoamericana", "Exposición de Arte Abstracto", "Festival de Dramaturgia Emergente", "Historia y Patrimonio Urbano", "Escultura y Cerámica Viva"],
            "Educación & Talleres": ["Metodologías Ágiles en Aula", "Pedagogía Digital y STEM", "Gamificación en el Aprendizaje", "Inclusión Educativa y Neurodiversidad", "Educación Financiera para Jóvenes", "Liderazgo Docente"],
            "Deportes & Fitness": ["Maratón y Resistencia Urbana", "Campeonato de Trail Running", "Crossfit y Acondicionamiento Físico", "Torneo Abierto de Pádel", "Calistenia y Fuerza Funcional", "Natación y Aguas Abiertas"],
            "Medio Ambiente & Sostenibilidad": ["Economía Circular y Residuo Cero", "Reforestación y Conservación de Bosques", "Gestión Eficiente del Agua", "Transición Energética Limpia", "Ciudades Verdes e Inteligentes", "Agricultura Regenerativa"],
            "Cine & Fotografía": ["Dirección de Fotografía Cinematográfica", "Festival de Cine Documental", "Fotoperiodismo y Realidad Social", "Guionismo para Series y Streaming", "Fotografía Nocturna y Astrofotografía", "Edición y Colorimetría Digital"],
        }

        lugares_presenciales = [
            "Centro Cultural La Moneda, Santiago",
            "Espacio Riesco, Pabellón Central",
            "Teatro Municipal de Las Condes",
            "Parque de las Esculturas, Providencia",
            "Auditorio Central Campus San Joaquín",
            "Centro de Convenciones CasaPiedra",
            "Teatro Caupolicán, Santiago",
            "Centro de Eventos SurActivo, Concepción",
            "Palacio Baburizza, Valparaíso",
            "Movistar Arena, Santiago",
            "Estadio Bicentenario de La Florida",
            "Centro Cultural Gabriela Mistral (GAM)",
            "Hotel W Santiago, Salón Magnolia",
            "Quinta Vergara, Viña del Mar",
            "Parque Bicentenario de Vitacura",
        ]

        valores_pagados = [
            5000, 8000, 10000, 15000, 20000, 25000, 35000, 45000, 50000,
            65000, 80000, 95000, 120000, 150000,
        ]

        ahora = timezone.now()
        eventos_a_crear = []

        for i in range(total_eventos):
            cat = categorias_list[i % len(categorias_list)]
            subtemas = subtemas_por_categoria.get(cat.nombre, ["General"])
            prefijo = random.choice(prefijos_titulos)
            subtema = random.choice(subtemas)
            numero_edicion = (i // len(categorias_list)) + 1
            titulo = f"{prefijo} {subtema} (Edición #{numero_edicion})"

            # ~35% de los eventos serán GRATUITOS (Free), el resto con valor monetario
            es_gratis = (i % 3 == 0) or (random.random() < 0.25)
            if es_gratis:
                valor = 0.00
            else:
                valor = float(random.choice(valores_pagados))

            es_online = random.random() < 0.35
            ubicacion = "Plataforma Virtual Streaming HD / Zoom" if es_online else random.choice(lugares_presenciales)

            # Fechas distribuidas en los últimos 18 meses hasta los próximos 4 meses
            dias_desplazamiento = random.randint(-400, 90)
            fecha_inicio = ahora + timedelta(days=dias_desplazamiento, hours=random.randint(9, 20), minutes=random.choice([0, 15, 30, 45]))
            fecha_fin = fecha_inicio + timedelta(hours=random.randint(2, 8))

            if fecha_inicio < ahora:
                estado = "finalizado"
            elif fecha_inicio <= ahora <= fecha_fin:
                estado = "en_curso"
            else:
                estado = "cancelado" if random.random() < 0.03 else "programado"

            capacidad = random.choice([80, 150, 250, 500, 1000, 2500, 5000])
            organizador = f"Asociación de {cat.nombre} & Producciones Global"

            descripcion = (
                f"Participa en el evento más destacado de {cat.nombre}: '{titulo}'. "
                f"Contaremos con expositores líderes del sector, sesiones interactivas, espacios de networking y material exclusivo. "
                f"Modalidad {'100% online y en vivo' if es_online else 'presencial con cupos limitados'}."
            )

            evento = Evento(
                titulo=titulo,
                descripcion=descripcion,
                categoria=cat,
                valor=valor,
                es_gratuito=es_gratis,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                ubicacion=ubicacion,
                es_online=es_online,
                capacidad_maxima=capacidad,
                organizador=organizador,
                estado=estado,
            )
            eventos_a_crear.append(evento)

        with transaction.atomic():
            eventos_creados = Evento.objects.bulk_create(eventos_a_crear, batch_size=500)

        # Recuperamos los eventos con sus IDs creados
        eventos_db = list(Evento.objects.order_by("id"))
        conteo_free = sum(1 for e in eventos_db if e.es_free)
        conteo_pagos = len(eventos_db) - conteo_free
        self.stdout.write(self.style.SUCCESS(
            f"-> {len(eventos_db)} eventos creados exitosamente "
            f"({conteo_free} eventos Free/Gratis, {conteo_pagos} eventos Pagados)."
        ))

        # 3. Generar 30,000 Personas Únicas
        self.stdout.write(f"3. Generando {total_personas} personas asistentes únicas...")

        nombres_pila = [
            "Alejandro", "Camila", "Sebastián", "Valentina", "Matías", "Constanza",
            "Nicolás", "Javiera", "Felipe", "Daniela", "Cristóbal", "Catalina",
            "Benjamín", "Francisca", "Ignacio", "Fernanda", "Diego", "Sofía",
            "Tomás", "Isidora", "Lucas", "Martina", "Joaquín", "Antonia",
            "Rodrigo", "Paula", "Gonzalo", "Carolina", "Andrés", "Macarena",
            "Gabriel", "Paulina", "Maximiliano", "Victoria", "Esteban", "Montserrat",
            "Álvaro", "Bárbara", "Emilio", "Florencia", "Patricio", "Trinidad",
            "Guillermo", "Esperanza", "Eduardo", "Clara", "Vicente", "Rocío",
            "Claudio", "Julieta", "Hernán", "Agustina", "Manuel", "Renata",
        ]

        apellidos = [
            "González", "Muñoz", "Rojas", "Díaz", "Pérez", "Soto", "Contreras",
            "Silva", "Martínez", "Sepúlveda", "Morales", "Rodríguez", "López",
            "Fuentes", "Hernández", "Torres", "Araya", "Flores", "Espinoza",
            "Valenzuela", "Castillo", "Tapia", "Reyes", "Gutiérrez", "Castro",
            "Pizarro", "Álvarez", "Vásquez", "Sánchez", "Fernández", "Carrasco",
            "Gómez", "Cortés", "Herrera", "Núñez", "Jara", "Vergara", "Rivera",
            "Figueroa", "Miranda", "Bravo", "Molina", "Vega", "Campos", "Sandoval",
            "Cárdenas", "Zúñiga", "Paredes", "Salazar", "Guzmán", "Paz", "Orellana",
        ]

        ciudades = [
            "Santiago", "Valparaíso", "Concepción", "La Serena", "Antofagasta",
            "Temuco", "Rancagua", "Talca", "Puerto Montt", "Arica", "Iquique",
            "Chillán", "Valdivia", "Copiapó", "Punta Arenas", "Viña del Mar",
        ]

        dominios_email = ["gmail.com", "outlook.com", "yahoo.com", "hotmail.com", "empresa.cl", "universidad.cl"]

        personas_a_crear = []
        rut_base_inicio = 11_000_000

        # Para asegurar velocidad óptima y 100% de unicidad en RUT y email:
        for idx in range(total_personas):
            rut_num = rut_base_inicio + idx
            rut_str = self._calcular_rut(rut_num)

            nom = nombres_pila[idx % len(nombres_pila)]
            ape1 = apellidos[(idx // len(nombres_pila)) % len(apellidos)]
            ape2 = apellidos[(idx * 7) % len(apellidos)]
            nombre_completo = f"{nom} {ape1} {ape2}"

            # Email único combinando nombre y un hash / índice
            nom_clean = nom.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
            ape_clean = ape1.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
            dominio = dominios_email[idx % len(dominios_email)]
            email = f"{nom_clean}.{ape_clean}.{idx + 1000}@{dominio}"

            telefono = f"+569{random.randint(10000000, 99999999)}"
            ciudad = ciudades[idx % len(ciudades)]

            persona = Persona(
                rut=rut_str,
                nombre_completo=nombre_completo,
                email=email,
                telefono=telefono,
                ciudad=ciudad,
            )
            personas_a_crear.append(persona)

        self.stdout.write("Insertando las 30,000 personas en lotes optimizados...")
        with transaction.atomic():
            Persona.objects.bulk_create(personas_a_crear, batch_size=3000)

        personas_db = list(Persona.objects.order_by("id"))
        self.stdout.write(self.style.SUCCESS(f"-> {len(personas_db)} personas creadas exitosamente."))

        # 4. Generar Asistencias vinculando las 30,000 personas a los eventos
        # Regla esencial: "30000 personas diferentes que han asistido a estos eventos"
        # Para cumplir al 100%: CADA UNA de las 30,000 personas debe tener al menos 1 asistencia (asistio=True) a un evento.
        # Además, muchas personas asisten a 2 o más eventos (para un total de ~50,000 asistencias).
        self.stdout.write("4. Vinculando asistencias de las 30,000 personas a los eventos...")

        asistencias_a_crear = []
        pares_unicos = set()
        num_eventos = len(eventos_db)

        # Paso A: Asistencia garantizada para CADA persona (30,000 asistencias)
        for idx, persona in enumerate(personas_db):
            # Asignamos a un evento (distribuidos equitativamente)
            evento_idx = (idx * 31 + 7) % num_eventos
            evento = eventos_db[evento_idx]
            pares_unicos.add((evento.id, persona.id))

            precio = 0.00 if evento.es_free else evento.valor
            asistencias_a_crear.append(
                Asistencia(
                    evento=evento,
                    persona=persona,
                    asistio=True,  # Asistió efectivamente
                    precio_pagado=precio,
                    codigo_ticket=f"TK-{evento.id:04d}-{persona.id:06d}",
                )
            )

        # Paso B: Asistencias adicionales para participantes recurrentes (ej. 20,000 asistencias más)
        personas_extra = random.sample(personas_db, k=min(20000, len(personas_db)))
        for persona in personas_extra:
            evento = random.choice(eventos_db)
            par = (evento.id, persona.id)
            if par not in pares_unicos:
                pares_unicos.add(par)
                precio = 0.00 if evento.es_free else evento.valor
                asistencias_a_crear.append(
                    Asistencia(
                        evento=evento,
                        persona=persona,
                        asistio=True,
                        precio_pagado=precio,
                        codigo_ticket=f"TK-{evento.id:04d}-{persona.id:06d}-R",
                    )
                )

        self.stdout.write(f"Insertando {len(asistencias_a_crear)} registros de asistencia...")
        with transaction.atomic():
            Asistencia.objects.bulk_create(asistencias_a_crear, batch_size=4000)

        # 5. Validación final de requisitos
        total_eventos_count = Evento.objects.count()
        total_personas_count = Persona.objects.count()
        personas_asistentes_distintas = Asistencia.objects.filter(asistio=True).values("persona").distinct().count()
        total_asistencias_count = Asistencia.objects.count()
        eventos_free_count = Evento.objects.filter(es_gratuito=True).count()
        eventos_pago_count = Evento.objects.filter(es_gratuito=False).count()

        elapsed = time.time() - start_time

        self.stdout.write(self.style.MIGRATE_LABEL("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("[OK] SEEDER COMPLETADO CON EXITO"))
        self.stdout.write(self.style.MIGRATE_LABEL("=" * 60))
        self.stdout.write(f"- Total Eventos creados: {total_eventos_count} (Requerido: > 500)")
        self.stdout.write(f"  * Eventos Gratuitos (Free): {eventos_free_count}")
        self.stdout.write(f"  * Eventos de Pago: {eventos_pago_count}")
        self.stdout.write(f"- Total Personas creadas: {total_personas_count}")
        self.stdout.write(
            self.style.SUCCESS(
                f"- Personas diferentes con asistencia comprobada: {personas_asistentes_distintas} (Requerido: 30,000)"
            )
        )
        self.stdout.write(f"- Total registros de Asistencia: {total_asistencias_count}")
        self.stdout.write(f"- Tiempo total de ejecucion: {elapsed:.2f} segundos")
        self.stdout.write(self.style.MIGRATE_LABEL("=" * 60 + "\n"))

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
