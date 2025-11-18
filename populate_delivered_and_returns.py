"""
Script completo para:
1. Cambiar órdenes a estado DELIVERED
2. Crear devoluciones de ejemplo
3. Aprobar/rechazar algunas devoluciones
"""

import requests
import json
from datetime import datetime, timedelta

BACKEND_URL = "https://backend-2ex-ecommerce.onrender.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def get_admin_token():
    """Obtiene token JWT del admin"""
    print("🔑 Autenticando como admin...")
    
    response = requests.post(
        f"{BACKEND_URL}/token/",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    )
    
    if response.status_code == 200:
        token = response.json()["access"]
        print(f"✅ Token obtenido\n")
        return token
    else:
        print(f"❌ Error: {response.status_code}\n")
        return None


def change_orders_to_delivered(token, count=10):
    """Cambia órdenes a estado DELIVERED"""
    print("=" * 80)
    print("📦 PASO 1: Cambiando órdenes a DELIVERED")
    print("=" * 80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Obtener órdenes
    response = requests.get(
        f"{BACKEND_URL}/orders/admin/?page=1&page_size=100",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Error obteniendo órdenes: {response.status_code}")
        return []
    
    data = response.json()
    orders = data.get('results', data) if isinstance(data, dict) else data
    
    # Filtrar órdenes que NO sean DELIVERED o CANCELLED
    non_delivered = [o for o in orders if o.get('status') not in ['DELIVERED', 'CANCELLED']]
    
    print(f"\n📊 Órdenes disponibles: {len(non_delivered)}")
    print(f"🎯 Cambiando {min(count, len(non_delivered))} a DELIVERED...\n")
    
    delivered_orders = []
    
    for i, order in enumerate(non_delivered[:count], 1):
        order_id = order['id']
        old_status = order.get('status')
        
        # Cambiar a DELIVERED
        update_response = requests.post(
            f"{BACKEND_URL}/orders/admin/{order_id}/update_status/",
            headers=headers,
            json={"status": "DELIVERED"}
        )
        
        if update_response.status_code == 200:
            print(f"   {i}. ✅ Orden #{order_id}: {old_status} → DELIVERED")
            delivered_orders.append(order_id)
        else:
            print(f"   {i}. ❌ Orden #{order_id}: Error {update_response.status_code}")
    
    print(f"\n✅ {len(delivered_orders)} órdenes cambiadas a DELIVERED")
    return delivered_orders


def create_returns(token, order_ids):
    """Crea devoluciones para las órdenes"""
    print("\n" + "=" * 80)
    print("📦 PASO 2: Creando devoluciones")
    print("=" * 80)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Razones válidas según el modelo
    reasons_list = [
        ("DEFECTIVE", "El producto llegó con defectos de fábrica, no enciende correctamente"),
        ("WRONG_ITEM", "Recibí un producto diferente al que pedí, color equivocado"),
        ("NOT_AS_DESCRIBED", "El producto no coincide con la descripción del sitio web"),
        ("DEFECTIVE", "El producto llegó dañado por el envío, caja rota"),
        ("CHANGED_MIND", "Ya no necesito el producto, compré otro similar"),
        ("OTHER", "La talla no es la correcta, necesito una más grande"),
        ("OTHER", "La calidad no es la esperada, materiales de baja calidad"),
        ("DEFECTIVE", "No funciona correctamente, tiene fallas técnicas"),
        ("WRONG_ITEM", "Color incorrecto, pedí negro y llegó blanco"),
        ("NOT_AS_DESCRIBED", "Embalaje roto y producto dañado en transporte")
    ]
    
    created_returns = []
    
    # Primero obtener las órdenes completas para sacar los product_ids
    for i, order_id in enumerate(order_ids[:10], 1):
        # Obtener detalles de la orden para conseguir product_id
        order_response = requests.get(
            f"{BACKEND_URL}/orders/admin/{order_id}/",
            headers=headers
        )
        
        if order_response.status_code != 200:
            print(f"   {i}. ⚠️  No se pudo obtener orden #{order_id}")
            continue
        
        order_data = order_response.json()
        items = order_data.get('items', [])
        
        if not items:
            print(f"   {i}. ⚠️  Orden #{order_id} no tiene items")
            continue
        
        # Tomar el primer producto de la orden
        first_item = items[0]
        product_id = first_item.get('product', {}).get('id') if isinstance(first_item.get('product'), dict) else first_item.get('product')
        
        if not product_id:
            print(f"   {i}. ⚠️  No se pudo obtener product_id de orden #{order_id}")
            continue
        
        reason, description = reasons_list[i-1] if i-1 < len(reasons_list) else reasons_list[0]
        
        # Crear la devolución con order_id y product_id
        response = requests.post(
            f"{BACKEND_URL}/deliveries/returns/",
            headers=headers,
            json={
                "order_id": order_id,
                "product_id": product_id,
                "quantity": 1,
                "reason": reason,
                "description": description
            }
        )
        
        if response.status_code in [200, 201]:
            return_data = response.json()
            return_id = return_data.get('id')
            created_returns.append(return_id)
            print(f"   {i}. ✅ Devolución #{return_id} creada para orden #{order_id}")
            print(f"      Producto ID: {product_id}")
            print(f"      Razón: {reason}")
        else:
            print(f"   {i}. ❌ Error en orden #{order_id}: {response.status_code}")
            print(f"      {response.text[:200]}")
    
    print(f"\n✅ {len(created_returns)} devoluciones creadas")
    return created_returns


def approve_returns(token, return_ids, count=3):
    """Aprueba algunas devoluciones"""
    print("\n" + "=" * 80)
    print("✅ PASO 3: Aprobando devoluciones")
    print("=" * 80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    approved = 0
    for return_id in return_ids[:count]:
        response = requests.post(
            f"{BACKEND_URL}/deliveries/returns/{return_id}/approve/",
            headers=headers,
            json={"refund_method": "WALLET"}
        )
        
        if response.status_code in [200, 201]:
            approved += 1
            print(f"   ✅ Devolución #{return_id} aprobada (reembolso a WALLET)")
        else:
            print(f"   ⚠️  Devolución #{return_id}: Error {response.status_code}")
    
    print(f"\n✅ {approved} devoluciones aprobadas")


def reject_returns(token, return_ids, count=2):
    """Rechaza algunas devoluciones"""
    print("\n" + "=" * 80)
    print("❌ PASO 4: Rechazando devoluciones")
    print("=" * 80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    rejection_reasons = [
        "Fuera del período de devolución de 30 días",
        "El producto muestra signos de uso inadecuado",
        "No se puede verificar el defecto reportado",
        "Falta documentación requerida"
    ]
    
    # Saltar las primeras que fueron aprobadas
    to_reject = return_ids[count:]
    
    rejected = 0
    for i, return_id in enumerate(to_reject[:count]):
        reason = rejection_reasons[i % len(rejection_reasons)]
        
        response = requests.post(
            f"{BACKEND_URL}/deliveries/returns/{return_id}/reject/",
            headers=headers,
            json={"rejection_reason": reason}
        )
        
        if response.status_code in [200, 201]:
            rejected += 1
            print(f"   ❌ Devolución #{return_id} rechazada")
            print(f"      Motivo: {reason}")
        else:
            print(f"   ⚠️  Devolución #{return_id}: Error {response.status_code}")
    
    print(f"\n❌ {rejected} devoluciones rechazadas")


def show_final_summary(token):
    """Muestra resumen final"""
    print("\n" + "=" * 80)
    print("📊 RESUMEN FINAL")
    print("=" * 80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BACKEND_URL}/deliveries/returns/",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        returns = data.get('results', data) if isinstance(data, dict) else data
        
        if isinstance(returns, list):
            print(f"\n✅ Total devoluciones en BD: {len(returns)}")
            
            # Contar por estado
            by_status = {}
            by_reason = {}
            
            for r in returns:
                status = r.get('status', 'UNKNOWN')
                reason = r.get('reason', 'UNKNOWN')
                by_status[status] = by_status.get(status, 0) + 1
                by_reason[reason] = by_reason.get(reason, 0) + 1
            
            print("\n📊 Devoluciones por estado:")
            for status, count in sorted(by_status.items()):
                print(f"   {status}: {count}")
            
            print("\n📊 Devoluciones por razón:")
            for reason, count in sorted(by_reason.items()):
                print(f"   {reason}: {count}")
            
            # Mostrar ejemplos
            print("\n📋 Últimas 5 devoluciones:")
            for i, r in enumerate(returns[:5], 1):
                print(f"\n   {i}. Devolución #{r.get('id')}")
                print(f"      Orden: #{r.get('order')}")
                print(f"      Estado: {r.get('status')}")
                print(f"      Razón: {r.get('reason')}")
                print(f"      Creada: {r.get('created_at', '')[:19]}")


def main():
    print("=" * 80)
    print("🚀 POBLADO COMPLETO: ÓRDENES DELIVERED + DEVOLUCIONES")
    print("=" * 80)
    print(f"\n🌐 Backend: {BACKEND_URL}")
    print(f"👤 Usuario: {ADMIN_USERNAME}\n")
    
    # Autenticar
    token = get_admin_token()
    if not token:
        return
    
    # Paso 1: Cambiar órdenes a DELIVERED
    delivered_order_ids = change_orders_to_delivered(token, count=12)
    
    if not delivered_order_ids:
        print("\n❌ No se pudieron crear órdenes DELIVERED. Abortando.")
        return
    
    # Paso 2: Crear devoluciones
    return_ids = create_returns(token, delivered_order_ids)
    
    if not return_ids:
        print("\n❌ No se pudieron crear devoluciones. Abortando.")
        return
    
    # Paso 3: Aprobar algunas (primeras 3)
    approve_returns(token, return_ids, count=3)
    
    # Paso 4: Rechazar algunas (siguientes 2)
    reject_returns(token, return_ids, count=2)
    
    # Paso 5: Resumen final
    show_final_summary(token)
    
    print("\n" + "=" * 80)
    print("✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 80)
    print("\n📋 Ahora tienes:")
    print("   - ~12 órdenes en estado DELIVERED")
    print("   - ~10 devoluciones creadas")
    print("   - ~3 devoluciones APROBADAS")
    print("   - ~2 devoluciones RECHAZADAS")
    print("   - ~5 devoluciones PENDIENTES")
    print("\n🌐 Puedes verlas en:")
    print("   https://web-2ex.vercel.app/admin/returns")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
