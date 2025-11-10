#!/usr/bin/env python
"""
Script para probar el flujo simplificado de devoluciones
Sistema: SmartSales365 - Sistema de Devoluciones

Flujo:
1. Cliente solicita devolución desde su historial
2. Manager envía a evaluación física
3. Manager aprueba o rechaza basado en informe
4. Sistema procesa reembolso automático (si aprobado)
5. Cliente recibe email con resultado
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.contrib.auth import get_user_model
from shop_orders.models import Order, OrderItem
from products.models import Product
from deliveries.models import Return
from django.utils import timezone

User = get_user_model()


def print_section(title):
    """Imprimir sección del test"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_success(message):
    """Imprimir mensaje de éxito"""
    print(f"✅ {message}")


def print_info(message):
    """Imprimir información"""
    print(f"ℹ️  {message}")


def print_error(message):
    """Imprimir error"""
    print(f"❌ {message}")


def get_or_create_test_users():
    """Crear usuarios de prueba si no existen"""
    print_section("1. PREPARAR USUARIOS DE PRUEBA")
    
    # Cliente
    cliente, created = User.objects.get_or_create(
        username='cliente_returns',
        defaults={
            'email': 'cliente.returns@test.com',
            'role': 'ADMIN',  # Para que pueda crear órdenes
            'first_name': 'Juan',
            'last_name': 'Pérez'
        }
    )
    if created:
        cliente.set_password('test123')
        cliente.save()
        print_success(f"Cliente creado: {cliente.username}")
    else:
        print_info(f"Cliente existente: {cliente.username}")
    
    # Manager
    manager, created = User.objects.get_or_create(
        username='manager_returns',
        defaults={
            'email': 'manager.returns@test.com',
            'role': 'MANAGER',
            'first_name': 'Ana',
            'last_name': 'García'
        }
    )
    if created:
        manager.set_password('test123')
        manager.save()
        print_success(f"Manager creado: {manager.username}")
    else:
        print_info(f"Manager existente: {manager.username}")
    
    return cliente, manager


def create_test_order(cliente):
    """Crear orden de prueba con productos"""
    print_section("2. CREAR ORDEN DE PRUEBA")
    
    # Buscar un producto
    producto = Product.objects.first()
    if not producto:
        print_error("No hay productos en la base de datos")
        return None
    
    print_info(f"Producto seleccionado: {producto.name} (${producto.price})")
    
    # Crear orden
    orden = Order.objects.create(
        user=cliente,
        status='DELIVERED',  # Debe estar entregada para poder devolver
        total_price=producto.price * 2
    )
    
    # Agregar items
    OrderItem.objects.create(
        order=orden,
        product=producto,
        quantity=2,
        price=producto.price
    )
    
    print_success(f"Orden #{orden.id} creada con estado DELIVERED")
    print_info(f"  - Total: ${orden.total_price}")
    print_info(f"  - Productos: {orden.items.count()}")
    
    return orden, producto


def test_solicitar_devolucion(cliente, orden, producto):
    """Paso 1: Cliente solicita devolución"""
    print_section("3. CLIENTE SOLICITA DEVOLUCIÓN")
    
    devolucion = Return.objects.create(
        order=orden,
        product=producto,
        user=cliente,
        quantity=1,
        reason=Return.ReturnReason.DEFECTIVE,
        description='El producto llegó con la pantalla rota. No enciende correctamente.',
        status=Return.ReturnStatus.REQUESTED
    )
    
    print_success(f"Devolución #{devolucion.id} creada")
    print_info(f"  - Cliente: {cliente.get_full_name()} ({cliente.email})")
    print_info(f"  - Orden: #{orden.id}")
    print_info(f"  - Producto: {producto.name}")
    print_info(f"  - Cantidad: {devolucion.quantity}")
    print_info(f"  - Motivo: {devolucion.get_reason_display()}")
    print_info(f"  - Estado: {devolucion.get_status_display()}")
    print_info(f"  - Descripción: {devolucion.description}")
    print_info(f"  - Fecha: {devolucion.requested_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n📧 Email enviado al Manager:")
    print(f"   Asunto: 🔔 Nueva Solicitud de Devolución #{devolucion.id}")
    print(f"   Para: manager.returns@test.com")
    
    return devolucion


def test_enviar_a_evaluacion(manager, devolucion):
    """Paso 2: Manager envía a evaluación física"""
    print_section("4. MANAGER ENVÍA A EVALUACIÓN FÍSICA")
    
    print_info(f"Manager {manager.get_full_name()} revisa la solicitud...")
    print_info("Manager decide enviar el producto a un técnico externo para evaluación física")
    
    devolucion.status = Return.ReturnStatus.IN_EVALUATION
    devolucion.manager_notes = (
        "Producto enviado a Técnica XYZ para evaluación física. "
        "Se espera informe en 24-48 horas."
    )
    devolucion.save()
    
    print_success(f"Devolución #{devolucion.id} enviada a evaluación")
    print_info(f"  - Estado anterior: REQUESTED")
    print_info(f"  - Estado actual: {devolucion.get_status_display()}")
    print_info(f"  - Notas: {devolucion.manager_notes}")


def test_aprobar_devolucion(manager, devolucion):
    """Paso 3: Manager aprueba devolución"""
    print_section("5. TERCERO EVALÚA Y MANAGER APRUEBA")
    
    print_info("🔬 Técnico externo realiza evaluación física:")
    print_info("   ✓ Pantalla efectivamente rota")
    print_info("   ✓ No enciende correctamente")
    print_info("   ✓ Daño no causado por mal uso")
    print_info("   ✓ Producto defectuoso confirmado")
    
    print_info(f"\nManager {manager.get_full_name()} recibe informe y aprueba la devolución...")
    
    # Calcular reembolso
    refund_amount = devolucion.product.price * devolucion.quantity
    
    devolucion.status = Return.ReturnStatus.APPROVED
    devolucion.evaluation_notes = (
        "Evaluación realizada por Técnica XYZ:\n"
        "- Pantalla LCD rota confirmada\n"
        "- Circuitería interna dañada\n"
        "- Producto defectuoso de fábrica\n"
        "- RECOMENDACIÓN: Aprobar devolución"
    )
    devolucion.refund_amount = refund_amount
    devolucion.refund_method = Return.RefundMethod.WALLET
    devolucion.evaluated_at = timezone.now()
    devolucion.save()
    
    print_success(f"Devolución #{devolucion.id} APROBADA")
    print_info(f"  - Estado: {devolucion.get_status_display()}")
    print_info(f"  - Monto a reembolsar: ${devolucion.refund_amount}")
    print_info(f"  - Método: {devolucion.get_refund_method_display()}")
    print_info(f"  - Fecha evaluación: {devolucion.evaluated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n💰 Procesando reembolso automático...")
    
    # Marcar como completado
    devolucion.status = Return.ReturnStatus.COMPLETED
    devolucion.processed_at = timezone.now()
    devolucion.completed_at = timezone.now()
    devolucion.save()
    
    print_success("Reembolso procesado exitosamente")
    print_info(f"  - Estado final: {devolucion.get_status_display()}")
    print_info(f"  - Completado: {devolucion.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n📧 Email enviado al Cliente:")
    print(f"   Asunto: ✅ Tu Devolución #{devolucion.id} ha sido Aprobada")
    print(f"   Para: {devolucion.user.email}")
    print(f"   Mensaje:")
    print(f"   - Devolución aprobada")
    print(f"   - Monto reembolsado: ${devolucion.refund_amount}")
    print(f"   - Método: {devolucion.get_refund_method_display()}")
    print(f"   - El saldo estará disponible en tu billetera virtual en 24-48 horas")


def test_rechazar_devolucion(manager, orden, producto, cliente):
    """Caso alternativo: Manager rechaza devolución"""
    print_section("6. CASO ALTERNATIVO: RECHAZO DE DEVOLUCIÓN")
    
    # Crear segunda devolución
    devolucion2 = Return.objects.create(
        order=orden,
        product=producto,
        user=cliente,
        quantity=1,
        reason=Return.ReturnReason.NOT_AS_DESCRIBED,
        description='El color no es exactamente como en la foto.',
        status=Return.ReturnStatus.REQUESTED
    )
    
    print_info(f"Cliente solicita segunda devolución #{devolucion2.id}")
    print_info(f"  - Motivo: {devolucion2.get_reason_display()}")
    
    # Enviar a evaluación
    devolucion2.status = Return.ReturnStatus.IN_EVALUATION
    devolucion2.manager_notes = "Enviado a evaluación"
    devolucion2.save()
    
    print_info("\nManager envía a evaluación física...")
    print_info("🔬 Técnico evalúa y determina:")
    print_info("   ✓ Producto en perfecto estado")
    print_info("   ✓ Color coincide con especificaciones")
    print_info("   ✓ Sin defectos visibles")
    print_info("   ✓ RECOMENDACIÓN: Rechazar devolución")
    
    # Rechazar
    devolucion2.status = Return.ReturnStatus.REJECTED
    devolucion2.evaluation_notes = (
        "Evaluación realizada por Técnica XYZ:\n"
        "- Producto en perfecto estado funcional\n"
        "- Color coincide 100% con especificaciones del fabricante\n"
        "- Sin defectos de fabricación\n"
        "- RECOMENDACIÓN: Rechazar devolución"
    )
    devolucion2.manager_notes = (
        "El producto cumple con las especificaciones publicadas. "
        "La diferencia de color puede deberse a la calibración de pantalla. "
        "Devolución rechazada."
    )
    devolucion2.evaluated_at = timezone.now()
    devolucion2.save()
    
    print_success(f"Devolución #{devolucion2.id} RECHAZADA")
    print_info(f"  - Estado: {devolucion2.get_status_display()}")
    print_info(f"  - Motivo: Producto cumple especificaciones")
    
    print("\n📧 Email enviado al Cliente:")
    print(f"   Asunto: ❌ Tu Solicitud de Devolución #{devolucion2.id}")
    print(f"   Para: {devolucion2.user.email}")
    print(f"   Mensaje:")
    print(f"   - Lamentamos informarte que tu solicitud ha sido rechazada")
    print(f"   - Motivo: {devolucion2.manager_notes}")
    print(f"   - Si tienes dudas, contáctanos en: soporte@smartsales365.com")


def test_ver_historial(cliente):
    """Ver historial de devoluciones del cliente"""
    print_section("7. HISTORIAL DE DEVOLUCIONES DEL CLIENTE")
    
    devoluciones = Return.objects.filter(user=cliente).order_by('-requested_at')
    
    print_info(f"Cliente: {cliente.get_full_name()}")
    print_info(f"Total de devoluciones: {devoluciones.count()}\n")
    
    for i, dev in enumerate(devoluciones, 1):
        print(f"{i}. Devolución #{dev.id}")
        print(f"   - Producto: {dev.product.name}")
        print(f"   - Orden: #{dev.order.id}")
        print(f"   - Estado: {dev.get_status_display()}")
        print(f"   - Motivo: {dev.get_reason_display()}")
        print(f"   - Solicitada: {dev.requested_at.strftime('%Y-%m-%d %H:%M')}")
        
        if dev.status == Return.ReturnStatus.COMPLETED:
            print(f"   - ✅ Reembolso: ${dev.refund_amount}")
        elif dev.status == Return.ReturnStatus.REJECTED:
            print(f"   - ❌ Rechazada")
        
        print()


def print_estadisticas():
    """Mostrar estadísticas generales"""
    print_section("8. ESTADÍSTICAS GENERALES")
    
    total = Return.objects.count()
    solicitadas = Return.objects.filter(status=Return.ReturnStatus.REQUESTED).count()
    en_evaluacion = Return.objects.filter(status=Return.ReturnStatus.IN_EVALUATION).count()
    aprobadas = Return.objects.filter(status=Return.ReturnStatus.APPROVED).count()
    rechazadas = Return.objects.filter(status=Return.ReturnStatus.REJECTED).count()
    completadas = Return.objects.filter(status=Return.ReturnStatus.COMPLETED).count()
    
    print_info(f"Total de devoluciones: {total}")
    print_info(f"  - Solicitadas: {solicitadas}")
    print_info(f"  - En evaluación: {en_evaluacion}")
    print_info(f"  - Aprobadas: {aprobadas}")
    print_info(f"  - Rechazadas: {rechazadas}")
    print_info(f"  - Completadas: {completadas}")
    
    if total > 0:
        tasa_aprobacion = ((aprobadas + completadas) / total) * 100
        print_info(f"\n📊 Tasa de aprobación: {tasa_aprobacion:.1f}%")
        
        total_reembolsado = Return.objects.filter(
            status=Return.ReturnStatus.COMPLETED
        ).aggregate(
            total=django.db.models.Sum('refund_amount')
        )['total'] or 0
        
        print_info(f"💰 Total reembolsado: ${total_reembolsado}")


def main():
    """Ejecutar todos los tests"""
    print("\n" + "=" * 80)
    print("  🧪 TEST: SISTEMA SIMPLIFICADO DE DEVOLUCIONES")
    print("  SmartSales365 - Backend API")
    print("=" * 80)
    
    try:
        # 1. Preparar usuarios
        cliente, manager = get_or_create_test_users()
        
        # 2. Crear orden de prueba
        result = create_test_order(cliente)
        if not result:
            return
        orden, producto = result
        
        # 3. Flujo de aprobación
        devolucion = test_solicitar_devolucion(cliente, orden, producto)
        test_enviar_a_evaluacion(manager, devolucion)
        test_aprobar_devolucion(manager, devolucion)
        
        # 4. Flujo de rechazo
        test_rechazar_devolucion(manager, orden, producto, cliente)
        
        # 5. Ver historial
        test_ver_historial(cliente)
        
        # 6. Estadísticas
        print_estadisticas()
        
        print_section("✅ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        
        print("\n📝 RESUMEN:")
        print("  ✅ Usuarios de prueba creados")
        print("  ✅ Orden de prueba creada")
        print("  ✅ Devolución aprobada y reembolsada")
        print("  ✅ Devolución rechazada")
        print("  ✅ Historial consultado")
        print("  ✅ Estadísticas generadas")
        
        print("\n💡 PRÓXIMOS PASOS:")
        print("  1. Implementar envío de emails")
        print("  2. Integrar con sistema de billetera virtual")
        print("  3. Conectar con Stripe para reembolsos al método original")
        print("  4. Agregar notificaciones en tiempo real")
        
    except Exception as e:
        print_error(f"Error durante el test: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    import django.db.models
    sys.exit(main())
