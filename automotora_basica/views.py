from django.shortcuts import render

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect

from .forms import VehiculoForm
from .models import Vehiculo

VEHICULO_LIST_URL = "automotora_basica:vehiculo_list"


@staff_member_required
def vehiculo_list(request):
    consulta = request.GET.get("q", "").strip()
    vehiculos = Vehiculo.objects.all()

    if consulta:
        vehiculos = vehiculos.filter(
            Q(patente__icontains=consulta)
            | Q(marca__icontains=consulta)
            | Q(modelo__icontains=consulta)
        )

    return render(
        request,
        "automotora_basica/vehiculo_list.html",
        {
            "vehiculos": vehiculos.order_by("-fecha_registro"),
            "consulta": consulta,
            "total_vehiculos": Vehiculo.objects.count(),
        },
    )


@staff_member_required
def vehiculo_create(request):
    form = VehiculoForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(VEHICULO_LIST_URL)

    return render(
        request,
        "automotora_basica/vehiculo_form.html",
        {"form": form, "titulo": "Registrar vehículo", "accion": "Crear vehículo"},
    )


@staff_member_required
def vehiculo_update(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    form = VehiculoForm(
        request.POST if request.method == "POST" else None,
        instance=vehiculo,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(VEHICULO_LIST_URL)

    return render(
        request,
        "automotora_basica/vehiculo_form.html",
        {"form": form, "titulo": "Editar vehículo", "accion": "Guardar cambios"},
    )


@staff_member_required
def vehiculo_delete(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    if request.method == "POST":
        vehiculo.delete()
        return redirect(VEHICULO_LIST_URL)

    return render(
        request,
        "automotora_basica/vehiculo_confirm_delete.html",
        {"vehiculo": vehiculo},
    )
