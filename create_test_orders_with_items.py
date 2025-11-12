#!/usr/bin/env python3
"""
Crea órdenes de prueba con items para testing del frontend
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from users.models import CustomUser
from products.models import Product
from shop_orders.models import Order, OrderItem
from decimal import Decimal

def create_test_orders():
    """Crea 5 órdenes de prueba con items"""
    
    print("🔍 Verificando datos existentes...")
    
    # Obtener usuarios
    try:
        admin = CustomUser.objects.get(username='admin')
        pedro = CustomUser.objects.filter(username='pedro_cliente').first()
        users = [admin, pedro] if pedro else [admin]
        print(f"✅ Usuarios encontrados: {len(users)}")
    except Exception as e:
        print(f"❌ Error obteniendo usuarios: {e}")
        return
    
    # Obtener productos
    products = list(Product.objects.all()[:10])
    if not products:
        print("❌ No hay productos. Ejecuta seed_data.py primero")
        return
    print(f"✅ Productos disponibles: {len(products)}")
    
    # Eliminar orden vacía si existe
    empty_orders = Order.objects.filter(total_price=0)
    if empty_orders.exists():
        count = empty_orders.count()
        empty_orders.delete()
        print(f"🗑️ Eliminadas {count} órdenes vacías\n")
    
    print("🛒 Creando órdenes de prueba...\n")
    
    statuses = ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED']
    
    for i in range(5):
        user = users[i % len(users)]
        status = statuses[i % len(statuses)]
        
        # Crear orden
        order = Order.objects.create(
            user=user,
            status=status,
            total_price=Decimal('0.00')
        )
        
        # Agregar 2-4 items aleatorios
        import random
        num_items = random.randint(2, 4)
        total = Decimal('0.00')
        
        for j in range(num_items):
            product = products[random.randint(0, len(products) - 1)]
            quantity = random.randint(1, 3)
            price = product.price
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )
            
            total += price * quantity
        
        # Actualizar total de la orden
        order.total_price = total
        order.save()
        
        print(f"✅ Orden #{order.id} - {user.username} - {status} - ${total} ({num_items} items)")
    
    print(f"\n{'='*60}")
    print(f"✅ Se crearon 5 órdenes de prueba exitosamente")
    print(f"{'='*60}\n")
    
    # Verificar
    total_orders = Order.objects.count()
    total_items = OrderItem.objects.count()
    print(f"📊 Total órdenes: {total_orders}")
    print(f"📦 Total items: {total_items}")
    print(f"💰 Orden más valiosa: ${Order.objects.order_by('-total_price').first().total_price}")


if __name__ == '__main__':
    create_test_orders()
