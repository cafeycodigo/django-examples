import random
from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from faker import Faker

from educacion.models import (
    Alumno,
    Asignatura,
    Carrera,
    DetalleAsignatura,
    Docente,
    Institucion,
    Nota,
    Sede,
)


INSTITUCIONES = [
    ("Instituto Profesional del Pacífico", "IPP", "Instituto profesional"),
    ("Centro de Formación Técnica Andina", "CFTA", "Centro de formación técnica"),
]

SEDES = [
    ("Sede Alameda", "Santiago"),
    ("Sede Valparaíso", "Valparaíso"),
    ("Sede Concepción", "Concepción"),
    ("Sede Temuco", "Temuco"),
]

CARRERAS = [
    ("INF-01", "Técnico en Programación y Análisis de Sistemas", "informatica", "Técnico de Nivel Superior en Programación", 5),
    ("INF-02", "Ingeniería en Informática", "informatica", "Ingeniero en Informática", 8),
    ("INF-03", "Técnico en Redes y Telecomunicaciones", "informatica", "Técnico de Nivel Superior en Redes", 5),
    ("INF-04", "Técnico en Ciberseguridad", "informatica", "Técnico de Nivel Superior en Ciberseguridad", 5),
    ("SAL-01", "Técnico en Enfermería", "salud", "Técnico de Nivel Superior en Enfermería", 5),
    ("ELE-01", "Ingeniería en Electricidad y Automatización", "electricidad", "Ingeniero en Electricidad y Automatización", 8),
    ("ADM-01", "Técnico en Administración Logística", "administracion", "Técnico de Nivel Superior en Logística", 5),
    ("CON-01", "Técnico en Construcción", "construccion", "Técnico de Nivel Superior en Construcción", 5),
]

ASIGNATURAS = [
    ("MAT-101", "Matemática Aplicada", "Formación general", 5),
    ("COM-101", "Comunicación Efectiva", "Formación general", 4),
    ("PRO-101", "Fundamentos de Programación", "Informática", 6),
    ("PRO-102", "Programación Orientada a Objetos", "Informática", 6),
    ("BDA-101", "Bases de Datos", "Informática", 5),
    ("RED-101", "Redes y Conectividad", "Informática", 5),
    ("CIB-101", "Fundamentos de Ciberseguridad", "Informática", 5),
    ("SIS-101", "Sistemas Operativos", "Informática", 5),
    ("ENF-101", "Fundamentos de Enfermería", "Salud", 6),
    ("ENF-102", "Anatomía y Fisiología", "Salud", 6),
    ("ENF-103", "Primeros Auxilios", "Salud", 5),
    ("ENF-104", "Salud Comunitaria", "Salud", 5),
    ("ELE-101", "Circuitos Eléctricos", "Electricidad", 6),
    ("ELE-102", "Instalaciones Eléctricas", "Electricidad", 6),
    ("ELE-103", "Automatización Industrial", "Electricidad", 6),
    ("ADM-101", "Gestión de Operaciones", "Administración", 5),
    ("ADM-102", "Logística y Abastecimiento", "Administración", 5),
    ("CON-101", "Materiales de Construcción", "Construcción", 5),
]

ASIGNATURAS_POR_AREA = {
    "informatica": ["PRO-101", "PRO-102", "BDA-101", "RED-101", "CIB-101", "SIS-101"],
    "salud": ["ENF-101", "ENF-102", "ENF-103", "ENF-104"],
    "electricidad": ["ELE-101", "ELE-102", "ELE-103", "MAT-101"],
    "administracion": ["ADM-101", "ADM-102", "MAT-101", "COM-101"],
    "construccion": ["CON-101", "MAT-101", "COM-101", "ADM-101"],
}

ESPECIALIDADES = {
    "informatica": "Desarrollo de software y sistemas",
    "salud": "Enfermería y atención clínica",
    "electricidad": "Electricidad y automatización",
    "administracion": "Administración y logística",
    "construccion": "Construcción y obras civiles",
}


def rut_ficticio(numero):
    cuerpo = str(numero)
    factores = (2, 3, 4, 5, 6, 7)
    suma = sum(int(digito) * factores[indice % len(factores)] for indice, digito in enumerate(reversed(cuerpo)))
    verificador = 11 - suma % 11
    digito = "0" if verificador == 11 else "K" if verificador == 10 else str(verificador)
    return f"{int(cuerpo):,}".replace(",", ".") + f"-{digito}"


class Command(BaseCommand):
    help = "Crea instituciones, carreras y datos ficticios de educación superior."

    def add_arguments(self, parser):
        parser.add_argument(
            "--cantidad",
            type=int,
            default=4500,
            help="Cantidad mínima de alumnos a crear (por defecto: 4500).",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=2026,
            help="Semilla para generar los datos ficticios.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        cantidad = options["cantidad"]
        if cantidad < 1:
            raise CommandError("--cantidad debe ser un número mayor que cero.")

        fake = Faker("es_CL")
        fake.seed_instance(options["seed"])
        rng = random.Random(options["seed"])

        instituciones = []
        for nombre, sigla, tipo in INSTITUCIONES:
            institucion, _ = Institucion.objects.get_or_create(
                sigla=sigla,
                defaults={"nombre": nombre, "tipo": tipo},
            )
            instituciones.append(institucion)

        sedes = []
        for indice, (nombre, ciudad) in enumerate(SEDES):
            institucion = instituciones[indice % len(instituciones)]
            sede, _ = Sede.objects.get_or_create(
                institucion=institucion,
                nombre=nombre,
                ciudad=ciudad,
            )
            sedes.append(sede)

        asignaturas = {}
        for codigo, nombre, area, creditos in ASIGNATURAS:
            asignatura, _ = Asignatura.objects.get_or_create(
                codigo=codigo,
                defaults={
                    "nombre": nombre,
                    "area": area,
                    "creditos": creditos,
                    "descripcion": f"Asignatura de formación en {area.lower()}.",
                },
            )
            asignaturas[codigo] = asignatura

        docentes = {}
        for indice, sede in enumerate(sedes):
            docente, _ = Docente.objects.get_or_create(
                email=f"docente{indice + 1:02d}@demo-educacion.cl",
                defaults={
                    "rut": rut_ficticio(15000000 + indice),
                    "nombres": fake.first_name(),
                    "apellidos": fake.last_name(),
                    "especialidad": ESPECIALIDADES[
                        ("informatica", "salud", "electricidad", "administracion")[indice % 4]
                    ],
                    "sede": sede,
                },
            )
            docentes[sede.id] = docente

        carreras = []
        for indice, (codigo, nombre, area, titulo, duracion) in enumerate(CARRERAS):
            sede = sedes[indice % len(sedes)]
            carrera, _ = Carrera.objects.get_or_create(
                codigo=codigo,
                defaults={
                    "sede": sede,
                    "nombre": nombre,
                    "area": area,
                    "titulo": titulo,
                    "duracion_semestres": duracion,
                    "modalidad": "presencial" if indice % 3 else "hibrida",
                },
            )
            carreras.append(carrera)

        ofertas_por_carrera = {}
        for carrera in carreras:
            codigos = ASIGNATURAS_POR_AREA[carrera.area]
            ofertas = []
            for codigo in codigos:
                oferta, _ = DetalleAsignatura.objects.get_or_create(
                    carrera=carrera,
                    asignatura=asignaturas[codigo],
                    periodo=2026,
                    semestre=1,
                    seccion="A",
                    defaults={
                        "docente": docentes[carrera.sede_id],
                        "modalidad": carrera.modalidad,
                        "cupos": 45,
                    },
                )
                ofertas.append(oferta)
            ofertas_por_carrera[carrera.id] = ofertas

        existentes = set(Alumno.objects.values_list("email", flat=True))
        nuevos_alumnos = []
        alumnos_por_correo = {}
        for indice in range(1, cantidad + 1):
            email = f"alumno{indice:05d}@estudiantes.demo.cl"
            if email in existentes:
                continue
            carrera = carreras[(indice - 1) % len(carreras)]
            alumno = Alumno(
                rut=rut_ficticio(20000000 + indice),
                nombres=fake.first_name(),
                apellidos=f"{fake.last_name()} {fake.last_name()}",
                email=email,
                telefono=fake.phone_number()[:25],
                comuna=fake.city(),
                fecha_nacimiento=fake.date_of_birth(minimum_age=18, maximum_age=45),
                carrera=carrera,
                cohorte=rng.choice([2022, 2023, 2024, 2025, 2026]),
                semestre_actual=rng.randint(1, min(carrera.duracion_semestres, 8)),
                estado="egresado" if rng.random() < 0.08 else "regular",
            )
            nuevos_alumnos.append(alumno)
            alumnos_por_correo[email] = alumno

        Alumno.objects.bulk_create(nuevos_alumnos, batch_size=500)
        if alumnos_por_correo:
            alumnos_creados = Alumno.objects.filter(
                email__in=alumnos_por_correo
            ).select_related("carrera")
        else:
            alumnos_creados = Alumno.objects.none()

        tipo_evaluaciones = [
            ("control_1", date(2026, 4, 10)),
            ("evaluacion_1", date(2026, 5, 15)),
            ("evaluacion_2", date(2026, 6, 20)),
        ]
        notas_existentes = set(
            Nota.objects.values_list("alumno_id", "detalle_asignatura_id", "evaluacion")
        )
        notas_nuevas = []
        for alumno in alumnos_creados:
            ofertas = ofertas_por_carrera[alumno.carrera_id]
            for oferta in ofertas[:3]:
                for evaluacion, fecha in tipo_evaluaciones:
                    clave = (alumno.id, oferta.id, evaluacion)
                    if clave in notas_existentes:
                        continue
                    notas_nuevas.append(
                        Nota(
                            alumno=alumno,
                            detalle_asignatura=oferta,
                            evaluacion=evaluacion,
                            valor=Decimal(rng.randint(30, 70)) / Decimal("10"),
                            fecha=fecha,
                        )
                    )

        Nota.objects.bulk_create(notas_nuevas, batch_size=1000)
        total = Alumno.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Datos listos: {total} alumnos, {Carrera.objects.count()} carreras, "
                f"{DetalleAsignatura.objects.count()} ofertas y {Nota.objects.count()} notas."
            )
        )
