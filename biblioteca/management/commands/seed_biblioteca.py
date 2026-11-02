from datetime import timedelta
import random
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from biblioteca.models import Libro, Ejemplar, Usuario, Prestamo, Multa


class Command(BaseCommand):
    help = "Crea o actualiza datos de prueba para la app biblioteca usando Faker"

    def add_arguments(self, parser):
        parser.add_argument(
            "--usuarios",
            type=int,
            default=60,
            help="Cantidad de usuarios a generar (por defecto: 60)",
        )
        parser.add_argument(
            "--libros",
            type=int,
            default=80,
            help="Cantidad de libros a generar (por defecto: 80)",
        )
        parser.add_argument(
            "--ejemplares",
            type=int,
            default=150,
            help="Cantidad de ejemplares físicos a generar (por defecto: 150)",
        )
        parser.add_argument(
            "--prestamos",
            type=int,
            default=100,
            help="Cantidad de préstamos a generar (por defecto: 100)",
        )

    def handle(self, *args, **options):
        fake = Faker("es_CL")
        fake.seed_instance(42)
        random.seed(42)
        User = get_user_model()

        cant_usuarios = options["usuarios"]
        cant_libros = options["libros"]
        cant_ejemplares = options["ejemplares"]
        cant_prestamos = options["prestamos"]

        self.stdout.write(self.style.NOTICE("Iniciando seeder de biblioteca..."))

        # 1. Crear Usuarios de auth con correo institucional y perfil biblioteca
        carreras = [
            "Ingeniería Civil Informática",
            "Derecho",
            "Medicina",
            "Psicología",
            "Arquitectura",
            "Enfermería",
            "Contador Auditor",
            "Pedagogía en Historia",
            "Diseño Gráfico",
            "Ingeniería Comercial",
        ]
        dominios_institucionales = ["instituto.edu", "universidad.cl", "campus.edu.cl"]

        usuarios_creados = 0
        usuarios_actualizados = 0
        lista_auth_users = []

        for _ in range(cant_usuarios):
            rut_base = fake.unique.random_int(min=10_000_000, max=25_000_000)
            rut = self._rut_con_digito_verificador(rut_base)
            first_name = fake.first_name()
            last_name = fake.last_name()
            nombre_completo = f"{first_name} {last_name}"
            
            # Generar correo institucional basado en el nombre y dominio institucional
            dominio = fake.random_element(elements=dominios_institucionales)
            sufijo_num = fake.random_int(min=1, max=999)
            email_inst = f"{first_name.lower()}.{last_name.lower()}{sufijo_num}@{dominio}"
            username = f"{first_name.lower()[:3]}{last_name.lower()[:5]}{sufijo_num}"

            # Crear o actualizar en auth User
            auth_user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email_inst,
                    "is_active": True,
                }
            )

            defaults = {
                "user": auth_user,
                "nombre_completo": nombre_completo,
                "email_institucional": email_inst,
                "carrera_o_departamento": fake.random_element(elements=carreras),
                "activo": True,
            }

            usuario_obj, creado = Usuario.objects.update_or_create(
                rut=rut,
                defaults=defaults,
            )
            if creado:
                usuarios_creados += 1
            else:
                usuarios_actualizados += 1
            lista_auth_users.append(auth_user)

        # 2. Crear Libros
        editoriales = [
            "Planeta", "Penguin Random House", "Anagrama", "Fondo de Cultura Económica",
            "Alfaguara", "Siglo XXI", "Ediciones UC", "LOM Ediciones", "Norma", "Alianza Editorial"
        ]

        libros_creados = 0
        libros_actualizados = 0
        lista_libros = []

        for _ in range(cant_libros):
            isbn = fake.unique.numerify(text="978##########")
            titulo = fake.sentence(nb_words=fake.random_int(min=2, max=6)).rstrip(".")[:120].title()
            autor = fake.name()[:100]
            editorial = fake.random_element(elements=editoriales)
            anio = fake.random_int(min=1970, max=2025)

            libro, creado = Libro.objects.update_or_create(
                isbn=isbn,
                defaults={
                    "titulo": titulo,
                    "autor": autor,
                    "editorial": editorial,
                    "anio_publicacion": anio,
                },
            )
            if creado:
                libros_creados += 1
            else:
                libros_actualizados += 1
            lista_libros.append(libro)

        # 3. Crear Ejemplares
        ejemplares_creados = 0
        ejemplares_actualizados = 0
        lista_ejemplares = []

        for num in range(cant_ejemplares):
            codigo_barra = f"BIB-{num + 1:06d}"
            libro_elegido = fake.random_element(elements=lista_libros)
            estante = fake.random_int(min=1, max=30)
            pasillo = fake.random_element(elements=["A", "B", "C", "D", "E"])
            ubicacion = f"Pasillo {pasillo} - Estante {estante}"
            fecha_adq = fake.date_between(start_date="-4y", end_date="today")

            ejemplar, creado = Ejemplar.objects.update_or_create(
                codigo_barra=codigo_barra,
                defaults={
                    "id_libro": libro_elegido,
                    "estado": "DISPONIBLE",
                    "ubicacion": ubicacion,
                    "fecha_adquisicion": fecha_adq,
                },
            )
            if creado:
                ejemplares_creados += 1
            else:
                ejemplares_actualizados += 1
            lista_ejemplares.append(ejemplar)

        # 4. Crear Préstamos y Multas
        prestamos_creados = 0
        multas_creadas = 0

        # Para préstamos, tomamos una muestra de ejemplares
        ejemplares_para_prestamo = lista_ejemplares[:cant_prestamos]

        for i, ejemplar in enumerate(ejemplares_para_prestamo):
            usuario_elegido = fake.random_element(elements=lista_auth_users)
            fecha_prestamo = fake.date_between(start_date="-1y", end_date="-5d")
            dias_pactados = fake.random_element(elements=[7, 14, 21])
            fecha_pactada = fecha_prestamo + timedelta(days=dias_pactados)

            # Simulamos si ya fue devuelto o sigue activo
            # 70% devuelto, 30% activo
            fue_devuelto = (i % 10) < 7

            if fue_devuelto:
                # Algunos devueltos a tiempo, otros con retraso
                hubo_retraso = (i % 3 == 0)
                if hubo_retraso:
                    dias_retraso = fake.random_int(min=1, max=15)
                    fecha_real = fecha_pactada + timedelta(days=dias_retraso)
                else:
                    dias_retraso = 0
                    fecha_real = fecha_prestamo + timedelta(days=fake.random_int(min=1, max=dias_pactados))
                estado_prestamo = "DEVUELTO"
                ejemplar.estado = "DISPONIBLE"
            else:
                fecha_real = None
                estado_prestamo = "ACTIVO"
                ejemplar.estado = "PRESTADO"
                dias_retraso = 0

            ejemplar.save()

            prestamo, creado = Prestamo.objects.get_or_create(
                id_ejemplar=ejemplar,
                usuario=usuario_elegido,
                fecha_prestamo=fecha_prestamo,
                defaults={
                    "fecha_devolucion_pactada": fecha_pactada,
                    "fecha_devolucion_real": fecha_real,
                    "estado": estado_prestamo,
                },
            )

            if creado:
                prestamos_creados += 1

                # Si hubo retraso en la devolución o está activo y ya pasó la fecha pactada, crear multa
                if fue_devuelto and dias_retraso > 0:
                    monto = dias_retraso * 1000  # $1.000 por día
                    Multa.objects.get_or_create(
                        id_prestamo=prestamo,
                        defaults={
                            "dias_retraso": dias_retraso,
                            "monto_multa": monto,
                            "pagada": fake.boolean(chance_of_getting_true=60),
                            "motivo": f"Devolución con {dias_retraso} días de retraso",
                        },
                    )
                    multas_creadas += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeder de biblioteca completado con éxito:\n"
                f" - Usuarios: {usuarios_creados} creados, {usuarios_actualizados} actualizados\n"
                f" - Libros: {libros_creados} creados, {libros_actualizados} actualizados\n"
                f" - Ejemplares: {ejemplares_creados} creados, {ejemplares_actualizados} actualizados\n"
                f" - Préstamos: {prestamos_creados} creados\n"
                f" - Multas: {multas_creadas} creadas"
            )
        )

    @staticmethod
    def _rut_con_digito_verificador(numero):
        suma = 0
        multiplicador = 2
        for digito in reversed(str(numero)):
            suma += int(digito) * multiplicador
            multiplicador = 2 if multiplicador == 7 else multiplicador + 1

        digito_verificador = 11 - suma % 11
        if digito_verificador == 11:
            digito_verificador = "0"
        elif digito_verificador == 10:
            digito_verificador = "K"

        return f"{numero}-{digito_verificador}"
