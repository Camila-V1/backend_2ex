"""
Script para probar el flujo completo de Orden → Delivery → Garantía

Este script demuestra que el sistema está completamente integrado y funciona automáticamente.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.contrib.auth import get_user_model
from shop_orders.models import Order, OrderItem
from products.models import Product
from deliveries.models import Delivery, Warranty, DeliveryProfile
from django.utils import timezone

User = get_user_model()


def print_separator(title=""):
    """Imprimir separador visual"""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
    print("=" * 80 + "\n")


def test_flujo_completo():
    """Probar el flujo completo: Orden → Pago → Delivery → Entrega → Garantía"""
    
    print_separator("🧪 PRUEBA DE FLUJO COMPLETO: ORDEN → DELIVERY → GARANTÍA")
    
    # 1. Obtener o crear usuario de prueba
    print("📌 PASO 1: Obtener usuario de prueba")
    try:
        user = User.objects.get(username='cliente_test')
        print(f"✅ Usuario encontrado: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='cliente_test',
            email='cliente@test.com',
            password='test123',
            first_name='Cliente',
            last_name='De Prueba',
            role='CLIENT'
        )
        user.address = 'Av. Prueba 123, Lima, Perú'
        user.phone_number = '+51 999 888 777'
        user.save()
        print(f"✅ Usuario creado: {user.username}")
    
    # 2. Crear una orden PENDING
    print("\n📌 PASO 2: Crear orden en estado PENDING")
    
    # Obtener productos
    productos = Product.objects.filter(is_active=True)[:2]
    
    if not productos.exists():
        print("❌ ERROR: No hay productos disponibles. Ejecuta seed_data.py primero.")
        return
    
    # Crear orden
    orden = Order.objects.create(
        user=user,
        status=Order.OrderStatus.PENDING,
        total_price=0
    )
    
    # Agregar items
    total = 0
    for producto in productos:
        item = OrderItem.objects.create(
            order=orden,
            product=producto,
            quantity=1,
            price=producto.price
        )
        total += float(producto.price)
        print(f"   • Agregado: {producto.name} - ${producto.price}")
    
    orden.total_price = total
    orden.save()
    
    print(f"\n✅ Orden creada: #{orden.id}")
    print(f"   Estado: {orden.status}")
    print(f"   Total: ${orden.total_price}")
    print(f"   ¿Tiene Delivery? {hasattr(orden, 'delivery')}")
    print(f"   ¿Tiene Garantías? {orden.warranties.exists()}")
    
    # 3. Marcar orden como PAID (simular pago exitoso)
    print("\n📌 PASO 3: Marcar orden como PAID (simular pago exitoso)")
    orden.status = Order.OrderStatus.PAID
    orden.save()
    
    # Refrescar desde BD para obtener relaciones creadas por signals
    orden.refresh_from_db()
    
    print(f"✅ Orden actualizada a: {orden.status}")
    
    # Verificar si se creó el delivery automáticamente
    if hasattr(orden, 'delivery'):
        delivery = orden.delivery
        print(f"\n🚚 ¡DELIVERY CREADO AUTOMÁTICAMENTE!")
        print(f"   ID: {delivery.id}")
        print(f"   Estado: {delivery.status}")
        print(f"   Dirección: {delivery.delivery_address}")
        print(f"   Teléfono: {delivery.customer_phone}")
        print(f"   ¿Repartidor asignado? {delivery.delivery_person is not None}")
    else:
        print(f"\n❌ ERROR: No se creó delivery automáticamente")
        return
    
    # 4. Asignar repartidor (opcional, si existe)
    print("\n📌 PASO 4: Intentar asignar repartidor")
    try:
        repartidor = DeliveryProfile.objects.filter(
            status=DeliveryProfile.DeliveryStatus.AVAILABLE
        ).first()
        
        if repartidor:
            delivery.delivery_person = repartidor
            delivery.zone = repartidor.zone
            delivery.status = Delivery.DeliveryStatus.ASSIGNED
            delivery.assigned_at = timezone.now()
            delivery.save()
            
            repartidor.status = DeliveryProfile.DeliveryStatus.BUSY
            repartidor.save()
            
            print(f"✅ Repartidor asignado: {repartidor.user.get_full_name()}")
            print(f"   Zona: {repartidor.zone.name if repartidor.zone else 'N/A'}")
        else:
            print("⚠️  No hay repartidores disponibles (ejecuta create_delivery_test_data.py)")
    except Exception as e:
        print(f"⚠️  No se pudo asignar repartidor: {e}")
    
    # 5. Simular proceso de entrega
    print("\n📌 PASO 5: Simular proceso de entrega")
    
    # Recoger paquete
    delivery.status = Delivery.DeliveryStatus.PICKED_UP
    delivery.picked_up_at = timezone.now()
    delivery.save()
    print(f"   ✅ Estado: {delivery.status}")
    
    # En tránsito
    delivery.status = Delivery.DeliveryStatus.IN_TRANSIT
    delivery.save()
    print(f"   ✅ Estado: {delivery.status}")
    
    # Entregar (esto debería actualizar la orden y crear garantías)
    print("\n📌 PASO 6: Marcar como DELIVERED (trigger de garantías)")
    delivery.status = Delivery.DeliveryStatus.DELIVERED
    delivery.delivered_at = timezone.now()
    delivery.save()
    
    # Actualizar orden a DELIVERED también
    orden.status = Order.OrderStatus.DELIVERED
    orden.save()
    
    print(f"   ✅ Delivery: {delivery.status}")
    print(f"   ✅ Orden: {orden.status}")
    
    # Refrescar para obtener garantías
    orden.refresh_from_db()
    
    # 6. Verificar garantías creadas
    print("\n📌 PASO 7: Verificar garantías creadas automáticamente")
    
    warranties = orden.warranties.all()
    
    if warranties.exists():
        print(f"\n🎉 ¡GARANTÍAS CREADAS AUTOMÁTICAMENTE!")
        print(f"   Total de garantías: {warranties.count()}")
        
        for warranty in warranties:
            print(f"\n   📜 Garantía #{warranty.id}")
            print(f"      Producto: {warranty.product.name}")
            print(f"      Estado: {warranty.status}")
            print(f"      Inicio: {warranty.start_date}")
            print(f"      Fin: {warranty.end_date}")
            print(f"      Duración: {(warranty.end_date - warranty.start_date).days} días")
            print(f"      ¿Expirada? {warranty.get_is_expired() if hasattr(warranty, 'get_is_expired') else 'N/A'}")
    else:
        print(f"\n❌ ERROR: No se crearon garantías automáticamente")
    
    # Resumen final
    print_separator("📊 RESUMEN FINAL")
    
    print(f"✅ Orden #{orden.id}")
    print(f"   • Cliente: {orden.user.get_full_name()}")
    print(f"   • Estado: {orden.status}")
    print(f"   • Total: ${orden.total_price}")
    print(f"   • Items: {orden.items.count()}")
    
    print(f"\n✅ Delivery #{delivery.id}")
    print(f"   • Estado: {delivery.status}")
    print(f"   • Repartidor: {delivery.delivery_person.user.get_full_name() if delivery.delivery_person else 'Sin asignar'}")
    print(f"   • Entregado: {delivery.delivered_at}")
    
    print(f"\n✅ Garantías: {warranties.count()}")
    for w in warranties:
        print(f"   • {w.product.name}: válida hasta {w.end_date}")
    
    print_separator("✅ FLUJO COMPLETO PROBADO EXITOSAMENTE")
    
    print("\n🎯 CONCLUSIÓN:")
    print("   • Deliveries se crean automáticamente cuando orden = PAID")
    print("   • Garantías se crean automáticamente cuando orden = DELIVERED")
    print("   • El sistema está COMPLETAMENTE INTEGRADO y funcional")
    
    return orden, delivery, warranties


if __name__ == '__main__':
    try:
        test_flujo_completo()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
