from django.contrib import admin
from .models import Producto, CarritoItem, Pedido
from django.contrib.auth.models import User

class SinStockFilter(admin.SimpleListFilter):
    title = 'Sin stock'
    parameter_name = 'sin_stock'

    def lookups(self, request, model_admin):
        return [('yes', 'Sin stock')]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(cantidad_stock=0)
        return queryset

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio', 'cantidad_stock')
    list_filter = ('precio', SinStockFilter)
    search_fields = ('nombre',)
    list_per_page = 20
    actions = ['actualizar_stock']

    def actualizar_stock(self, request, queryset):
        for producto in queryset:
            producto.cantidad_stock += 1  
            producto.save()
        self.message_user(request, "Stock actualizado con éxito.")
    actualizar_stock.short_description = 'Incrementar Stock en 1'

    def save_model(self, request, obj, form, change):
        if obj.precio < 0:
            raise ValueError("El precio no puede ser negativo.")
        super().save_model(request, obj, form, change)


@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'producto', 'cantidad', 'total_precio')
    search_fields = ('usuario__username', 'producto__nombre')
    list_filter = ('usuario', 'producto')

    def total_precio(self, obj):
        return obj.producto.precio * obj.cantidad
    total_precio.short_description = 'Precio Total'

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'total', 'estado', 'fecha')
    list_filter = ('estado', 'fecha')
    search_fields = ('usuario__username',)
    actions = ['marcar_como_entregado', 'marcar_como_pendiente', 'marcar_como_cancelado']

    def marcar_como_entregado(self, request, queryset):
        queryset.update(estado='entregado')
        self.message_user(request, "Los pedidos seleccionados han sido marcados como entregados.")
    marcar_como_entregado.short_description = 'Marcar como Entregado'

    def marcar_como_pendiente(self, request, queryset):
        queryset.update(estado='pendiente')
        self.message_user(request, "Los pedidos seleccionados han sido marcados como pendientes.")
    marcar_como_pendiente.short_description = 'Marcar como Pendiente'

    def marcar_como_cancelado(self, request, queryset):
        
        queryset.update(estado='cancelado')
        self.message_user(request, "Los pedidos seleccionados han sido marcados como cancelados.")
    marcar_como_cancelado.short_description = 'Marcar como Cancelado'
