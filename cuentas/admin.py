from django.contrib import admin
from .models import Producto, CarritoItem

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio', 'cantidad_stock')  # Columnas en la tabla
    search_fields = ('nombre',)  # Barra de búsqueda
    list_filter = ('precio',)  # Filtros laterales
    ordering = ('-id',)  # Orden predeterminado

@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'producto', 'cantidad')
    search_fields = ('usuario__username', 'producto__nombre')
    list_filter = ('usuario',)
