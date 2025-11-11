# tests_api/test_orders.py
"""
Pruebas de endpoints de órdenes
"""
import requests
from config import API_BASE_URL, DEFAULT_HEADERS, Colors
from test_auth import test_login, print_result

def test_create_order(access_token):
    """Prueba crear una orden"""
    print(f"\n{Colors.BOLD}🛒 Probando crear orden...{Colors.ENDC}")
    
    order_data = {
        'items': [
            {
                'product_id': 1,
                'quantity': 2
            },
            {
                'product_id': 2,
                'quantity': 1
            }
        ],
        'shipping_address': '123 Test Street',
        'payment_method': 'STRIPE'
    }
    
    try:
        headers = DEFAULT_HEADERS.copy()
        headers['Authorization'] = f'Bearer {access_token}'
        
        response = requests.post(
            f"{API_BASE_URL}/orders/",
            json=order_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_result("Create order", True, 
                        f"Orden creada: #{data.get('id')} - Total: ${data.get('total_amount')}")
            return data
        else:
            print_result("Create order", False, f"Status: {response.status_code} - {response.text[:200]}")
            return None
            
    except Exception as e:
        print_result("Create order", False, f"Error: {str(e)}")
        return None

def test_list_orders(access_token):
    """Prueba listar órdenes del usuario"""
    print(f"\n{Colors.BOLD}📋 Probando listar órdenes...{Colors.ENDC}")
    
    try:
        headers = DEFAULT_HEADERS.copy()
        headers['Authorization'] = f'Bearer {access_token}'
        
        response = requests.get(
            f"{API_BASE_URL}/orders/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get('count', 0)
            print_result("List orders", True, f"Total órdenes: {count}")
            return data
        else:
            print_result("List orders", False, f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_result("List orders", False, f"Error: {str(e)}")
        return None

def test_get_order_detail(access_token, order_id=1):
    """Prueba obtener detalle de una orden"""
    print(f"\n{Colors.BOLD}🔍 Probando detalle de orden {order_id}...{Colors.ENDC}")
    
    try:
        headers = DEFAULT_HEADERS.copy()
        headers['Authorization'] = f'Bearer {access_token}'
        
        response = requests.get(
            f"{API_BASE_URL}/orders/{order_id}/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result("Get order detail", True, 
                        f"Orden #{data.get('id')} - Estado: {data.get('status')}")
            return data
        else:
            print_result("Get order detail", False, f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_result("Get order detail", False, f"Error: {str(e)}")
        return None

def test_admin_dashboard(access_token):
    """Prueba el dashboard de administrador"""
    print(f"\n{Colors.BOLD}📊 Probando dashboard admin...{Colors.ENDC}")
    
    try:
        headers = DEFAULT_HEADERS.copy()
        headers['Authorization'] = f'Bearer {access_token}'
        
        response = requests.get(
            f"{API_BASE_URL}/orders/admin/dashboard/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result("Admin dashboard", True, 
                        f"Total ventas: ${data.get('total_sales', 0)}")
            return data
        else:
            print_result("Admin dashboard", False, f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_result("Admin dashboard", False, f"Error: {str(e)}")
        return None

def run_tests():
    """Ejecuta todas las pruebas de órdenes"""
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}🛒 PRUEBAS DE ÓRDENES{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0
    }
    
    # Primero obtener token de admin
    auth_data = test_login('admin')
    if not auth_data:
        print(f"{Colors.FAIL}No se pudo autenticar, abortando pruebas de órdenes{Colors.ENDC}")
        return results
    
    access_token = auth_data.get('access')
    
    # Test 1: Listar órdenes
    results['total'] += 1
    if test_list_orders(access_token):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 2: Detalle de orden
    results['total'] += 1
    if test_get_order_detail(access_token, 1):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 3: Dashboard admin
    results['total'] += 1
    if test_admin_dashboard(access_token):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 4: Crear orden (comentado porque modifica la BD)
    # results['total'] += 1
    # if test_create_order(access_token):
    #     results['passed'] += 1
    # else:
    #     results['failed'] += 1
    
    return results

if __name__ == '__main__':
    results = run_tests()
    print(f"\n{Colors.BOLD}Resultados: {results['passed']}/{results['total']} pruebas exitosas{Colors.ENDC}")
