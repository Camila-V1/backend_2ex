import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from shop_orders.models import Order
from shop_orders.serializers import OrderSerializer

print(f'📊 Total órdenes en DB: {Order.objects.count()}')
print(f'📦 Órdenes con items: {Order.objects.filter(items__isnull=False).distinct().count()}')

# Últimas 5 órdenes
last_5 = Order.objects.order_by('-id')[:5]
print('\n📋 Últimas 5 órdenes:')
for order in last_5:
    print(f'  #{order.id} - {order.user.username} - {order.status} - ${order.total_price} - {order.items.count()} items')

# Simular lo que hace el ViewSet
print('\n🔍 Simulando queryset del AdminOrderViewSet:')
queryset = Order.objects.all().order_by('-created_at')
print(f'  Total en queryset: {queryset.count()}')
print(f'  Primeras 5: {list(queryset.values_list("id", flat=True)[:5])}')

# Serializar como lo hace el endpoint
print('\n📤 Serializando las primeras 5:')
serialized = OrderSerializer(queryset[:5], many=True)
print(f'  Cantidad serializada: {len(serialized.data)}')
for order_data in serialized.data[:3]:
    print(f'  #{order_data["id"]} - {order_data["user"]} - {len(order_data["items"])} items')
