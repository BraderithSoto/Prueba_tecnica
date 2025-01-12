from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Producto, CarritoItem

# Vista del home
def home(request):
    productos = Producto.objects.all()  # Obtener todos los productos
    return render(request, 'cuentas/home.html', {'productos': productos})

# Vista de productos
def productos(request):
    productos = Producto.objects.all()  # Obtener todos los productos
    return render(request, 'cuentas/productos.html', {'productos': productos})

# Vista del carrito
def carrito(request):
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión para ver tu carrito.")
        return redirect('inicio_sesion')
    carrito_items = CarritoItem.objects.filter(usuario=request.user)
    total = sum(item.producto.precio * item.cantidad for item in carrito_items)
    return render(request, 'cuentas/carrito.html', {'carrito_items': carrito_items, 'total': total})

# Agregar producto al carrito
def agregar_al_carrito(request, producto_id):
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión para agregar productos al carrito.")
        return redirect('inicio_sesion')
    producto = get_object_or_404(Producto, id=producto_id)
    carrito_item, creado = CarritoItem.objects.get_or_create(usuario=request.user, producto=producto)
    if not creado:
        carrito_item.cantidad += 1
    carrito_item.save()
    messages.success(request, f"Se agregó {producto.nombre} al carrito.")
    return redirect('carrito')

# Eliminar producto del carrito
def eliminar_del_carrito(request, item_id):
    carrito_item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
    carrito_item.delete()
    messages.success(request, "Producto eliminado del carrito.")
    return redirect('carrito')

# Finalizar compra
def finalizar_compra(request):
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión para finalizar la compra.")
        return redirect('inicio_sesion')
    CarritoItem.objects.filter(usuario=request.user).delete()  # Elimina todos los productos del carrito
    messages.success(request, "¡Compra finalizada con éxito!")
    return redirect('home')

# Vista de registro
def registro(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('registro')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
            return redirect('registro')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo electrónico ya está registrado.")
            return redirect('registro')
        
        # Crear usuario
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.")
        return redirect('inicio_sesion')

    return render(request, 'cuentas/registro.html')

# Vista de inicio de sesión
def inicio_sesion(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            usuarios = User.objects.filter(email=email)
            if not usuarios.exists():
                messages.error(request, "El correo no está registrado.")
                return redirect('inicio_sesion')
            elif usuarios.count() > 1:
                messages.error(request, "Hay múltiples usuarios con ese correo. Contacte al administrador.")
                return redirect('inicio_sesion')
            
            username = usuarios.first().username
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"¡Bienvenido, {user.username}!")
                return redirect('home')
            else:
                messages.error(request, "Correo o contraseña incorrectos.")
        except User.DoesNotExist:
            messages.error(request, "El correo no está registrado.")
        
        return redirect('inicio_sesion')

    return render(request, 'cuentas/inicio_sesion.html')

# Vista de cierre de sesión
def cerrar_sesion(request):
    logout(request)
    messages.success(request, "Has cerrado sesión exitosamente.")
    return redirect('home')
