# tests_api/test_predictions.py
"""
Pruebas de endpoints de predicciones ML
"""
import requests
from config import API_BASE_URL, DEFAULT_HEADERS, Colors
from test_auth import test_login, print_result

def test_sales_predictions(access_token):
    """Prueba predicciones de ventas"""
    print(f"\n{Colors.BOLD}📈 Probando predicciones de ventas...{Colors.ENDC}")
    
    try:
        headers = DEFAULT_HEADERS.copy()
        headers['Authorization'] = f'Bearer {access_token}'
        
        response = requests.get(
            f"{API_BASE_URL}/predictions/sales/",
            headers=headers,
            timeout=30  # Aumentar timeout a 30s para ML
        )
        
        if response.status_code == 200:
            data = response.json()
            predictions = data.get('predictions', [])
            print_result("Sales predictions", True, 
                        f"Predicciones generadas: {len(predictions)}")
            return data
        else:
            print_result("Sales predictions", False, f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_result("Sales predictions", False, f"Error: {str(e)}")
        return None

def run_tests():
    """Ejecuta todas las pruebas de predicciones"""
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}📈 PRUEBAS DE PREDICCIONES ML{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0
    }
    
    # Primero obtener token de admin
    auth_data = test_login('admin')
    if not auth_data:
        print(f"{Colors.FAIL}No se pudo autenticar, abortando pruebas de predicciones{Colors.ENDC}")
        return results
    
    access_token = auth_data.get('access')
    
    # Test 1: Predicciones de ventas
    results['total'] += 1
    if test_sales_predictions(access_token):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    return results

if __name__ == '__main__':
    results = run_tests()
    print(f"\n{Colors.BOLD}Resultados: {results['passed']}/{results['total']} pruebas exitosas{Colors.ENDC}")
