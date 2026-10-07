from django import forms

from .models import Vehiculo


class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = (
            "patente",
            "marca",
            "modelo",
            "anio",
            "kilometraje",
            "combustible",
            "color",
            "capacidad_pasajeros",
        )
        labels = {
            "patente": "Patente",
            "marca": "Marca",
            "modelo": "Modelo",
            "anio": "Año",
            "kilometraje": "Kilometraje",
            "combustible": "Combustible",
            "color": "Color",
            "capacidad_pasajeros": "Capacidad de pasajeros",
        }
        widgets = {
            "patente": forms.TextInput(attrs={"placeholder": "ABCD12"}),
            "anio": forms.NumberInput(attrs={"min": 1886}),
            "kilometraje": forms.NumberInput(attrs={"min": 0}),
            "capacidad_pasajeros": forms.NumberInput(attrs={"min": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.error_messages["required"] = "Este campo es obligatorio."
            field.error_messages["invalid"] = "Ingresa un valor válido."
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "aria-describedby": f"id_{name}_help",
                    "aria-required": str(field.required).lower(),
                }
            )
        self.fields["patente"].error_messages["unique"] = (
            "Ya existe un vehículo con esta patente."
        )

    def clean(self):
        cleaned_data = super().clean()
        for name in self.errors:
            if name in self.fields:
                self.fields[name].widget.attrs["aria-invalid"] = "true"
        return cleaned_data
