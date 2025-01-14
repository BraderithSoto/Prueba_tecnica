from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Producto, CarritoItem, Pedido
from .forms import ProductoFiltroForm

#bloequeo de vistas
from django.contrib.auth.decorators import login_required


def home(request):
    productos = Producto.objects.all()  
    productos_recomendados = Producto.objects.filter(recomendado=True)
    carrito_count = CarritoItem.objects.filter(usuario=request.user).count() if request.user.is_authenticated else 0
    
    for producto in productos:
        producto.precio_en_pesos = producto.obtener_precio_en_pesos()

    return render(request, 'cuentas/home.html', {
        'productos': productos,
        'productos_recomendados': productos_recomendados,
        'carrito_count': carrito_count
    })

@login_required
def productos(request):
    form = ProductoFiltroForm(request.GET)
    productos = Producto.objects.all()  

    if form.is_valid():
        q = form.cleaned_data.get('q')
        if q:
            productos = productos.filter(nombre__icontains=q) | productos.filter(descripcion__icontains=q)

        precio_min = form.cleaned_data.get('precio_min')
        precio_max = form.cleaned_data.get('precio_max')
        if precio_min is not None:
            productos = productos.filter(precio__gte=precio_min)
        if precio_max is not None:
            productos = productos.filter(precio__lte=precio_max)

        orden = form.cleaned_data.get('orden')
        if orden == 'nombre':
            productos = productos.order_by('nombre')
        elif orden == 'precio':
            productos = productos.order_by('precio')

    return render(request, 'cuentas/productos.html', {'productos': productos, 'form': form})

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)  # Obtener producto por ID
    return render(request, 'cuentas/detalle_producto.html', {'producto': producto})

@login_required
def carrito(request):
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión para ver tu carrito.")
        return redirect('inicio_sesion')
    
    carrito_items = CarritoItem.objects.filter(usuario=request.user)
    carrito_items_disponibles = [item for item in carrito_items if item.producto.cantidad_stock > 0]
    total = sum(item.total_precio() for item in carrito_items_disponibles)

    productos_agotados = [item for item in carrito_items if item.producto.cantidad_stock <= 0]

    if not carrito_items_disponibles:
        messages.info(request, "Tu carrito está vacío.")
    
    return render(request, 'cuentas/carrito.html', {
        'carrito_items': carrito_items_disponibles, 
        'total': total,
        'productos_agotados': productos_agotados
    })

@login_required
def agregar_al_carrito(request, producto_id):
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión para agregar productos al carrito.")
        return redirect('inicio_sesion')
    
    producto = get_object_or_404(Producto, id=producto_id)

    if producto.cantidad_stock <= 0:
        messages.error(request, f"El producto {producto.nombre} está agotado.")
        return redirect('productos')

    carrito_item, created = CarritoItem.objects.get_or_create(usuario=request.user, producto=producto)
    
    if carrito_item.cantidad >= producto.cantidad_stock:
        messages.error(request, f"No puedes agregar más de {producto.cantidad_stock} unidades de {producto.nombre}.")
        return redirect('productos')

    if created:
        carrito_item.cantidad = 1
    else:
        carrito_item.cantidad += 1

    try:
        carrito_item.save()  
    except ValueError as e:
        messages.error(request, str(e))  
        return redirect('productos')
    
    messages.success(request, f"Producto {producto.nombre} agregado al carrito.")
    return redirect('carrito')

@login_required
def reducir_cantidad(request, item_id):
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión para modificar tu carrito.")
        return redirect('inicio_sesion')

    carrito_item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)

    if carrito_item.cantidad > 1:
        carrito_item.cantidad -= 1
        carrito_item.save()
        messages.success(request, f"La cantidad de {carrito_item.producto.nombre} ha sido reducida.")
    else:
        carrito_item.delete()
        messages.success(request, f"{carrito_item.producto.nombre} ha sido eliminado del carrito.")
    
    return redirect('carrito')

@login_required
def eliminar_del_carrito(request, item_id):
    carrito_item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
    
    carrito_item.delete()
    
    messages.success(request, "Producto eliminado del carrito.")
    return redirect('carrito')

@login_required
def finalizar_compra(request):
    if request.method == 'POST':
        direccion = request.POST.get('direccion')
        metodo_pago = request.POST.get('metodo_pago')
        password = request.POST.get('password')

        usuario = authenticate(username=request.user.username, password=password)
        if usuario is None:
            messages.error(request, "La contraseña es incorrecta. Por favor, inténtalo de nuevo.")
            return redirect('finalizar_compra')

        carrito_items = CarritoItem.objects.filter(usuario=request.user)
        if not carrito_items.exists():
            messages.error(request, "El carrito está vacío. No puedes finalizar una compra sin productos.")
            return redirect('carrito')

        total = sum(item.total_precio() for item in carrito_items)

        pedido = Pedido.objects.create(
            usuario=request.user,
            total=total,
            direccion=direccion,
            metodo_pago=metodo_pago
        )
        
        carrito_items.delete()

        messages.success(request, "¡Compra realizada con éxito! Gracias por tu pedido.")
        return redirect('productos')
    
    context = {}
    return render(request, 'cuentas/finalizar_compra.html', context)

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
        
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.")
        return redirect('inicio_sesion')

    return render(request, 'cuentas/registro.html')

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

def cerrar_sesion(request):
    logout(request)
    messages.success(request, "Has cerrado sesión exitosamente.")
    return redirect('home')
