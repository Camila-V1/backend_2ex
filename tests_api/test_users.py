# tests_api/test_users.py
"""
Pruebas de endpoints de usuarios
"""
import requests
from config import API_BASE_URL, TEST_CREDENTIALS, DEFAULT_HEADERS, Colors
from test_auth import test_login, print_result

def test_list_users(access_token):
    """Prueba listar todos los usuarios"""
    print(f"\n{Colors.BOLD}📋 Probando listar usuarios...{Colors.ENDC}")
    
    try:
        headers = DEFAULT_HEADERS.copy()
        headers['Authorization'] = f'Bearer {access_token}'
        
        response = requests.get(
            f"{API_BASE_URL}/users/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get('count', 0)
            print_result("List users", True, f"Total usuarios: {count}")
            return data
        else:
            print_result("List users", False, f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_result("List users", False, f"Error: {str(e)}")
        return None

def test_get_user_detail(access_token, user_id=1):
    """Prueba obtener detalle de un usuario"""
    print(f"\n{Colors.BOLD}🔍 Probando detalle de usuario {user_id}...{Colors.ENDC}")
    
    try:
        headers = DEFAULT_HEADERS.copy()
        headers['Authorization'] = f'Bearer {access_token}'
        
        response = requests.get(
            f"{API_BASE_URL}/users/{user_id}/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result("Get user detail", True, 
                        f"Usuario: {data.get('username')} - Email: {data.get('email')}")
            return data
        else:
            print_result("Get user detail", False, f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_result("Get user detail", False, f"Error: {str(e)}")
        return None

def test_create_user(access_token):
    """Prueba crear un nuevo usuario"""
    print(f"\n{Colors.BOLD}➕ Probando crear usuario...{Colors.ENDC}")
    
    new_user = {
        'username': 'test_user_api',
        'email': 'testapi@example.com',
        'password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'API',
        'role': 'CLIENTE'
    }
    
    try:
        headers = DEFAULT_HEADERS.copy()
        headers['Authorization'] = f'Bearer {access_token}'
        
        response = requests.post(
            f"{API_BASE_URL}/users/",
            json=new_user,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_result("Create user", True, f"Usuario creado: {data.get('username')}")
            return data
        else:
            print_result("Create user", False, f"Status: {response.status_code} - {response.text[:100]}")
            return None
            
    except Exception as e:
        print_result("Create user", False, f"Error: {str(e)}")
        return None

def run_tests():
    """Ejecuta todas las pruebas de usuarios"""
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}👥 PRUEBAS DE USUARIOS{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0
    }
    
    # Primero obtener token de admin
    auth_data = test_login('admin')
    if not auth_data:
        print(f"{Colors.FAIL}No se pudo autenticar, abortando pruebas de usuarios{Colors.ENDC}")
        return results
    
    access_token = auth_data.get('access')
    
    # Test 1: Listar usuarios
    results['total'] += 1
    if test_list_users(access_token):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 2: Obtener detalle de usuario
    results['total'] += 1
    if test_get_user_detail(access_token, user_id=1):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 3: Crear usuario
    results['total'] += 1
    new_user = test_create_user(access_token)
    if new_user:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    return results

if __name__ == '__main__':
    results = run_tests()
    print(f"\n{Colors.BOLD}Resultados: {results['passed']}/{results['total']} pruebas exitosas{Colors.ENDC}")
