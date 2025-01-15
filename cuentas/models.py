from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_stock = models.PositiveIntegerField()
    imagen = models.ImageField(upload_to='productos/')
    especificaciones = models.TextField()
    agotado = models.BooleanField(default=False)
    recomendado = models.BooleanField(default=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Usuario opcional

    def __str__(self):
        return self.nombre

    def reducir_stock(self, cantidad):
        """Reduce la cantidad de stock del producto cuando se agrega al carrito."""
        if self.cantidad_stock >= cantidad:
            self.cantidad_stock -= cantidad
            self.save()
        else:
            self.agotado = True  
            self.save()
            raise ValueError("No hay suficiente stock disponible.")
    
    def restablecer_stock(self, cantidad):
        """Restablece el stock del producto cuando se elimina del carrito."""
        self.cantidad_stock += cantidad
        if self.cantidad_stock > 0:
            self.agotado = False  # Si el stock es mayor a 0, marcamos el producto como disponible
        self.save()

    def obtener_precio_en_pesos(self):
        """Devuelve el precio formateado en pesos colombianos."""
        return f"${self.precio:,.2f}"

class CarritoItem(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.producto.nombre} - {self.usuario.username}"

    def total_precio(self):
        """Calcula el precio total para este producto en el carrito."""
        return self.producto.precio * self.cantidad

    def guardar(self):
        """Guarda el carrito, y actualiza el stock del producto."""
        if self.producto.agotado:  # Verifica si el producto está agotado
            raise ValueError("Este producto está agotado y no se puede agregar al carrito.")
        
        if self.producto.cantidad_stock >= self.cantidad:
            self.producto.reducir_stock(self.cantidad)  # Reduce el stock del producto
            super().save()  # Guarda el ítem en el carrito
        else:
            raise ValueError(f"No hay suficiente stock para agregar {self.cantidad} unidades de {self.producto.nombre} al carrito.")

    def eliminar(self):
        """Elimina este ítem del carrito y restablece el stock del producto."""
        self.producto.restablecer_stock(self.cantidad)  # Restablece el stock del producto
        super().delete()  # Elimina el ítem del carrito

class Pedido(models.Model):
    ESTADOS = [
        ('en_proceso', 'En proceso'),
        ('espera_confirmacion', 'Espera de confirmación'),
        ('entregado', 'Entregado'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='espera_confirmacion')
    fecha = models.DateTimeField(auto_now_add=True)
    direccion = models.CharField(max_length=500, default='Dirección no proporcionada')
    metodo_pago = models.CharField(max_length=100, default='Pago no especificado')

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username} - {self.estado}"
