"""
Script para crear órdenes en estado DELIVERED (Entregadas) en la base de datos de producción.
Útil para probar el sistema de devoluciones sin tener que esperar el flujo completo.

Uso:
    # Para conectar a la base de datos de PRODUCCIÓN (Render):
    python create_delivered_orders.py --production
    
    # Para conectar a la base de datos LOCAL:
    python create_delivered_orders.py

Este script:
1. Se conecta a la base de datos (producción o local)
2. Crea órdenes con estado DELIVERED
3. Asigna productos reales de la base de datos
4. Crea las órdenes para usuarios existentes
5. NO afecta el stock (las órdenes ya están "procesadas")
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Verificar si se quiere usar la base de datos de producción
USE_PRODUCTION = '--production' in sys.argv or '--prod' in sys.argv

if USE_PRODUCTION:
    # URL de la base de datos de producción en Render
    PRODUCTION_DB_URL = 'postgresql://ecommerce_db_k9tb_user:FTotph4caKAGtFwPAXSKVOtkXmJvg91E@dpg-d49llop5pdvs73d0dka0-a.oregon-postgres.render.com/ecommerce_db_k9tb'
    os.environ['DATABASE_URL'] = PRODUCTION_DB_URL
    print("🌐 Conectando a la base de datos de PRODUCCIÓN (Render)...")
else:
    print("💻 Conectando a la base de datos LOCAL...")

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.contrib.auth import get_user_model
from shop_orders.models import Order, OrderItem
from products.models import Product
from django.utils import timezone

User = get_user_model()


def create_delivered_orders(num_orders=10):
    """
    Crea órdenes en estado DELIVERED para probar devoluciones
    
    Args:
        num_orders: Número de órdenes a crear (default: 10)
    """
    print("🚀 Creando órdenes DELIVERED para pruebas de devoluciones...\n")
    
    if USE_PRODUCTION:
        print("⚠️  ADVERTENCIA: Estás modificando la base de datos de PRODUCCIÓN")
        print("   Presiona ENTER para continuar o Ctrl+C para cancelar...")
        input()
    
    # Verificar que hay usuarios
    users = User.objects.filter(is_staff=False).order_by('id')
    if not users.exists():
        print("❌ No hay usuarios en la base de datos.")
        print("   Primero crea algunos usuarios.")
        return
    
    print(f"✅ Encontrados {users.count()} usuarios")
    
    # Verificar que hay productos
    products = Product.objects.filter(is_active=True, stock__gt=0).order_by('id')
    if not products.exists():
        print("❌ No hay productos activos con stock.")
        print("   Primero agrega algunos productos.")
        return
    
    print(f"✅ Encontrados {products.count()} productos activos\n")
    
    created_orders = []
    
    for i in range(num_orders):
        # Seleccionar un usuario aleatorio
        user = users[(i % users.count())]
        
        # Crear la orden con estado DELIVERED
        # Fecha de creación: hace 5-15 días
        days_ago = 5 + (i % 10)
        created_at = timezone.now() - timedelta(days=days_ago)
        
        order = Order.objects.create(
            user=user,
            status=Order.OrderStatus.DELIVERED,  # ✅ Estado DELIVERED
            total_price=Decimal('0.00')
        )
        
        # Modificar la fecha de creación manualmente
        order.created_at = created_at
        order.save()
        
        # Agregar 1-3 productos a la orden
        num_items = 1 + (i % 3)
        order_total = Decimal('0.00')
        
        for j in range(num_items):
            product = products[(i + j) % products.count()]
            quantity = 1 + (j % 2)  # 1 o 2 unidades
            
            item_price = product.price
            subtotal = item_price * quantity
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=item_price
            )
            
            order_total += subtotal
        
        # Actualizar el total de la orden
        order.total_price = order_total
        order.save()
        
        created_orders.append(order)
        
        print(f"✅ Orden #{order.id} creada:")
        print(f"   Usuario: {user.email}")
        print(f"   Estado: DELIVERED")
        print(f"   Total: ${order.total_price}")
        print(f"   Items: {num_items}")
        print(f"   Fecha: {created_at.strftime('%Y-%m-%d %H:%M')}")
        print()
    
    print(f"\n🎉 ¡Completado! Se crearon {len(created_orders)} órdenes DELIVERED")
    print(f"\n📋 Resumen:")
    print(f"   - Total de órdenes: {len(created_orders)}")
    print(f"   - Estado: DELIVERED (listas para devolución)")
    print(f"   - Usuarios: {users.count()}")
    print(f"   - IDs de órdenes: {[o.id for o in created_orders]}")
    
    print(f"\n🧪 Para probar devoluciones:")
    print(f"   1. Inicia sesión con cualquiera de estos usuarios:")
    for user in users[:3]:
        print(f"      - {user.email}")
    print(f"   2. Ve a 'Mis Órdenes'")
    print(f"   3. Selecciona una orden DELIVERED")
    print(f"   4. Haz clic en 'Solicitar Devolución'")
    

if __name__ == '__main__':
    try:
        # Obtener el número de órdenes desde los argumentos
        num_orders = 10  # Default
        for arg in sys.argv:
            if arg.startswith('--num='):
                num_orders = int(arg.split('=')[1])
        
        create_delivered_orders(num_orders)
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
