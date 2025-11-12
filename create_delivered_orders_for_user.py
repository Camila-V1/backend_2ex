"""
Script para crear órdenes DELIVERED para un usuario específico.
Útil para probar el sistema de devoluciones con un usuario en particular.

Uso:
    # Para juan_cliente en producción
    python create_delivered_orders_for_user.py --production --username=juan_cliente --num=5
    
    # Para cualquier usuario
    python create_delivered_orders_for_user.py --production --username=laura@email.com --num=3
"""

import os
import sys
import django
from decimal import Decimal
from datetime import timedelta

# Verificar si se quiere usar la base de datos de producción
USE_PRODUCTION = '--production' in sys.argv or '--prod' in sys.argv

if USE_PRODUCTION:
    PRODUCTION_DB_URL = 'postgresql://ecommerce_db_k9tb_user:FTotph4caKAGtFwPAXSKVOtkXmJvg91E@dpg-d49llop5pdvs73d0dka0-a.oregon-postgres.render.com/ecommerce_db_k9tb'
    os.environ['DATABASE_URL'] = PRODUCTION_DB_URL
    print("🌐 Conectando a la base de datos de PRODUCCIÓN (Render)...")
else:
    print("💻 Conectando a la base de datos LOCAL...")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.contrib.auth import get_user_model
from shop_orders.models import Order, OrderItem
from products.models import Product
from django.utils import timezone

User = get_user_model()


def create_delivered_orders_for_user(username, num_orders=5):
    """
    Crea órdenes DELIVERED para un usuario específico
    """
    print(f"🚀 Creando órdenes DELIVERED para {username}...\n")
    
    if USE_PRODUCTION:
        print("⚠️  ADVERTENCIA: Estás modificando la base de datos de PRODUCCIÓN")
        print("   Presiona ENTER para continuar o Ctrl+C para cancelar...")
        input()
    
    # Buscar el usuario
    try:
        user = User.objects.get(username=username)
        print(f"✅ Usuario encontrado: {user.email} (ID: {user.id})\n")
    except User.DoesNotExist:
        # Intentar buscar por email
        try:
            user = User.objects.get(email=username)
            print(f"✅ Usuario encontrado: {user.email} (ID: {user.id})\n")
        except User.DoesNotExist:
            print(f"❌ Error: No se encontró el usuario '{username}'")
            print("\n📋 Usuarios disponibles:")
            for u in User.objects.filter(is_staff=False)[:10]:
                print(f"   - {u.username} ({u.email})")
            return
    
    # Verificar que hay productos
    products = Product.objects.filter(is_active=True, stock__gt=0).order_by('id')
    if not products.exists():
        print("❌ No hay productos activos con stock.")
        return
    
    print(f"✅ Encontrados {products.count()} productos activos\n")
    
    created_orders = []
    
    for i in range(num_orders):
        # Fecha de creación: hace 5-15 días
        days_ago = 5 + (i % 10)
        created_at = timezone.now() - timedelta(days=days_ago)
        
        order = Order.objects.create(
            user=user,
            status=Order.OrderStatus.DELIVERED,
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
            quantity = 1 + (j % 2)
            
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
    
    print(f"\n🎉 ¡Completado! Se crearon {len(created_orders)} órdenes DELIVERED para {user.username}")
    print(f"\n📋 Resumen:")
    print(f"   - Usuario: {user.username} ({user.email})")
    print(f"   - Total de órdenes creadas: {len(created_orders)}")
    print(f"   - Estado: DELIVERED (listas para devolución)")
    print(f"   - IDs de órdenes: {[o.id for o in created_orders]}")
    
    print(f"\n🧪 Para probar devoluciones:")
    print(f"   1. Inicia sesión con: {user.username}")
    print(f"   2. Ve a 'Mis Órdenes'")
    print(f"   3. Verás {len(created_orders)} órdenes DELIVERED")
    print(f"   4. Haz clic en 'Solicitar Devolución' en cualquiera")


if __name__ == '__main__':
    try:
        # Obtener parámetros
        username = None
        num_orders = 5
        
        for arg in sys.argv:
            if arg.startswith('--username='):
                username = arg.split('=')[1]
            if arg.startswith('--num='):
                num_orders = int(arg.split('=')[1])
        
        if not username:
            print("❌ Error: Debes especificar un usuario")
            print("\nUso:")
            print("  python create_delivered_orders_for_user.py --production --username=juan_cliente --num=5")
            sys.exit(1)
        
        create_delivered_orders_for_user(username, num_orders)
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
