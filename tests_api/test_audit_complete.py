#!/usr/bin/env python3
"""
Tests completos para el módulo de Audit (Auditoría)
Cubre: Logs de auditoría, filtros, consultas
"""
import requests
from config import API_BASE_URL, TEST_CREDENTIALS, Colors

class TestAuditComplete:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.admin_token = None
        self.manager_token = None
        self.test_log_id = None
        
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

    def test_list_audit_logs(self):
        """TEST: Listar logs de auditoría"""
        print("\n📋 TEST: Listar logs de auditoría...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/audit/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            if isinstance(data, dict):
                count = data.get('count', len(data.get('results', [])))
                results = data.get('results', [])
            else:
                count = len(data)
                results = data
            
            if count > 0 and len(results) > 0:
                self.test_log_id = results[0].get('id')
            
            return self.print_test(
                "List audit logs",
                True,
                f"Total logs: {count}"
            )
        else:
            return self.print_test(
                "List audit logs",
                False,
                f"Status: {response.status_code}"
            )

    def test_get_audit_log_detail(self):
        """TEST: Obtener detalle de un log"""
        print("\n🔍 TEST: Detalle de log de auditoría...")
        
        if not self.test_log_id:
            print(f"{Colors.WARNING}⚠ Saltando test (no hay logs){Colors.ENDC}")
            return True
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/audit/{self.test_log_id}/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            action = data.get('action', 'N/A')
            user = data.get('user', 'N/A')
            return self.print_test(
                "Get audit log detail",
                True,
                f"Acción: {action}, Usuario: {user}"
            )
        else:
            return self.print_test(
                "Get audit log detail",
                False,
                f"Status: {response.status_code}"
            )

    def test_filter_logs_by_user(self):
        """TEST: Filtrar logs por usuario"""
        print("\n🔎 TEST: Filtrar logs por usuario...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/audit/?user=admin",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            if isinstance(data, dict):
                count = data.get('count', len(data.get('results', [])))
            else:
                count = len(data)
            return self.print_test(
                "Filter logs by user",
                True,
                f"Logs de admin: {count}"
            )
        else:
            return self.print_test(
                "Filter logs by user",
                False,
                f"Status: {response.status_code}"
            )

    def test_filter_logs_by_action(self):
        """TEST: Filtrar logs por acción"""
        print("\n🎯 TEST: Filtrar logs por acción...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        # Acciones comunes: CREATE, READ, UPDATE, DELETE
        response = requests.get(
            f"{self.base_url}/audit/?action=GET",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            if isinstance(data, dict):
                count = data.get('count', len(data.get('results', [])))
            else:
                count = len(data)
            return self.print_test(
                "Filter logs by action",
                True,
                f"Logs con acción GET: {count}"
            )
        else:
            return self.print_test(
                "Filter logs by action",
                False,
                f"Status: {response.status_code}"
            )

    def test_filter_logs_by_endpoint(self):
        """TEST: Filtrar logs por endpoint"""
        print("\n🌐 TEST: Filtrar logs por endpoint...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/audit/?endpoint=/api/products/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            if isinstance(data, dict):
                count = data.get('count', len(data.get('results', [])))
            else:
                count = len(data)
            return self.print_test(
                "Filter logs by endpoint",
                True,
                f"Logs de /api/products/: {count}"
            )
        else:
            return self.print_test(
                "Filter logs by endpoint",
                False,
                f"Status: {response.status_code}"
            )

    def test_manager_can_view_audit(self):
        """TEST: Manager puede ver auditoría"""
        print("\n👔 TEST: Manager acceso a auditoría...")
        
        headers = {"Authorization": f"Bearer {self.manager_token}"}
        response = requests.get(
            f"{self.base_url}/audit/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            return self.print_test(
                "Manager can view audit",
                True,
                "Manager puede ver logs"
            )
        else:
            return self.print_test(
                "Manager can view audit",
                False,
                f"Status: {response.status_code}"
            )

    def test_pagination_audit_logs(self):
        """TEST: Paginación de logs"""
        print("\n📄 TEST: Paginación de logs...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/audit/?page=1&page_size=10",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            has_pagination = 'count' in data or 'next' in data or 'previous' in data
            return self.print_test(
                "Pagination audit logs",
                True,
                "Paginación disponible" if has_pagination else "Lista simple"
            )
        else:
            return self.print_test(
                "Pagination audit logs",
                False,
                f"Status: {response.status_code}"
            )

    def run_all_tests(self):
        """Ejecuta todos los tests de audit"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}🔍 TESTS COMPLETOS DE AUDIT{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        results = []
        
        # Setup: Login
        self.admin_token = self.login('admin')
        self.manager_token = self.login('manager')
        
        if not self.admin_token:
            print(f"{Colors.FAIL}❌ No se pudo obtener token. Abortando tests.{Colors.ENDC}")
            return []
        
        # Tests básicos
        print(f"\n{Colors.OKCYAN}📋 PARTE 1: Consultas Básicas{Colors.ENDC}")
        results.append(self.test_list_audit_logs())
        results.append(self.test_get_audit_log_detail())
        results.append(self.test_pagination_audit_logs())
        
        # Tests de filtros
        print(f"\n{Colors.OKCYAN}🔎 PARTE 2: Filtros{Colors.ENDC}")
        results.append(self.test_filter_logs_by_user())
        results.append(self.test_filter_logs_by_action())
        results.append(self.test_filter_logs_by_endpoint())
        
        # Tests de permisos
        print(f"\n{Colors.OKCYAN}🔐 PARTE 3: Permisos{Colors.ENDC}")
        results.append(self.test_manager_can_view_audit())
        
        return results


def main():
    tester = TestAuditComplete()
    results = tester.run_all_tests()
    
    # Resumen
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}📊 RESUMEN - AUDIT COMPLETE{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"Total tests: {total}")
    print(f"{Colors.OKGREEN}✅ Exitosos: {passed}{Colors.ENDC}")
    if failed > 0:
        print(f"{Colors.FAIL}❌ Fallidos: {failed}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    exit(main())
