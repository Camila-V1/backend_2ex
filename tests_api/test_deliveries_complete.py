#!/usr/bin/env python3
"""
Tests completos para el módulo de Deliveries
Cubre: Entregas, garantías, devoluciones, reparaciones
"""
import requests
import time
from config import API_BASE_URL, TEST_CREDENTIALS, Colors

class TestDeliveriesComplete:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.admin_token = None
        self.delivery_token = None
        self.test_delivery_id = None
        self.test_warranty_id = None
        self.test_return_id = None
        
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

    def test_list_delivery_zones(self):
        """TEST: Listar zonas de entrega"""
        print("\n🗺️ TEST: Listar zonas de entrega...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/deliveries/zones/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get('count', 0)
            return self.print_test(
                "List delivery zones",
                True,
                f"Total zonas: {count}"
            )
        else:
            return self.print_test(
                "List delivery zones",
                False,
                f"Status: {response.status_code}"
            )

    def test_list_delivery_profiles(self):
        """TEST: Listar perfiles de delivery"""
        print("\n👥 TEST: Listar perfiles delivery...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/deliveries/profiles/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get('count', 0)
            return self.print_test(
                "List delivery profiles",
                True,
                f"Total perfiles: {count}"
            )
        else:
            return self.print_test(
                "List delivery profiles",
                False,
                f"Status: {response.status_code}"
            )

    def test_list_deliveries(self):
        """TEST: Listar entregas"""
        print("\n📦 TEST: Listar entregas...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/deliveries/deliveries/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get('count', 0)
            if count > 0 and isinstance(data, list):
                self.test_delivery_id = data[0].get('id')
            return self.print_test(
                "List deliveries",
                True,
                f"Total entregas: {count}"
            )
        else:
            return self.print_test(
                "List deliveries",
                False,
                f"Status: {response.status_code}"
            )

    def test_get_delivery_detail(self):
        """TEST: Obtener detalle de entrega"""
        print("\n🔍 TEST: Detalle de entrega...")
        
        if not self.test_delivery_id:
            print(f"{Colors.WARNING}⚠ Saltando test (no hay entrega){Colors.ENDC}")
            return True
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/deliveries/deliveries/{self.test_delivery_id}/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            status = data.get('status', 'N/A')
            return self.print_test(
                "Get delivery detail",
                True,
                f"Estado: {status}"
            )
        else:
            return self.print_test(
                "Get delivery detail",
                False,
                f"Status: {response.status_code}"
            )

    def test_delivery_user_can_view_assigned(self):
        """TEST: Usuario delivery puede ver sus entregas asignadas"""
        print("\n🚚 TEST: Delivery ver entregas asignadas...")
        
        headers = {"Authorization": f"Bearer {self.delivery_token}"}
        response = requests.get(
            f"{self.base_url}/deliveries/deliveries/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get('count', 0)
            return self.print_test(
                "Delivery view assigned deliveries",
                True,
                f"Entregas asignadas: {count}"
            )
        else:
            return self.print_test(
                "Delivery view assigned deliveries",
                False,
                f"Status: {response.status_code}"
            )

    def test_list_warranties(self):
        """TEST: Listar garantías"""
        print("\n🛡️ TEST: Listar garantías...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/deliveries/warranties/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get('count', 0)
            if count > 0 and isinstance(data, list):
                self.test_warranty_id = data[0].get('id')
            return self.print_test(
                "List warranties",
                True,
                f"Total garantías: {count}"
            )
        else:
            return self.print_test(
                "List warranties",
                False,
                f"Status: {response.status_code}"
            )

    def test_get_warranty_detail(self):
        """TEST: Obtener detalle de garantía"""
        print("\n🔍 TEST: Detalle de garantía...")
        
        if not self.test_warranty_id:
            print(f"{Colors.WARNING}⚠ Saltando test (no hay garantía){Colors.ENDC}")
            return True
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/deliveries/warranties/{self.test_warranty_id}/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            status = data.get('status', 'N/A')
            return self.print_test(
                "Get warranty detail",
                True,
                f"Estado: {status}"
            )
        else:
            return self.print_test(
                "Get warranty detail",
                False,
                f"Status: {response.status_code}"
            )

    def test_list_returns(self):
        """TEST: Listar devoluciones"""
        print("\n↩️ TEST: Listar devoluciones...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/deliveries/returns/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get('count', 0)
            if count > 0 and isinstance(data, list):
                self.test_return_id = data[0].get('id')
            return self.print_test(
                "List returns",
                True,
                f"Total devoluciones: {count}"
            )
        else:
            return self.print_test(
                "List returns",
                False,
                f"Status: {response.status_code}"
            )

    def test_get_return_detail(self):
        """TEST: Obtener detalle de devolución"""
        print("\n🔍 TEST: Detalle de devolución...")
        
        if not self.test_return_id:
            print(f"{Colors.WARNING}⚠ Saltando test (no hay devolución){Colors.ENDC}")
            return True
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/deliveries/returns/{self.test_return_id}/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            status = data.get('status', 'N/A')
            return self.print_test(
                "Get return detail",
                True,
                f"Estado: {status}"
            )
        else:
            return self.print_test(
                "Get return detail",
                False,
                f"Status: {response.status_code}"
            )

    def test_list_repairs(self):
        """TEST: Listar reparaciones"""
        print("\n🔧 TEST: Listar reparaciones...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/deliveries/repairs/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get('count', 0)
            return self.print_test(
                "List repairs",
                True,
                f"Total reparaciones: {count}"
            )
        else:
            return self.print_test(
                "List repairs",
                False,
                f"Status: {response.status_code}"
            )

    def test_filter_deliveries_by_status(self):
        """TEST: Filtrar entregas por estado"""
        print("\n🔎 TEST: Filtrar entregas por estado...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/deliveries/deliveries/?status=PENDING",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get('count', 0)
            return self.print_test(
                "Filter deliveries by status",
                True,
                f"Entregas PENDING: {count}"
            )
        else:
            return self.print_test(
                "Filter deliveries by status",
                False,
                f"Status: {response.status_code}"
            )

    def run_all_tests(self):
        """Ejecuta todos los tests de deliveries"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}🚚 TESTS COMPLETOS DE DELIVERIES{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        results = []
        
        # Setup: Login
        self.admin_token = self.login('admin')
        self.delivery_token = self.login('delivery')
        
        if not self.admin_token:
            print(f"{Colors.FAIL}❌ No se pudo obtener token. Abortando tests.{Colors.ENDC}")
            return []
        
        # Tests de zonas y perfiles
        print(f"\n{Colors.OKCYAN}🗺️ PARTE 1: Zonas y Perfiles{Colors.ENDC}")
        results.append(self.test_list_delivery_zones())
        results.append(self.test_list_delivery_profiles())
        
        # Tests de entregas
        print(f"\n{Colors.OKCYAN}📦 PARTE 2: Entregas{Colors.ENDC}")
        results.append(self.test_list_deliveries())
        results.append(self.test_get_delivery_detail())
        results.append(self.test_delivery_user_can_view_assigned())
        results.append(self.test_filter_deliveries_by_status())
        
        # Tests de garantías
        print(f"\n{Colors.OKCYAN}🛡️ PARTE 3: Garantías{Colors.ENDC}")
        results.append(self.test_list_warranties())
        results.append(self.test_get_warranty_detail())
        
        # Tests de devoluciones
        print(f"\n{Colors.OKCYAN}↩️ PARTE 4: Devoluciones{Colors.ENDC}")
        results.append(self.test_list_returns())
        results.append(self.test_get_return_detail())
        
        # Tests de reparaciones
        print(f"\n{Colors.OKCYAN}🔧 PARTE 5: Reparaciones{Colors.ENDC}")
        results.append(self.test_list_repairs())
        
        return results


def main():
    tester = TestDeliveriesComplete()
    results = tester.run_all_tests()
    
    # Resumen
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}📊 RESUMEN - DELIVERIES COMPLETE{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"Total tests: {total}")
    print(f"{Colors.OKGREEN}✅ Exitosos: {passed}{Colors.ENDC}")
    if failed > 0:
        print(f"{Colors.FAIL}❌ Fallidos: {failed}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    exit(main())
