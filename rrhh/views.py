from django.shortcuts import render

from .models import Empleado


def index(request):
    empleados = Empleado.objects.all().order_by("nombre_completo")
    return render(request, "rrhh/index.html", {"empleados": empleados})
