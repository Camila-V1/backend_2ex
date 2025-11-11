# tests_api/test_auth.py
"""
Pruebas de autenticación y autorización
"""
import requests
from config import API_BASE_URL, TEST_CREDENTIALS, DEFAULT_HEADERS, Colors

def print_result(test_name, success, message=""):
    """Imprime el resultado de una prueba"""
    if success:
        print(f"{Colors.OKGREEN}✅ {test_name}{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ {test_name}{Colors.ENDC}")
    if message:
        print(f"   {message}")

def test_login(role='admin'):
    """Prueba el login con diferentes roles"""
    print(f"\n{Colors.BOLD}🔐 Probando login como {role}...{Colors.ENDC}")
    
    credentials = TEST_CREDENTIALS.get(role)
    if not credentials:
        print_result(f"Login {role}", False, "Credenciales no encontradas")
        return None
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/token/",
            json=credentials,
            headers=DEFAULT_HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(f"Login {role}", True, f"Token obtenido (longitud: {len(data.get('access', ''))})")
            return data
        else:
            print_result(f"Login {role}", False, f"Status: {response.status_code} - {response.text[:100]}")
            return None
            
    except Exception as e:
        print_result(f"Login {role}", False, f"Error: {str(e)}")
        return None

def test_token_refresh(refresh_token):
    """Prueba el refresh de token"""
    print(f"\n{Colors.BOLD}🔄 Probando refresh token...{Colors.ENDC}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/token/refresh/",
            json={'refresh': refresh_token},
            headers=DEFAULT_HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result("Token refresh", True, f"Nuevo token obtenido")
            return data.get('access')
        else:
            print_result("Token refresh", False, f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_result("Token refresh", False, f"Error: {str(e)}")
        return None

def test_profile(access_token):
    """Prueba obtener el perfil del usuario"""
    print(f"\n{Colors.BOLD}👤 Probando obtener perfil...{Colors.ENDC}")
    
    try:
        headers = DEFAULT_HEADERS.copy()
        headers['Authorization'] = f'Bearer {access_token}'
        
        response = requests.get(
            f"{API_BASE_URL}/users/profile/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result("Get profile", True, 
                        f"Usuario: {data.get('username')} - Role: {data.get('role')}")
            return data
        else:
            print_result("Get profile", False, f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_result("Get profile", False, f"Error: {str(e)}")
        return None

def run_tests():
    """Ejecuta todas las pruebas de autenticación"""
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}🔐 PRUEBAS DE AUTENTICACIÓN{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0
    }
    
    # Test 1: Login como admin
    results['total'] += 1
    auth_data = test_login('admin')
    if auth_data:
        results['passed'] += 1
        access_token = auth_data.get('access')
        refresh_token = auth_data.get('refresh')
        
        # Test 2: Obtener perfil
        results['total'] += 1
        if test_profile(access_token):
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # Test 3: Refresh token
        results['total'] += 1
        if test_token_refresh(refresh_token):
            results['passed'] += 1
        else:
            results['failed'] += 1
    else:
        results['failed'] += 1
    
    # Test 4: Login como manager
    results['total'] += 1
    if test_login('manager'):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 5: Login como cajero
    results['total'] += 1
    if test_login('cajero'):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    return results

if __name__ == '__main__':
    results = run_tests()
    print(f"\n{Colors.BOLD}Resultados: {results['passed']}/{results['total']} pruebas exitosas{Colors.ENDC}")
