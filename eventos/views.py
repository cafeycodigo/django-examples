from django.http import JsonResponse

from .models import Evento


def index(request):
    """Devuelve todos los eventos, equivalente a SELECT * FROM eventos_evento."""
    return JsonResponse(
        list(Evento.objects.values()),
        safe=False,
        json_dumps_params={"ensure_ascii": False, "indent": 2},
    )
