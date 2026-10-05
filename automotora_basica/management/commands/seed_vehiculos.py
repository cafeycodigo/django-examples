from django.core.management.base import BaseCommand
from automotora_basica.models import Vehiculo
from faker import Faker
import random


class Command(BaseCommand):
    help = "Genera vehículos de prueba"

    def handle(self, *args, **kwargs):

        fake = Faker("es_CL")

        marcas = [
            "Toyota",
            "Hyundai",
            "Kia",
            "Chevrolet",
            "Nissan"
        ]

        for i in range(20):

            Vehiculo.objects.create(
                patente=fake.bothify(
                    text="????##"
                ).upper(),

                marca=random.choice(marcas),

                modelo=fake.word().capitalize(),

                anio=random.randint(
                    2000,
                    2026
                ),

                kilometraje=random.randint(
                    0,
                    200000
                ),

                combustible=random.choice([
                    "Bencina",
                    "Diesel",
                    "Híbrido",
                    "Eléctrico"
                ]),

                color=fake.color_name(),

                capacidad_pasajeros=random.choice([
                    2, 4, 5, 7
                ])
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Vehículos creados correctamente."
            )
        )