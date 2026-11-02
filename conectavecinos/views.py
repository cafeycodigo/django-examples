from django.http import JsonResponse

def index(request):
    return JsonResponse({"proyecto": "ConectaVecinos", "administracion": "/admin/"})
