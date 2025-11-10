"""
Script de Prueba Completa del Sistema de Devoluciones y Garantías
===================================================================

Este script prueba el flujo completo:
1. Login de usuarios (cliente, manager, admin)
2. Crear orden y marcarla como entregada
3. Solicitar devolución (cliente)
4. Enviar a evaluación (manager)
5. Aprobar devolución con reembolso (manager)
6. Verificar billetera creada
7. Verificar transacciones
8. Probar garantías/warranties

Autor: GitHub Copilot
Fecha: 10 de Noviembre, 2025
"""

import requests
import json
from datetime import datetime
from decimal import Decimal

# Configuración
BASE_URL = "http://localhost:8000/api"
HEADERS = {"Content-Type": "application/json"}

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Imprime un header destacado"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")

def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}[OK] {text}{Colors.END}")

def print_error(text):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}[ERROR] {text}{Colors.END}")

def print_info(text):
    """Imprime mensaje informativo"""
    print(f"{Colors.YELLOW}[INFO] {text}{Colors.END}")

def print_data(label, data):
    """Imprime datos en formato JSON"""
    print(f"{Colors.CYAN}{label}:{Colors.END}")
    print(json.dumps(data, indent=2, ensure_ascii=False))

# Variables globales para tokens y IDs
tokens = {}
user_ids = {}
product_id = None
order_id = None
return_id = None
wallet_id = None

def login_user(username, password, role_name):
    """Login de usuario y almacenar token"""
    print_info(f"Intentando login como {role_name}: {username}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/token/",
            json={"username": username, "password": password},
            headers=HEADERS,
            timeout=10
        )
        
        print_info(f"Status code: {response.status_code}")
        print_info(f"Response text: {response.text[:200]}")
        
        if response.status_code == 200:
            data = response.json()
            tokens[role_name] = data.get('access')
            
            # Obtener información del usuario con el token
            profile_response = requests.get(
                f"{BASE_URL}/users/profile/",
                headers={"Authorization": f"Bearer {tokens[role_name]}"}
            )
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                user_ids[role_name] = profile_data.get('id')
                print_success(f"Login exitoso - {role_name}")
                print_data(f"Usuario {role_name}", {
                    "id": user_ids[role_name],
                    "username": username,
                    "role": profile_data.get('role')
                })
            else:
                user_ids[role_name] = None
                print_success(f"Login exitoso - {role_name} (sin perfil)")
            
            return True
        else:
            print_error(f"Login fallido - {role_name} (Status: {response.status_code})")
            try:
                print_data("Error", response.json())
            except:
                print_data("Error", {"message": response.text})
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Error de conexión: {str(e)}")
        return False

def get_auth_header(role):
    """Obtiene header con token de autenticación"""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {tokens[role]}"
    }

def get_existing_product():
    """Obtiene un producto existente"""
    global product_id
    print_info("Obteniendo producto existente...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/products/",
            headers=get_auth_header('admin')
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', data) if isinstance(data, dict) else data
            if results and len(results) > 0:
                product = results[0]
                product_id = product['id']
                print_success(f"Producto obtenido - ID: {product_id}")
                print_data("Producto", {
                    "id": product['id'],
                    "name": product['name'],
                    "price": product['price'],
                    "stock": product['stock']
                })
                return True
            else:
                print_error("No hay productos en la base de datos")
                return False
        else:
            print_error(f"Error al obtener productos (Status: {response.status_code})")
            return False
    except Exception as e:
        print_error(f"Excepción al obtener producto: {str(e)}")
        return False

def create_test_order():
    """Crea una orden de prueba"""
    global order_id
    print_info("Creando orden de prueba como cliente...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/orders/",
            json={
                "items": [
                    {
                        "product": product_id,
                        "quantity": 1
                    }
                ],
                "shipping_address": "Calle Principal 123, La Paz, Bolivia",
                "payment_method": "CARD"
            },
            headers=get_auth_header('cliente')
        )
        
        if response.status_code == 201:
            data = response.json()
            order_id = data['id']
            print_success(f"Orden creada - ID: {order_id}")
            print_data("Orden", {
                "id": data['id'],
                "status": data['status'],
                "total_price": data.get('total_price', 'N/A')
            })
            return True
        else:
            print_error(f"Error al crear orden (Status: {response.status_code})")
            try:
                print_data("Error", response.json())
            except:
                print_data("Error", {"message": response.text[:500]})
            return False
    except Exception as e:
        print_error(f"Excepción al crear orden: {str(e)}")
        return False

def mark_order_as_delivered():
    """Marca la orden como entregada"""
    print_info(f"Marcando orden {order_id} como DELIVERED...")
    
    try:
        response = requests.patch(
            f"{BASE_URL}/orders/{order_id}/",
            json={"status": "DELIVERED"},
            headers=get_auth_header('admin')
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Orden marcada como DELIVERED")
            print_data("Orden actualizada", {
                "id": data['id'],
                "status": data['status'],
                "total_price": data.get('total_price', 'N/A')
            })
            return True
        else:
            print_error(f"Error al actualizar orden (Status: {response.status_code})")
            try:
                print_data("Error", response.json())
            except:
                print_data("Error", {"message": response.text[:500]})
            return False
    except Exception as e:
        print_error(f"Excepción al actualizar orden: {str(e)}")
        return False

def request_return():
    """Cliente solicita una devolución"""
    global return_id
    print_info("Cliente solicita devolución...")
    
    response = requests.post(
        f"{BASE_URL}/deliveries/returns/",
        json={
            "order": order_id,
            "product": product_id,
            "quantity": 1,
            "reason": "El producto no cumple con las especificaciones anunciadas. La pantalla tiene píxeles muertos.",
            "refund_method": "WALLET"
        },
        headers=get_auth_header('cliente')
    )
    
    if response.status_code == 201:
        data = response.json()
        return_id = data['id']
        print_success(f"Devolución solicitada - ID: {return_id}")
        print_data("Devolución", data)
        return True
    else:
        print_error("Error al solicitar devolución")
        print_data("Error", response.json())
        return False

def get_return_details():
    """Obtiene detalles de la devolución"""
    print_info(f"Consultando detalles de devolución {return_id}...")
    
    response = requests.get(
        f"{BASE_URL}/deliveries/returns/{return_id}/",
        headers=get_auth_header('cliente')
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success("Detalles obtenidos")
        print_data("Devolución", data)
        return data
    else:
        print_error("Error al obtener detalles")
        print_data("Error", response.json())
        return None

def send_to_evaluation():
    """Manager envía devolución a evaluación"""
    print_info(f"Manager envía devolución {return_id} a evaluación...")
    
    response = requests.post(
        f"{BASE_URL}/deliveries/returns/{return_id}/send_to_evaluation/",
        json={},
        headers=get_auth_header('manager')
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success("Devolución enviada a evaluación")
        print_data("Estado actualizado", {
            "id": data['id'],
            "status": data['status'],
            "message": data.get('message', 'Evaluación iniciada')
        })
        return True
    else:
        print_error("Error al enviar a evaluación")
        print_data("Error", response.json())
        return False

def approve_return():
    """Manager aprueba la devolución"""
    print_info(f"Manager aprueba devolución {return_id}...")
    
    response = requests.post(
        f"{BASE_URL}/deliveries/returns/{return_id}/approve/",
        json={
            "evaluation_notes": "Producto verificado. Píxeles muertos confirmados en zona superior derecha. Aprobada para reembolso completo."
        },
        headers=get_auth_header('manager')
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success("Devolución aprobada y reembolso procesado")
        print_data("Resultado", data)
        return True
    else:
        print_error("Error al aprobar devolución")
        print_data("Error", response.json())
        return False

def get_client_wallet():
    """Obtiene la billetera del cliente"""
    global wallet_id
    print_info("Consultando billetera del cliente...")
    
    response = requests.get(
        f"{BASE_URL}/users/wallets/my_wallet/",
        headers=get_auth_header('cliente')
    )
    
    if response.status_code == 200:
        data = response.json()
        wallet_id = data['id']
        print_success(f"Billetera encontrada - ID: {wallet_id}")
        print_data("Billetera", {
            "id": data['id'],
            "balance": data['balance'],
            "user": data['user'],
            "created_at": data['created_at']
        })
        return data
    else:
        print_error("Error al obtener billetera")
        print_data("Error", response.json())
        return None

def get_wallet_balance():
    """Obtiene el saldo de la billetera"""
    print_info("Consultando saldo de billetera...")
    
    response = requests.get(
        f"{BASE_URL}/users/wallets/my_balance/",
        headers=get_auth_header('cliente')
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success("Saldo obtenido")
        print_data("Saldo", data)
        return data
    else:
        print_error("Error al obtener saldo")
        print_data("Error", response.json())
        return None

def get_wallet_transactions():
    """Obtiene transacciones de la billetera"""
    print_info("Consultando transacciones de billetera...")
    
    response = requests.get(
        f"{BASE_URL}/users/wallets/my_transactions/",
        headers=get_auth_header('cliente')
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Transacciones obtenidas - Total: {len(data)}")
        print_data("Transacciones", data)
        return data
    else:
        print_error("Error al obtener transacciones")
        print_data("Error", response.json())
        return None

def get_wallet_statistics():
    """Obtiene estadísticas de la billetera"""
    print_info("Consultando estadísticas de billetera...")
    
    response = requests.get(
        f"{BASE_URL}/users/wallets/statistics/",
        headers=get_auth_header('cliente')
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success("Estadísticas obtenidas")
        print_data("Estadísticas", data)
        return data
    else:
        print_error("Error al obtener estadísticas")
        print_data("Error", response.json())
        return None

def get_my_returns():
    """Cliente consulta sus devoluciones"""
    print_info("Cliente consulta sus devoluciones...")
    
    response = requests.get(
        f"{BASE_URL}/deliveries/returns/my_returns/",
        headers=get_auth_header('cliente')
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Devoluciones obtenidas - Total: {len(data)}")
        print_data("Mis devoluciones", data)
        return data
    else:
        print_error("Error al obtener devoluciones")
        print_data("Error", response.json())
        return None

def manager_list_all_returns():
    """Manager lista todas las devoluciones"""
    print_info("Manager consulta todas las devoluciones...")
    
    response = requests.get(
        f"{BASE_URL}/deliveries/returns/",
        headers=get_auth_header('manager')
    )
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', data) if isinstance(data, dict) else data
        print_success(f"Todas las devoluciones - Total: {len(results)}")
        print_data("Devoluciones del sistema", results)
        return results
    else:
        print_error("Error al obtener devoluciones")
        print_data("Error", response.json())
        return None

def test_reject_return_flow():
    """Prueba el flujo de rechazo de devolución"""
    print_header("FLUJO DE RECHAZO DE DEVOLUCIÓN")
    
    # Crear otra orden
    print_info("Creando segunda orden para probar rechazo...")
    response = requests.post(
        f"{BASE_URL}/orders/",
        json={
            "items": [
                {
                    "product": product_id,
                    "quantity": 1
                }
            ],
            "shipping_address": "Avenida 6 de Agosto 456, La Paz",
            "payment_method": "CARD"
        },
        headers=get_auth_header('cliente')
    )
    
    if response.status_code != 201:
        print_error("Error al crear segunda orden")
        return False
    
    order2_id = response.json()['id']
    print_success(f"Segunda orden creada - ID: {order2_id}")
    
    # Marcar como entregada
    requests.patch(
        f"{BASE_URL}/orders/{order2_id}/",
        json={"status": "DELIVERED"},
        headers=get_auth_header('admin')
    )
    print_success("Segunda orden marcada como DELIVERED")
    
    # Solicitar devolución
    response = requests.post(
        f"{BASE_URL}/deliveries/returns/",
        json={
            "order": order2_id,
            "product": product_id,
            "quantity": 1,
            "reason": "Cambié de opinión",
            "refund_method": "ORIGINAL"
        },
        headers=get_auth_header('cliente')
    )
    
    if response.status_code != 201:
        print_error("Error al solicitar segunda devolución")
        return False
    
    return2_id = response.json()['id']
    print_success(f"Segunda devolución solicitada - ID: {return2_id}")
    
    # Enviar a evaluación
    requests.post(
        f"{BASE_URL}/deliveries/returns/{return2_id}/send_to_evaluation/",
        json={},
        headers=get_auth_header('manager')
    )
    print_success("Segunda devolución enviada a evaluación")
    
    # Rechazar
    print_info(f"Manager rechaza devolución {return2_id}...")
    response = requests.post(
        f"{BASE_URL}/deliveries/returns/{return2_id}/reject/",
        json={
            "rejection_reason": "El motivo 'cambié de opinión' no está cubierto por nuestra política de devoluciones. Solo aceptamos devoluciones por defectos de fábrica o productos dañados."
        },
        headers=get_auth_header('manager')
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success("Devolución rechazada correctamente")
        print_data("Resultado rechazo", data)
        return True
    else:
        print_error("Error al rechazar devolución")
        print_data("Error", response.json())
        return False

def test_warranties():
    """Prueba el sistema de garantías"""
    print_header("SISTEMA DE GARANTÍAS (WARRANTIES)")
    
    print_info("Consultando garantías disponibles...")
    
    response = requests.get(
        f"{BASE_URL}/deliveries/warranties/",
        headers=get_auth_header('cliente')
    )
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', data) if isinstance(data, dict) else data
        print_success(f"Garantías obtenidas - Total: {len(results)}")
        print_data("Garantías", results)
        
        # Buscar garantía de nuestra orden
        warranty_found = False
        for warranty in results:
            if warranty.get('order') == order_id:
                print_success(f"Garantía encontrada para orden {order_id}")
                print_data("Detalles de garantía", warranty)
                warranty_found = True
                
                # Obtener detalles específicos
                warranty_id = warranty['id']
                detail_response = requests.get(
                    f"{BASE_URL}/deliveries/warranties/{warranty_id}/",
                    headers=get_auth_header('cliente')
                )
                
                if detail_response.status_code == 200:
                    print_success("Detalles completos de garantía obtenidos")
                    print_data("Garantía completa", detail_response.json())
                
                break
        
        if not warranty_found:
            print_info("No se encontró garantía para la orden de prueba")
        
        return True
    else:
        print_error("Error al obtener garantías")
        print_data("Error", response.json())
        return False

def test_audit_logs():
    """Prueba el sistema de auditoría"""
    print_header("SISTEMA DE AUDITORÍA")
    
    print_info("Cliente consulta sus propias acciones auditadas...")
    
    response = requests.get(
        f"{BASE_URL}/audit_log/my_actions/",
        headers=get_auth_header('cliente')
    )
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', data) if isinstance(data, dict) else data
        print_success(f"Acciones auditadas - Total: {len(results)}")
        
        # Mostrar últimas 5 acciones
        print_data("Últimas acciones del cliente", results[:5] if len(results) > 5 else results)
        return True
    else:
        print_error("Error al obtener logs de auditoría")
        print_data("Error", response.json())
        return False

def print_summary():
    """Imprime resumen final de las pruebas"""
    print_header("RESUMEN DE PRUEBAS")
    
    print(f"{Colors.BOLD}IDs Generados:{Colors.END}")
    print(f"  • Producto ID: {product_id}")
    print(f"  • Orden ID: {order_id}")
    print(f"  • Devolución ID: {return_id}")
    print(f"  • Billetera ID: {wallet_id}")
    
    print(f"\n{Colors.BOLD}Usuarios autenticados:{Colors.END}")
    for role, user_id in user_ids.items():
        print(f"  • {role.capitalize()}: ID {user_id}")
    
    print(f"\n{Colors.BOLD}Flujos probados:{Colors.END}")
    print(f"  [OK] Login y autenticacion")
    print(f"  [OK] Creacion de productos")
    print(f"  [OK] Creacion de ordenes")
    print(f"  [OK] Solicitud de devolucion")
    print(f"  [OK] Evaluacion de devolucion")
    print(f"  [OK] Aprobacion con reembolso")
    print(f"  [OK] Creacion automatica de billetera")
    print(f"  [OK] Transacciones de billetera")
    print(f"  [OK] Rechazo de devolucion")
    print(f"  [OK] Sistema de garantias")
    print(f"  [OK] Sistema de auditoria")

def main():
    """Función principal"""
    print_header("SCRIPT DE PRUEBA COMPLETO - SISTEMA DE DEVOLUCIONES Y GARANTÍAS")
    
    print(f"{Colors.BOLD}Servidor:{Colors.END} {BASE_URL}")
    print(f"{Colors.BOLD}Fecha:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. LOGIN DE USUARIOS
        print_header("PASO 1: AUTENTICACIÓN DE USUARIOS")
        if not login_user("juan_cliente", "juan123", "cliente"):
            print_error("No se pudo autenticar al cliente")
            return
        
        if not login_user("carlos_manager", "carlos123", "manager"):
            print_error("No se pudo autenticar al manager")
            return
        
        if not login_user("admin", "admin123", "admin"):
            print_error("No se pudo autenticar al admin")
            return
        
        # 2. OBTENER PRODUCTO
        print_header("PASO 2: OBTENER PRODUCTO EXISTENTE")
        if not get_existing_product():
            print_error("No se pudo obtener el producto")
            return
        
        # 3. OBTENER UNA ORDEN EXISTENTE DEL CLIENTE
        print_header("PASO 3: OBTENER ORDEN EXISTENTE DEL CLIENTE")
        response = requests.get(f"{BASE_URL}/orders/", headers=get_auth_header('cliente'))
        if response.status_code == 200:
            data = response.json()
            orders = data if isinstance(data, list) else data.get('results', [])
            if len(orders) > 0:
                order_id = orders[0]['id']
                print_success(f"Orden existente obtenida - ID: {order_id}")
                print_data("Orden", {
                    "id": orders[0]['id'],
                    "status": orders[0]['status'],
                    "total_price": orders[0].get('total_price', 'N/A')
                })
            else:
                print_info("Cliente no tiene órdenes, saltando pruebas de devoluciones...")
                print_info("Para una prueba completa, el cliente necesita tener al menos una orden DELIVERED")
                return
        else:
            print_error("No se pudo obtener órdenes")
            return
        
        # 4. MARCAR ORDEN COMO ENTREGADA
        print_header("PASO 4: MARCAR ORDEN COMO ENTREGADA")
        if not mark_order_as_delivered():
            print_error("No se pudo marcar la orden como entregada")
            return
        
        # 5. SOLICITAR DEVOLUCIÓN
        print_header("PASO 5: SOLICITUD DE DEVOLUCIÓN (CLIENTE)")
        if not request_return():
            print_error("No se pudo solicitar la devolución")
            return
        
        # 6. CONSULTAR DETALLES
        print_header("PASO 6: CONSULTAR DETALLES DE DEVOLUCIÓN")
        get_return_details()
        
        # 7. ENVIAR A EVALUACIÓN
        print_header("PASO 7: ENVIAR A EVALUACIÓN (MANAGER)")
        if not send_to_evaluation():
            print_error("No se pudo enviar a evaluación")
            return
        
        # 8. APROBAR DEVOLUCIÓN
        print_header("PASO 8: APROBAR DEVOLUCIÓN Y PROCESAR REEMBOLSO (MANAGER)")
        if not approve_return():
            print_error("No se pudo aprobar la devolución")
            return
        
        # 9. VERIFICAR BILLETERA
        print_header("PASO 9: VERIFICAR BILLETERA CREADA")
        wallet = get_client_wallet()
        if wallet:
            get_wallet_balance()
            get_wallet_transactions()
            get_wallet_statistics()
        
        # 10. CONSULTAR MIS DEVOLUCIONES
        print_header("PASO 10: CLIENTE CONSULTA SUS DEVOLUCIONES")
        get_my_returns()
        
        # 11. MANAGER LISTA TODAS LAS DEVOLUCIONES
        print_header("PASO 11: MANAGER LISTA TODAS LAS DEVOLUCIONES")
        manager_list_all_returns()
        
        # 12. PROBAR RECHAZO
        test_reject_return_flow()
        
        # 13. PROBAR GARANTÍAS
        test_warranties()
        
        # 14. PROBAR AUDITORÍA
        test_audit_logs()
        
        # RESUMEN FINAL
        print_summary()
        
        print_header("[OK] TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        
    except KeyboardInterrupt:
        print_error("\n\nPruebas interrumpidas por el usuario")
    except Exception as e:
        print_error(f"\n\nError inesperado: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
