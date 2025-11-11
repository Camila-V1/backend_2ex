# tests_api/test_products.py
"""
Pruebas de endpoints de productos
"""
import requests
from config import API_BASE_URL, DEFAULT_HEADERS, Colors
from test_auth import test_login, print_result

def test_list_products():
    """Prueba listar todos los productos (endpoint público)"""
    print(f"\n{Colors.BOLD}📦 Probando listar productos...{Colors.ENDC}")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/products/",
            headers=DEFAULT_HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get('count', 0)
            print_result("List products", True, f"Total productos: {count}")
            return data
        else:
            print_result("List products", False, f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_result("List products", False, f"Error: {str(e)}")
        return None

def test_get_product_detail(product_id=1):
    """Prueba obtener detalle de un producto"""
    print(f"\n{Colors.BOLD}🔍 Probando detalle de producto {product_id}...{Colors.ENDC}")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/products/{product_id}/",
            headers=DEFAULT_HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result("Get product detail", True, 
                        f"Producto: {data.get('name')} - Precio: ${data.get('price')}")
            return data
        else:
            print_result("Get product detail", False, f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_result("Get product detail", False, f"Error: {str(e)}")
        return None

def test_list_categories():
    """Prueba listar categorías"""
    print(f"\n{Colors.BOLD}🏷️ Probando listar categorías...{Colors.ENDC}")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/products/categories/",
            headers=DEFAULT_HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get('count', 0)
            print_result("List categories", True, f"Total categorías: {count}")
            return data
        else:
            print_result("List categories", False, f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_result("List categories", False, f"Error: {str(e)}")
        return None

def test_search_products(query="laptop"):
    """Prueba búsqueda de productos"""
    print(f"\n{Colors.BOLD}🔎 Probando búsqueda: '{query}'...{Colors.ENDC}")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/products/?search={query}",
            headers=DEFAULT_HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get('count', 0)
            print_result("Search products", True, f"Resultados encontrados: {count}")
            return data
        else:
            print_result("Search products", False, f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_result("Search products", False, f"Error: {str(e)}")
        return None

def test_filter_products_by_category(category_id=1):
    """Prueba filtrar productos por categoría"""
    print(f"\n{Colors.BOLD}🎯 Probando filtro por categoría {category_id}...{Colors.ENDC}")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/products/?category={category_id}",
            headers=DEFAULT_HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get('count', 0)
            print_result("Filter by category", True, f"Productos en categoría: {count}")
            return data
        else:
            print_result("Filter by category", False, f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_result("Filter by category", False, f"Error: {str(e)}")
        return None

def run_tests():
    """Ejecuta todas las pruebas de productos"""
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}📦 PRUEBAS DE PRODUCTOS{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0
    }
    
    # Test 1: Listar productos
    results['total'] += 1
    if test_list_products():
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 2: Detalle de producto
    results['total'] += 1
    if test_get_product_detail(1):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 3: Listar categorías
    results['total'] += 1
    if test_list_categories():
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 4: Búsqueda de productos
    results['total'] += 1
    if test_search_products("laptop"):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 5: Filtrar por categoría
    results['total'] += 1
    if test_filter_products_by_category(1):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    return results

if __name__ == '__main__':
    results = run_tests()
    print(f"\n{Colors.BOLD}Resultados: {results['passed']}/{results['total']} pruebas exitosas{Colors.ENDC}")
