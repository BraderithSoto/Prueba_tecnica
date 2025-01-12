from django.contrib import admin
from .models import Producto, CarritoItem

# Filtro personalizado para productos sin stock
class SinStockFilter(admin.SimpleListFilter):
    title = 'Sin stock'
    parameter_name = 'sin_stock'

    def lookups(self, request, model_admin):
        return [('yes', 'Sin stock')]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(cantidad_stock=0)
        return queryset

# Configuración del modelo Producto en el administrador
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio', 'cantidad_stock')
    list_filter = ('precio', SinStockFilter)
    search_fields = ('nombre',)
    list_per_page = 20
    actions = ['actualizar_stock']

    def actualizar_stock(self, request, queryset):
        for producto in queryset:
            producto.cantidad_stock += 10  # Incrementar stock por 10
            producto.save()
        self.message_user(request, "Stock actualizado con éxito.")
    actualizar_stock.short_description = 'Incrementar Stock en 10'

    def save_model(self, request, obj, form, change):
        if obj.precio < 0:
            raise ValueError("El precio no puede ser negativo.")
        super().save_model(request, obj, form, change)

# Configuración del modelo CarritoItem en el administrador
@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'producto', 'cantidad', 'total_precio')
    search_fields = ('usuario__username', 'producto__nombre')
    list_filter = ('usuario', 'producto')

    def total_precio(self, obj):
        return obj.producto.precio * obj.cantidad
    total_precio.short_description = 'Precio Total'
