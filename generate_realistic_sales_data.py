#!/usr/bin/env python
"""
Script para generar datos de ventas realistas con variaciones
Ejecutar: python generate_realistic_sales_data.py
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from users.models import CustomUser
from products.models import Product
from shop_orders.models import Order, OrderItem
from django.utils import timezone


def print_header(text):
    """Imprime un header colorido"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"✅ {text}")


def print_info(text):
    """Imprime mensaje informativo"""
    print(f"ℹ️  {text}")


def get_or_create_admin():
    """Obtiene o crea el usuario admin"""
    try:
        admin = CustomUser.objects.get(username='admin')
        return admin
    except CustomUser.DoesNotExist:
        admin = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@smartsales365.com',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema',
            role='ADMIN'
        )
        return admin


def get_sales_pattern(day_of_week, hour):
    """
    Retorna un multiplicador de ventas basado en patrones realistas:
    - Lunes a viernes: más ventas durante el día (9am-6pm)
    - Fines de semana: ventas distribuidas más uniformemente
    - Picos en viernes/sábado
    """
    # Patrón por día de la semana (0=Lunes, 6=Domingo)
    day_multipliers = {
        0: 0.9,   # Lunes - inicio de semana lento
        1: 1.0,   # Martes - normal
        2: 1.1,   # Miércoles - mejora
        3: 1.15,  # Jueves - buenas ventas
        4: 1.4,   # Viernes - pico pre-fin de semana
        5: 1.5,   # Sábado - PICO máximo
        6: 1.2,   # Domingo - buenas ventas pero menos que sábado
    }
    
    # Patrón por hora del día
    hour_multipliers = {
        range(0, 6): 0.1,    # Madrugada - casi nada
        range(6, 9): 0.5,    # Mañana temprano
        range(9, 12): 1.2,   # Media mañana - PICO
        range(12, 14): 1.0,  # Almuerzo
        range(14, 18): 1.3,  # Tarde - PICO MÁXIMO
        range(18, 21): 1.1,  # Noche
        range(21, 24): 0.7,  # Noche tardía
    }
    
    day_mult = day_multipliers.get(day_of_week, 1.0)
    
    hour_mult = 1.0
    for hour_range, mult in hour_multipliers.items():
        if hour in hour_range:
            hour_mult = mult
            break
    
    return day_mult * hour_mult


def generate_realistic_orders(days_back=120, min_orders_per_day=3, max_orders_per_day=15):
    """
    Genera órdenes con patrones realistas de ventas
    
    Args:
        days_back: Días hacia atrás desde hoy
        min_orders_per_day: Mínimo de órdenes por día
        max_orders_per_day: Máximo de órdenes por día
    """
    print_header("📊 GENERANDO DATOS REALISTAS DE VENTAS")
    
    # Obtener datos necesarios
    admin = get_or_create_admin()
    customers = list(CustomUser.objects.filter(role='CLIENTE'))
    products = list(Product.objects.all())
    
    if not customers:
        print_info("No hay clientes, creando algunos...")
        # Crear clientes de ejemplo
        for i in range(5):
            CustomUser.objects.create_user(
                username=f'cliente{i+1}',
                email=f'cliente{i+1}@email.com',
                password='cliente123',
                first_name=f'Cliente{i+1}',
                last_name='Prueba',
                role='CLIENTE'
            )
        customers = list(CustomUser.objects.filter(role='CLIENTE'))
    
    if not products:
        print_info("⚠️  No hay productos disponibles")
        return
    
    print_info(f"Clientes disponibles: {len(customers)}")
    print_info(f"Productos disponibles: {len(products)}")
    print_info(f"Generando {days_back} días de datos históricos...\n")
    
    # Productos populares (20% de productos tienen 60% de las ventas)
    num_popular = max(1, len(products) // 5)
    popular_products = random.sample(products, num_popular)
    
    total_orders_created = 0
    total_items_created = 0
    start_date = timezone.now() - timedelta(days=days_back)
    
    # Generar órdenes por cada día
    for day_offset in range(days_back):
        current_date = start_date + timedelta(days=day_offset)
        day_of_week = current_date.weekday()
        
        # Determinar cuántas órdenes crear este día basado en patrón semanal
        base_orders = random.randint(min_orders_per_day, max_orders_per_day)
        day_pattern = get_sales_pattern(day_of_week, 12)  # Usar mediodía como base
        num_orders = int(base_orders * day_pattern)
        num_orders = max(min_orders_per_day, min(num_orders, max_orders_per_day * 2))
        
        # Crear órdenes para este día
        for _ in range(num_orders):
            # Hora aleatoria del día
            hour = random.randint(6, 23)
            minute = random.randint(0, 59)
            order_time = current_date.replace(hour=hour, minute=minute)
            
            # Cliente aleatorio
            customer = random.choice(customers)
            
            # Crear orden
            order = Order.objects.create(
                user=customer,
                status='PAID',  # Todas pagadas para el modelo ML
            )
            # Modificar created_at manualmente
            order.created_at = order_time
            order.save()
            
            # Número de items por orden (1-5, con sesgo a 1-2)
            num_items = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5])[0]
            
            # Decidir si usar productos populares (70% de chance)
            use_popular = random.random() < 0.7
            available_products = popular_products if use_popular else products
            
            order_total = Decimal('0.00')
            
            # Crear items
            for _ in range(num_items):
                product = random.choice(available_products)
                
                # Cantidad: mayoría compra 1, algunos 2-3
                quantity = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
                
                # Precio con pequeña variación (promociones, etc)
                price_variation = random.uniform(0.85, 1.0)  # Hasta 15% descuento
                price = Decimal(str(float(product.price) * price_variation)).quantize(Decimal('0.01'))
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price
                )
                
                order_total += price * quantity
                total_items_created += 1
            
            # Actualizar total de la orden
            order.total_price = order_total
            order.save()
            
            total_orders_created += 1
        
        # Progreso cada 10 días
        if (day_offset + 1) % 10 == 0:
            progress = ((day_offset + 1) / days_back) * 100
            print(f"📈 Progreso: {progress:.1f}% - {total_orders_created} órdenes, {total_items_created} items")
    
    print_success(f"\n✨ Generación completada!")
    print_info(f"   • Total órdenes creadas: {total_orders_created}")
    print_info(f"   • Total items creados: {total_items_created}")
    print_info(f"   • Período: {days_back} días")
    print_info(f"   • Promedio: {total_orders_created / days_back:.1f} órdenes/día")


def add_seasonal_trends():
    """
    Añade tendencias estacionales y eventos especiales
    """
    print_header("🎯 AÑADIENDO TENDENCIAS ESTACIONALES")
    
    # Black Friday (último viernes de noviembre)
    # Cyber Monday (lunes siguiente)
    # Navidad (15-25 diciembre)
    # Año Nuevo (27-31 diciembre)
    
    current_date = timezone.now()
    orders = Order.objects.filter(status='PAID')
    
    # Identificar órdenes en fechas especiales y multiplicar items
    special_dates = []
    
    # Últimos 4 meses
    for order in orders.filter(created_at__gte=current_date - timedelta(days=120)):
        order_date = order.created_at
        
        # Black Friday (simulado como último viernes de noviembre)
        if order_date.month == 11 and order_date.weekday() == 4 and order_date.day >= 24:
            # Duplicar items para simular más ventas
            items = OrderItem.objects.filter(order=order)
            for item in items:
                # 50% chance de duplicar el item
                if random.random() < 0.5:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=random.randint(1, 2),
                        price=item.price * Decimal('0.9')  # 10% descuento
                    )
            special_dates.append(('Black Friday', order_date))
        
        # Navidad
        if order_date.month == 12 and 15 <= order_date.day <= 25:
            items = OrderItem.objects.filter(order=order)
            for item in items:
                if random.random() < 0.4:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=1,
                        price=item.price
                    )
            special_dates.append(('Navidad', order_date))
    
    # Recalcular totales de órdenes
    for order in orders:
        items = OrderItem.objects.filter(order=order)
        total = sum(item.price * item.quantity for item in items)
        order.total_price = total
        order.save()
    
    print_success(f"Tendencias estacionales añadidas: {len(set(special_dates))} fechas especiales")


def show_statistics():
    """Muestra estadísticas de los datos generados"""
    print_header("📊 ESTADÍSTICAS DE DATOS GENERADOS")
    
    total_orders = Order.objects.filter(status='PAID').count()
    total_items = OrderItem.objects.filter(order__status='PAID').count()
    total_revenue = sum(order.total_price for order in Order.objects.filter(status='PAID'))
    
    # Por día de la semana
    from django.db.models import Count, Sum
    from django.db.models.functions import ExtractWeekDay
    
    days_map = {
        1: 'Domingo',
        2: 'Lunes',
        3: 'Martes',
        4: 'Miércoles',
        5: 'Jueves',
        6: 'Viernes',
        7: 'Sábado',
    }
    
    print_info(f"📦 Total órdenes PAID: {total_orders}")
    print_info(f"📝 Total items vendidos: {total_items}")
    print_info(f"💰 Ingresos totales: ${total_revenue:.2f}")
    print_info(f"💵 Ticket promedio: ${total_revenue / total_orders:.2f}\n")
    
    print("📅 Ventas por día de la semana:")
    
    orders_by_day = Order.objects.filter(status='PAID').annotate(
        weekday=ExtractWeekDay('created_at')
    ).values('weekday').annotate(
        count=Count('id'),
        total=Sum('total_price')
    ).order_by('weekday')
    
    for day_data in orders_by_day:
        day_name = days_map.get(day_data['weekday'], 'Desconocido')
        count = day_data['count']
        total = day_data['total'] or 0
        avg = total / count if count > 0 else 0
        bar = '█' * int(count / 10)
        print(f"   {day_name:10s}: {count:4d} órdenes  ${avg:6.2f} promedio  {bar}")


def train_model():
    """Entrena el modelo de predicción con los nuevos datos"""
    print_header("🤖 ENTRENANDO MODELO DE MACHINE LEARNING")
    
    from predictions.services import train_sales_prediction_model
    
    print_info("Iniciando entrenamiento...")
    
    try:
        result = train_sales_prediction_model()
        
        if result['status'] == 'success':
            print_success("Modelo entrenado exitosamente!")
            print_info(f"   • Archivo: {result['path']}")
            print_info(f"   • Error cuadrático medio (MSE): {result['mse']:.4f}")
            print_info(f"   • Muestras usadas: {result['n_samples']}")
        else:
            print(f"⚠️  {result['message']}")
    except Exception as e:
        print(f"❌ Error entrenando modelo: {str(e)}")


def main():
    """Función principal"""
    print_header("🚀 GENERADOR DE DATOS REALISTAS DE VENTAS")
    print_info("Este script generará datos históricos con patrones realistas")
    print_info("Incluye variaciones por día de la semana, hora del día y tendencias")
    
    try:
        # Preguntar al usuario
        print("\n" + "─" * 80)
        print("📋 OPCIONES:")
        print("─" * 80)
        print("  1. Generar 30 días de datos (rápido - para pruebas)")
        print("  2. Generar 60 días de datos (medio - recomendado)")
        print("  3. Generar 120 días de datos (completo - 4 meses)")
        print("  4. Solo entrenar modelo con datos existentes")
        print("  0. Salir")
        print("─" * 80)
        
        opcion = input("\n👉 Selecciona una opción: ").strip()
        
        if opcion == '0':
            print_info("Script cancelado")
            return
        
        if opcion == '1':
            generate_realistic_orders(days_back=30, min_orders_per_day=5, max_orders_per_day=20)
            add_seasonal_trends()
            show_statistics()
            train_model()
        elif opcion == '2':
            generate_realistic_orders(days_back=60, min_orders_per_day=5, max_orders_per_day=20)
            add_seasonal_trends()
            show_statistics()
            train_model()
        elif opcion == '3':
            generate_realistic_orders(days_back=120, min_orders_per_day=5, max_orders_per_day=20)
            add_seasonal_trends()
            show_statistics()
            train_model()
        elif opcion == '4':
            show_statistics()
            train_model()
        else:
            print("❌ Opción inválida")
            return
        
        print_header("✅ PROCESO COMPLETADO")
        print_info("Ahora puedes probar las predicciones en:")
        print_info("   • Backend: GET /api/predictions/sales/")
        print_info("   • Frontend React: /predictions")
        print_info("   • Postman con token de admin")
        
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print_info("Script interrumpido por el usuario")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
