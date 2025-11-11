"""
Signals para gestión automática de entregas y garantías.

Este módulo maneja la creación automática de:
1. Deliveries cuando una orden se marca como PAID
2. Warranties cuando una orden se marca como DELIVERED
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from shop_orders.models import Order
from .models import Delivery, Warranty


@receiver(post_save, sender=Order)
def create_delivery_on_paid_order(sender, instance, created, **kwargs):
    """
    Crear automáticamente un Delivery cuando una orden se marca como PAID.
    
    Flujo:
    1. Cliente paga → Orden status='PAID'
    2. Signal se dispara
    3. Se crea Delivery con status='PENDING'
    4. Manager puede entonces asignar un repartidor
    """
    # Solo crear delivery si la orden cambió a PAID y no tiene delivery ya
    if instance.status == Order.OrderStatus.PAID and not hasattr(instance, 'delivery'):
        # Obtener dirección del usuario (puedes personalizarlo)
        customer_address = getattr(instance.user, 'address', 'Dirección no especificada')
        customer_phone = getattr(instance.user, 'phone_number', 'Sin teléfono')
        
        # Crear el delivery
        Delivery.objects.create(
            order=instance,
            delivery_address=customer_address if customer_address else 'Dirección no especificada',
            customer_phone=customer_phone if customer_phone else 'Sin teléfono',
            status=Delivery.DeliveryStatus.PENDING,
            notes=f'Delivery creado automáticamente para orden #{instance.id}'
        )
        print(f'✅ Delivery creado automáticamente para orden #{instance.id}')


@receiver(post_save, sender=Order)
def create_warranties_on_delivered_order(sender, instance, **kwargs):
    """
    Crear automáticamente Warranties cuando una orden se marca como DELIVERED.
    
    Flujo:
    1. Repartidor marca delivery como completado → Orden status='DELIVERED'
    2. Signal se dispara
    3. Se crean garantías para cada producto en la orden
    4. Duración de garantía según warranty_info del producto
    """
    # Solo crear garantías si la orden está DELIVERED
    if instance.status == Order.OrderStatus.DELIVERED:
        # Verificar que no se hayan creado garantías ya
        if instance.warranties.exists():
            return  # Ya existen garantías, no duplicar
        
        # Crear garantía para cada item de la orden
        for item in instance.items.all():
            product = item.product
            
            if not product:
                continue  # Skip si el producto fue eliminado
            
            # Extraer duración de garantía del warranty_info (ej: "1 año de garantía")
            warranty_duration_days = extract_warranty_duration(product.warranty_info)
            
            # Calcular fecha de fin de garantía
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=warranty_duration_days)
            
            # Crear garantía
            Warranty.objects.create(
                order=instance,
                product=product,
                start_date=start_date,
                end_date=end_date,
                status=Warranty.WarrantyStatus.ACTIVE,
                terms=f'Garantía del fabricante: {product.warranty_info}. '
                      f'Válida por {warranty_duration_days} días desde la entrega. '
                      f'Cubre defectos de fábrica y mal funcionamiento.',
                notes=f'Garantía creada automáticamente al entregar orden #{instance.id}'
            )
        
        print(f'✅ Garantías creadas automáticamente para orden #{instance.id}')


def extract_warranty_duration(warranty_info):
    """
    Extraer duración de garantía en días desde el texto warranty_info.
    
    Ejemplos:
    - "1 año de garantía" → 365 días
    - "2 años de garantía" → 730 días
    - "6 meses de garantía" → 180 días
    - "90 días de garantía" → 90 días
    """
    if not warranty_info:
        return 365  # Default: 1 año
    
    warranty_text = warranty_info.lower()
    
    # Buscar años
    if 'año' in warranty_text or 'years' in warranty_text or 'year' in warranty_text:
        import re
        match = re.search(r'(\d+)\s*(año|year)', warranty_text)
        if match:
            years = int(match.group(1))
            return years * 365
    
    # Buscar meses
    if 'mes' in warranty_text or 'month' in warranty_text:
        import re
        match = re.search(r'(\d+)\s*(mes|month)', warranty_text)
        if match:
            months = int(match.group(1))
            return months * 30
    
    # Buscar días
    if 'día' in warranty_text or 'day' in warranty_text:
        import re
        match = re.search(r'(\d+)\s*(día|day)', warranty_text)
        if match:
            return int(match.group(1))
    
    # Default: 1 año si no se puede parsear
    return 365


# Señal para limpiar repartidor cuando delivery falla
@receiver(post_save, sender=Delivery)
def handle_delivery_status_change(sender, instance, **kwargs):
    """
    Manejar cambios de estado en deliveries.
    
    - Si falla: liberar repartidor
    - Si se entrega: actualizar orden a DELIVERED
    """
    if instance.status == Delivery.DeliveryStatus.FAILED:
        if instance.delivery_person and instance.delivery_person.status != 'AVAILABLE':
            instance.delivery_person.status = 'AVAILABLE'
            instance.delivery_person.save()
            print(f'✅ Repartidor {instance.delivery_person.user.username} liberado (delivery fallido)')

