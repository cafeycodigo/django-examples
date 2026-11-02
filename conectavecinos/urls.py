from django.urls import path
from . import views

app_name = "conectavecinos"

urlpatterns = [
    path("", views.index, name="index"),
]
