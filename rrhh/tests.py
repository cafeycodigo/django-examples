from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase
from django.test import TransactionTestCase
from django.urls import reverse

from .models import Cargo, Empleado


class EmpleadoIndexTests(TestCase):
    def test_index_shows_employees_created_by_seeder(self):
        empleado = Empleado.objects.create(
            rut="12345678-5",
            nombre_completo="Ana Ejemplo",
            cargo=Cargo.objects.create(nombre="Analista"),
            salario=Decimal("1250000.00"),
            activo=True,
            email="ana@example.com",
            telefono="+56912345678",
        )

        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrhh/index.html")
        self.assertContains(response, empleado.rut)
        self.assertContains(response, empleado.nombre_completo)
        self.assertContains(response, empleado.cargo)
        self.assertContains(response, str(empleado.salario))
        self.assertContains(response, empleado.email)
        self.assertContains(response, empleado.telefono)

    def test_index_shows_message_when_there_are_no_employees(self):
        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No hay empleados registrados.")


class EmpleadoSeederTests(TestCase):
    def test_seeder_creates_employees_and_linked_cargos_idempotently(self):
        primera_ejecucion = StringIO()
        call_command("seed_empleado", stdout=primera_ejecucion)

        self.assertEqual(Empleado.objects.count(), 20)
        self.assertGreater(Cargo.objects.count(), 0)
        self.assertEqual(
            Empleado.objects.filter(cargo__isnull=True).count(),
            0,
        )
        cantidad_cargos = Cargo.objects.count()
        self.assertIn("20 empleados creados", primera_ejecucion.getvalue())

        segunda_ejecucion = StringIO()
        call_command("seed_empleado", stdout=segunda_ejecucion)

        self.assertEqual(Empleado.objects.count(), 20)
        self.assertEqual(Cargo.objects.count(), cantidad_cargos)
        self.assertIn("20 actualizados", segunda_ejecucion.getvalue())
        self.assertIn("0 cargos creados", segunda_ejecucion.getvalue())


class CargoAdminTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="rrhh-admin",
            email="rrhh-admin@example.com",
            password=None,
        )
        self.client.force_login(self.admin_user)

    def test_cargo_admin_lists_cargo_and_employee_count(self):
        cargo = Cargo.objects.create(nombre="Analista")
        Empleado.objects.create(
            rut="12345678-5",
            nombre_completo="Ana Ejemplo",
            cargo=cargo,
            salario=Decimal("1250000.00"),
        )

        response = self.client.get(
            reverse("admin:rrhh_cargo_changelist")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Analista")
        self.assertContains(response, "1")

    def test_employee_admin_lists_related_cargo(self):
        cargo = Cargo.objects.create(nombre="Analista")
        Empleado.objects.create(
            rut="12345678-5",
            nombre_completo="Ana Ejemplo",
            cargo=cargo,
            salario=Decimal("1250000.00"),
        )

        response = self.client.get(
            reverse("admin:rrhh_empleado_changelist")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ana Ejemplo")
        self.assertContains(response, "Analista")


class CargoDataMigrationTests(TransactionTestCase):
    migrate_from = ("rrhh", "0001_initial")
    migrate_to = ("rrhh", "0002_cargo_empleado")

    def setUp(self):
        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_from])
        old_apps = executor.loader.project_state([self.migrate_from]).apps
        old_empleado = old_apps.get_model("rrhh", "Empleado")
        old_empleado.objects.create(
            rut="12345678-5",
            nombre_completo="Ana Ejemplo",
            cargo="Analista",
            salario=Decimal("1250000.00"),
        )
        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_to])
        self.apps = executor.loader.project_state([self.migrate_to]).apps

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_existing_cargo_text_is_migrated_to_related_model(self):
        empleado_model = self.apps.get_model("rrhh", "Empleado")
        empleado = empleado_model.objects.get(rut="12345678-5")

        self.assertEqual(empleado.cargo.nombre, "Analista")

    def test_migration_can_be_reversed_without_losing_cargo_name(self):
        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_from])
        old_apps = executor.loader.project_state([self.migrate_from]).apps
        empleado = old_apps.get_model("rrhh", "Empleado").objects.get(
            rut="12345678-5"
        )

        self.assertEqual(empleado.cargo, "Analista")

        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_to])
