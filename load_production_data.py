#!/usr/bin/env python
"""
Script para cargar datos de prueba en la base de datos de producción.
Crea órdenes con items para testing del frontend.

Uso:
    python load_production_data.py
"""

import os
import sys
import django
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from shop_orders.models import Order, OrderItem
from products.models import Product
from users.models import CustomUser


def main():
    print('🚀 CARGANDO DATOS DE PRUEBA EN PRODUCCIÓN')
    print('=' * 60)
    
    # Verificar usuario admin
    try:
        user = CustomUser.objects.get(username='admin')
        print(f'✅ Usuario encontrado: {user.username}')
    except CustomUser.DoesNotExist:
        print('❌ Usuario admin no encontrado')
        print('   Creando usuario admin...')
        user = CustomUser.objects.create_user(
            username='admin',
            email='admin@ecommerce.com',
            password='admin123',
            is_staff=True,
            is_superuser=True,
            role='ADMIN'
        )
        print(f'✅ Usuario admin creado')
    
    # Verificar productos
    products = list(Product.objects.all()[:10])
    if not products:
        print('❌ No hay productos en la base de datos')
        print('   Ejecuta seed_data.py primero')
        return
    print(f'✅ Productos disponibles: {len(products)}')
    
    # Limpiar órdenes vacías
    empty_orders = Order.objects.filter(total_price=0)
    empty_count = empty_orders.count()
    if empty_count > 0:
        empty_orders.delete()
        print(f'🗑️  Eliminadas {empty_count} órdenes vacías')
    
    # Crear órdenes con items
    print('\n📦 Creando órdenes con items...')
    statuses = ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED']
    
    for i in range(5):
        status = statuses[i]
        order = Order.objects.create(user=user, status=status, total_price=0)
        
        # Agregar 2-4 items por orden
        num_items = random.randint(2, 4)
        total = 0
        
        for j in range(num_items):
            product = random.choice(products)
            quantity = random.randint(1, 3)
            price = product.price
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )
            
            total += price * quantity
        
        order.total_price = total
        order.save()
        
        print(f'  ✅ Orden #{order.id} - {status} - ${total:.2f} ({num_items} items)')
    
    # Estadísticas finales
    print('\n' + '=' * 60)
    print('📊 RESUMEN')
    print('=' * 60)
    print(f'  Total órdenes: {Order.objects.count()}')
    print(f'  Total items: {OrderItem.objects.count()}')
    print(f'  Orden más valiosa: ${Order.objects.order_by("-total_price").first().total_price:.2f}')
    print('\n✅ Datos cargados exitosamente')


if __name__ == '__main__':
    main()
