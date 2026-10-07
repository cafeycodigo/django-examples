from django.core.management.base import BaseCommand
from faker import Faker

from rrhh.models import Empleado


class Command(BaseCommand):
    help = "Crea o actualiza empleados de prueba"

    def handle(self, *args, **options):
        fake = Faker("es_CL")
        fake.seed_instance(42)
        creados = 0
        actualizados = 0

        for _ in range(20):
            rut_base = fake.unique.random_int(min=10_000_000, max=25_000_000)
            rut = self._rut_con_digito_verificador(rut_base)
            defaults = {
                "nombre_completo": fake.name()[:100],
                "cargo": fake.job()[:50],
                "salario": fake.pydecimal(
                    min_value=550_000,
                    max_value=2_500_000,
                    right_digits=2,
                ),
                "activo": fake.boolean(chance_of_getting_true=90),
                "email": fake.unique.safe_email()[:100],
                "telefono": fake.numerify(text="+569########"),
            }
            _, creado = Empleado.objects.update_or_create(
                rut=rut,
                defaults=defaults,
            )
            if creado:
                creados += 1
            else:
                actualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeder finalizado: {creados} empleados creados, "
                f"{actualizados} actualizados."
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
