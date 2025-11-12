#!/usr/bin/env python3
"""
Script de diagnóstico para identificar endpoints fallando en dashboard admin
Simula las llamadas que hace el frontend al cargar el dashboard
"""
import requests
from tests_api.config import API_BASE_URL, TEST_CREDENTIALS, Colors

class DashboardDiagnostic:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token = None
        self.errors = []
        self.warnings = []
        
    def login_admin(self):
        """Login como admin"""
        print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}🔍 DIAGNÓSTICO DE DASHBOARD ADMIN{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}\n")
        
        print("🔐 Login como admin...")
        response = requests.post(
            f"{self.base_url}/token/",
            json=TEST_CREDENTIALS['admin']
        )
        
        if response.status_code == 200:
            self.token = response.json()['access']
            print(f"{Colors.OKGREEN}✅ Token obtenido{Colors.ENDC}\n")
            return True
        else:
            print(f"{Colors.FAIL}❌ Error login: {response.status_code}{Colors.ENDC}")
            return False
    
    def test_endpoint(self, method, endpoint, description, data=None):
        """Testa un endpoint y registra errores"""
        print(f"🔍 Testeando: {description}")
        print(f"   {method} {endpoint}")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            if method == 'GET':
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
            elif method == 'POST':
                response = requests.post(
                    f"{self.base_url}{endpoint}", 
                    json=data, 
                    headers=headers
                )
            
            if response.status_code in [200, 201]:
                print(f"{Colors.OKGREEN}   ✅ OK - Status {response.status_code}{Colors.ENDC}")
                try:
                    json_data = response.json()
                    # Verificar estructura de respuesta
                    if isinstance(json_data, dict):
                        keys = list(json_data.keys())[:5]
                        print(f"   📦 Keys: {keys}")
                    elif isinstance(json_data, list):
                        print(f"   📦 Array con {len(json_data)} elementos")
                except:
                    print(f"{Colors.WARNING}   ⚠️ Respuesta no es JSON{Colors.ENDC}")
            else:
                error_msg = f"{description}: {response.status_code}"
                self.errors.append(error_msg)
                print(f"{Colors.FAIL}   ❌ ERROR - Status {response.status_code}{Colors.ENDC}")
                try:
                    print(f"   📄 Response: {response.text[:200]}")
                except:
                    pass
        
        except Exception as e:
            error_msg = f"{description}: {str(e)}"
            self.errors.append(error_msg)
            print(f"{Colors.FAIL}   ❌ EXCEPTION: {str(e)}{Colors.ENDC}")
        
        print()
    
    def run_dashboard_tests(self):
        """Simula todas las llamadas del dashboard admin"""
        
        if not self.login_admin():
            return
        
        print(f"{Colors.OKCYAN}📊 PARTE 1: Endpoints del Dashboard Admin{Colors.ENDC}\n")
        
        # Dashboard principal
        self.test_endpoint('GET', '/orders/admin/dashboard/', 'Dashboard de órdenes')
        
        # Órdenes
        self.test_endpoint('GET', '/orders/admin/', 'Lista de órdenes admin')
        self.test_endpoint('GET', '/orders/', 'Mis órdenes')
        
        # Usuarios
        self.test_endpoint('GET', '/users/', 'Lista de usuarios')
        self.test_endpoint('GET', '/users/profile/', 'Mi perfil')
        
        # Productos
        self.test_endpoint('GET', '/products/', 'Lista de productos')
        self.test_endpoint('GET', '/products/categories/', 'Categorías')
        
        # Estadísticas y reportes
        print(f"{Colors.OKCYAN}📈 PARTE 2: Estadísticas y Reportes{Colors.ENDC}\n")
        
        self.test_endpoint('GET', '/predictions/sales/', 'Predicciones de ventas')
        
        # Reports con fechas
        self.test_endpoint(
            'GET', 
            '/reports/sales/preview/?start_date=2024-01-01&end_date=2024-12-31',
            'Preview reporte de ventas'
        )
        
        self.test_endpoint(
            'GET',
            '/reports/products/preview/',
            'Preview reporte de productos'
        )
        
        # Wallet
        print(f"{Colors.OKCYAN}💰 PARTE 3: Wallet y Transacciones{Colors.ENDC}\n")
        
        self.test_endpoint('GET', '/users/wallets/my_wallet/', 'Mi billetera')
        
        # Deliveries
        print(f"{Colors.OKCYAN}🚚 PARTE 4: Deliveries{Colors.ENDC}\n")
        
        self.test_endpoint('GET', '/deliveries/', 'Lista de entregas')
        self.test_endpoint('GET', '/deliveries/zones/', 'Zonas de entrega')
        
        # Auditoría
        print(f"{Colors.OKCYAN}🔍 PARTE 5: Auditoría{Colors.ENDC}\n")
        
        self.test_endpoint('GET', '/audit/', 'Logs de auditoría')
        
        # Endpoints que NO EXISTEN pero el frontend podría estar llamando
        print(f"{Colors.WARNING}⚠️ PARTE 6: Endpoints que NO EXISTEN (posibles errores){Colors.ENDC}\n")
        
        self.test_endpoint('GET', '/orders/', 'Lista órdenes (debería ser /orders/admin/)')
        self.test_endpoint('GET', '/wallet/', 'Wallet sin my_wallet/')
        self.test_endpoint('GET', '/reports/sales/', 'Sales sin fechas (falta ?start_date=)')
        self.test_endpoint('GET', '/dashboard/', 'Dashboard genérico')
        self.test_endpoint('GET', '/stats/', 'Stats genérico')
    
    def print_summary(self):
        """Imprime resumen de errores"""
        print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}📊 RESUMEN DEL DIAGNÓSTICO{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}\n")
        
        if len(self.errors) == 0:
            print(f"{Colors.OKGREEN}✅ No se detectaron errores{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}❌ ERRORES DETECTADOS ({len(self.errors)}):{Colors.ENDC}\n")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        
        if len(self.warnings) > 0:
            print(f"\n{Colors.WARNING}⚠️ ADVERTENCIAS ({len(self.warnings)}):{Colors.ENDC}\n")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
        
        # Recomendaciones
        if len(self.errors) > 0:
            print(f"\n{Colors.OKCYAN}💡 RECOMENDACIONES:{Colors.ENDC}\n")
            print("1. Revisar console.log del frontend para ver qué endpoint falla")
            print("2. Abrir DevTools > Network para ver requests fallidos")
            print("3. Comparar URLs llamadas con endpoints correctos validados")
            print("4. Verificar que frontend maneje errores con try/catch")
            print("\n📝 Ver ANALISIS_ERRORES_FRONTEND.md para soluciones")


def main():
    diagnostic = DashboardDiagnostic()
    diagnostic.run_dashboard_tests()
    diagnostic.print_summary()


if __name__ == '__main__':
    main()
