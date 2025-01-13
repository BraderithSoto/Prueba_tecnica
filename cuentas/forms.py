from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Producto

class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirma Contraseña")

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Correo")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'cantidad_stock', 'imagen', 'especificaciones']

# Formulario para el filtrado y búsqueda de productos
class ProductoFiltroForm(forms.Form):
    q = forms.CharField(max_length=100, required=False, label='Buscar')
    orden = forms.ChoiceField(choices=[('', 'Ordenar por'), ('nombre', 'Nombre'), ('precio', 'Precio')], required=False)
    precio_min = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Precio Mínimo')
    precio_max = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Precio Máximo')

    def clean(self):
        cleaned_data = super().clean()
        precio_min = cleaned_data.get('precio_min')
        precio_max = cleaned_data.get('precio_max')

        if precio_min and precio_max and precio_min > precio_max:
            raise forms.ValidationError("El precio mínimo no puede ser mayor al precio máximo.")
        return cleaned_data
