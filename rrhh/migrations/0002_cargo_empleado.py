from django.db import migrations, models
import django.db.models.deletion


def convertir_cargos_a_relacion(apps, schema_editor):
    empleado_model = apps.get_model("rrhh", "Empleado")
    cargo_model = apps.get_model("rrhh", "Cargo")
    database = schema_editor.connection.alias

    nombres_cargo = (
        empleado_model.objects.using(database)
        .values_list("cargo", flat=True)
        .distinct()
    )
    for nombre in nombres_cargo:
        cargo, _ = cargo_model.objects.using(database).get_or_create(nombre=nombre)
        empleado_model.objects.using(database).filter(cargo=nombre).update(
            cargo=str(cargo.pk)
        )


def revertir_cargos_a_texto(apps, schema_editor):
    empleado_model = apps.get_model("rrhh", "Empleado")
    cargo_model = apps.get_model("rrhh", "Cargo")
    database = schema_editor.connection.alias

    for cargo in cargo_model.objects.using(database).iterator():
        empleado_model.objects.using(database).filter(cargo=str(cargo.pk)).update(
            cargo=cargo.nombre
        )


class Migration(migrations.Migration):
    dependencies = [
        ("rrhh", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Cargo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.RunPython(
            convertir_cargos_a_relacion,
            revertir_cargos_a_texto,
        ),
        migrations.AlterField(
            model_name="empleado",
            name="cargo",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="empleados",
                to="rrhh.cargo",
            ),
        ),
    ]
