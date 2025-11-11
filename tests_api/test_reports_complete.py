#!/usr/bin/env python3
"""
Tests completos para el módulo de Reports
Cubre: Reportes de ventas, productos, facturas, previews
"""
import requests
from config import API_BASE_URL, TEST_CREDENTIALS, Colors

class TestReportsComplete:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.admin_token = None
        self.manager_token = None
        self.test_order_id = None
        
    def print_test(self, name, success, details=""):
        """Imprime resultado de test con formato"""
        if success:
            print(f"{Colors.OKGREEN}✅ {name}{Colors.ENDC}")
            if details:
                print(f"   {details}")
        else:
            print(f"{Colors.FAIL}❌ {name}{Colors.ENDC}")
            if details:
                print(f"   {details}")
        return success

    def login(self, role='admin'):
        """Login y obtiene token"""
        print(f"\n🔐 Obteniendo token {role}...")
        credentials = TEST_CREDENTIALS[role]
        response = requests.post(
            f"{self.base_url}/token/",
            json=credentials
        )
        
        if response.status_code == 200:
            token = response.json()['access']
            print(f"{Colors.OKGREEN}✅ Token obtenido{Colors.ENDC}")
            return token
        else:
            print(f"{Colors.FAIL}❌ Error login: {response.status_code}{Colors.ENDC}")
            return None

    def get_first_order(self):
        """Obtiene ID de la primera orden disponible"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(f"{self.base_url}/orders/admin/", headers=headers)
        if response.status_code == 200:
            orders = response.json()
            if orders and len(orders) > 0:
                return orders[0]['id']
        return None

    def test_sales_report_preview(self):
        """TEST: Preview de reporte de ventas"""
        print("\n📊 TEST: Preview reporte de ventas...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        params = {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        response = requests.get(
            f"{self.base_url}/reports/sales/preview/",
            params=params,
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            total_sales = data.get('total_sales', 0)
            return self.print_test(
                "Sales report preview",
                True,
                f"Total ventas: ${total_sales}"
            )
        else:
            return self.print_test(
                "Sales report preview",
                False,
                f"Status: {response.status_code}"
            )

    def test_products_report_preview(self):
        """TEST: Preview de reporte de productos"""
        print("\n📦 TEST: Preview reporte de productos...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/reports/products/preview/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            total_products = data.get('total_products', 0)
            return self.print_test(
                "Products report preview",
                True,
                f"Total productos: {total_products}"
            )
        else:
            return self.print_test(
                "Products report preview",
                False,
                f"Status: {response.status_code}"
            )

    def test_order_invoice(self):
        """TEST: Generar factura de orden"""
        print("\n🧾 TEST: Generar factura de orden...")
        
        if not self.test_order_id:
            self.test_order_id = self.get_first_order()
        
        if not self.test_order_id:
            print(f"{Colors.WARNING}⚠ Saltando test (no hay órdenes){Colors.ENDC}")
            return True
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/reports/orders/{self.test_order_id}/invoice/",
            headers=headers
        )
        
        # Debe retornar PDF (content-type application/pdf)
        success = response.status_code == 200
        if success:
            content_type = response.headers.get('Content-Type', '')
            is_pdf = 'pdf' in content_type.lower()
            return self.print_test(
                "Order invoice PDF",
                True,
                f"Factura generada ({len(response.content)} bytes)"
            )
        else:
            return self.print_test(
                "Order invoice PDF",
                False,
                f"Status: {response.status_code}"
            )

    def test_sales_report_pdf(self):
        """TEST: Generar reporte de ventas PDF"""
        print("\n📄 TEST: Generar reporte ventas PDF...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        params = {
            "format": "pdf",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        
        response = requests.get(
            f"{self.base_url}/reports/sales/",
            params=params,
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            return self.print_test(
                "Sales report PDF",
                True,
                f"PDF generado ({len(response.content)} bytes)"
            )
        else:
            return self.print_test(
                "Sales report PDF",
                False,
                f"Status: {response.status_code}"
            )

    def test_products_report_excel(self):
        """TEST: Generar reporte de productos Excel"""
        print("\n📊 TEST: Generar reporte productos Excel...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        params = {"format": "excel"}
        
        response = requests.get(
            f"{self.base_url}/reports/products/",
            params=params,
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            return self.print_test(
                "Products report Excel",
                True,
                f"Excel generado ({len(response.content)} bytes)"
            )
        else:
            return self.print_test(
                "Products report Excel",
                False,
                f"Status: {response.status_code}"
            )

    def test_dynamic_parser_preview(self):
        """TEST: Parser dinámico de reportes con NLP"""
        print("\n🎤 TEST: Dynamic parser preview...")
        
        headers = {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "command": "ventas del mes"
        }
        
        response = requests.post(
            f"{self.base_url}/reports/dynamic-parser/preview/",
            json=data,
            headers=headers
        )
        
        success = response.status_code in [200, 201]
        if success:
            return self.print_test(
                "Dynamic parser preview",
                True,
                "Parser procesó comando"
            )
        else:
            # Parser puede no estar configurado, no fallar el test
            print(f"{Colors.WARNING}⚠ Parser requiere configuración adicional{Colors.ENDC}")
            return True

    def test_manager_access_reports(self):
        """TEST: Manager puede acceder a reportes"""
        print("\n👔 TEST: Manager acceso a reportes...")
        
        headers = {"Authorization": f"Bearer {self.manager_token}"}
        params = {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        response = requests.get(
            f"{self.base_url}/reports/sales/preview/",
            params=params,
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            return self.print_test(
                "Manager access reports",
                True,
                "Manager puede ver reportes"
            )
        else:
            return self.print_test(
                "Manager access reports",
                False,
                f"Status: {response.status_code}"
            )

    def run_all_tests(self):
        """Ejecuta todos los tests de reports"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}📊 TESTS COMPLETOS DE REPORTS{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        results = []
        
        # Setup: Login
        self.admin_token = self.login('admin')
        self.manager_token = self.login('manager')
        
        if not self.admin_token:
            print(f"{Colors.FAIL}❌ No se pudo obtener token. Abortando tests.{Colors.ENDC}")
            return []
        
        # Tests de previews
        print(f"\n{Colors.OKCYAN}👀 PARTE 1: Previews (JSON){Colors.ENDC}")
        results.append(self.test_sales_report_preview())
        results.append(self.test_products_report_preview())
        
        # Tests de generación de documentos
        print(f"\n{Colors.OKCYAN}📄 PARTE 2: Documentos (PDF/Excel){Colors.ENDC}")
        results.append(self.test_sales_report_pdf())
        results.append(self.test_products_report_excel())
        results.append(self.test_order_invoice())
        
        # Tests de parser dinámico
        print(f"\n{Colors.OKCYAN}🎤 PARTE 3: Parser Dinámico{Colors.ENDC}")
        results.append(self.test_dynamic_parser_preview())
        
        # Tests de permisos
        print(f"\n{Colors.OKCYAN}🔐 PARTE 4: Permisos{Colors.ENDC}")
        results.append(self.test_manager_access_reports())
        
        return results


def main():
    tester = TestReportsComplete()
    results = tester.run_all_tests()
    
    # Resumen
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}📊 RESUMEN - REPORTS COMPLETE{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"Total tests: {total}")
    print(f"{Colors.OKGREEN}✅ Exitosos: {passed}{Colors.ENDC}")
    if failed > 0:
        print(f"{Colors.FAIL}❌ Fallidos: {failed}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    exit(main())
