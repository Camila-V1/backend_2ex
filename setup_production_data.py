#!/usr/bin/env python
"""
Script para ejecutar en producción (Render) vía Django shell
Genera datos realistas y entrena el modelo ML

EJECUTAR EN RENDER:
1. Ir a Shell en dashboard de Render
2. Copiar y pegar este código
3. Ejecutar
"""

import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from users.models import CustomUser
from products.models import Product
from shop_orders.models import Order, OrderItem

print("\n" + "=" * 80)
print("  🚀 GENERANDO DATOS REALISTAS EN PRODUCCIÓN")
print("=" * 80 + "\n")

# 1. Obtener datos base
customers = list(CustomUser.objects.filter(role='CLIENTE')[:5])
products = list(Product.objects.all())

if not customers:
    print("⚠️  No hay clientes CLIENTE, usando cualquier usuario")
    customers = list(CustomUser.objects.all()[:5])

if not products:
    print("❌ No hay productos")
    exit()

print(f"✅ Clientes: {len(customers)}")
print(f"✅ Productos: {len(products)}")

# 2. Patrones de ventas
def get_pattern(weekday):
    patterns = {0: 0.9, 1: 1.0, 2: 1.1, 3: 1.15, 4: 1.4, 5: 1.5, 6: 1.2}
    return patterns.get(weekday, 1.0)

# 3. Productos populares (20%)
num_popular = max(1, len(products) // 5)
popular_products = random.sample(products, num_popular)

# 4. Generar 60 días de datos
days = 60
start_date = timezone.now() - timedelta(days=days)
created = 0

print(f"\n📊 Generando {days} días de datos...")

for day_offset in range(days):
    current_date = start_date + timedelta(days=day_offset)
    weekday = current_date.weekday()
    
    # 8-20 órdenes por día con patrón semanal
    base_orders = random.randint(8, 20)
    num_orders = int(base_orders * get_pattern(weekday))
    
    for _ in range(num_orders):
        customer = random.choice(customers)
        hour = random.randint(6, 23)
        order_time = current_date.replace(hour=hour, minute=random.randint(0, 59))
        
        order = Order.objects.create(
            user=customer,
            status='PAID'
        )
        order.created_at = order_time
        order.save()
        
        # 1-3 items por orden
        num_items = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
        use_popular = random.random() < 0.7
        available = popular_products if use_popular else products
        
        total = Decimal('0.00')
        for _ in range(num_items):
            product = random.choice(available)
            quantity = random.choices([1, 2, 3], weights=[70, 20, 10])[0]
            price = Decimal(str(float(product.price) * random.uniform(0.85, 1.0))).quantize(Decimal('0.01'))
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )
            total += price * quantity
        
        order.total_price = total
        order.save()
        created += 1
    
    if (day_offset + 1) % 10 == 0:
        print(f"  Día {day_offset + 1}/{days}: {created} órdenes")

print(f"\n✅ Total órdenes creadas: {created}")

# 5. Entrenar modelo
print("\n🤖 Entrenando modelo ML...")
from predictions.services import train_sales_prediction_model

result = train_sales_prediction_model()
if result.get('status'):
    print(f"✅ Modelo entrenado!")
    print(f"   MSE: {result.get('mse', 0):.4f}")
    print(f"   Muestras: {result.get('n_samples', 0)}")
else:
    print(f"❌ Error: {result.get('message', 'Unknown')}")

print("\n" + "=" * 80)
print("✅ COMPLETADO - Recarga el frontend")
print("=" * 80 + "\n")
