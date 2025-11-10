"""Test para identificar error en deliveries"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from deliveries.models import Delivery
from shop_orders.models import Order
from django.contrib.auth import get_user_model

print("=== TESTING DELIVERIES ===")
print(f"Total orders: {Order.objects.count()}")
print(f"Total deliveries: {Delivery.objects.count()}")
print()

# Intentar crear una delivery
try:
    # Buscar una orden PAID
    order = Order.objects.filter(status='PAID').first()
    if order:
        print(f"Found PAID order: {order.id}")
        print(f"Order user: {order.user}")
        print(f"Order total: {order.total_price}")
        
        # Crear delivery
        delivery = Delivery.objects.create(
            order=order,
            delivery_address="Test Address 123",
            customer_phone="123456789",
            status=Delivery.DeliveryStatus.PENDING
        )
        print(f"✅ Delivery created: {delivery.id}")
        
        # Test queryset
        from deliveries.views import DeliveryViewSet
        from rest_framework.test import APIRequestFactory
        
        User = get_user_model()
        admin = User.objects.get(username='admin')
        
        factory = APIRequestFactory()
        request = factory.get('/api/deliveries/deliveries/')
        request.user = admin
        
        view = DeliveryViewSet()
        view.request = request
        
        qs = view.get_queryset()
        print(f"✅ Queryset works! Count: {qs.count()}")
        
        # Probar serializar
        from deliveries.serializers import DeliverySerializer
        serializer = DeliverySerializer(qs.first())
        print(f"✅ Serialization works!")
        print(f"Data keys: {serializer.data.keys()}")
        
    else:
        print("❌ No PAID orders found")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
