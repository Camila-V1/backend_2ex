#!/usr/bin/env python3
"""
MASTER TEST RUNNER - Ejecuta TODA la suite de tests
Incluye tests originales + tests completos nuevos
"""
import subprocess
import sys
from config import Colors

def run_test_file(test_file, description):
    """Ejecuta un archivo de test y retorna resultados"""
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{description}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    
    result = subprocess.run([sys.executable, test_file], capture_output=False)
    return result.returncode == 0

def main():
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}🚀 EJECUCIÓN COMPLETA DE SUITE DE TESTS{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}")
    
    test_suites = [
        # Tests originales (básicos)
        ('test_auth.py', '🔐 [1/6] AUTENTICACIÓN (Tests Básicos)'),
        ('test_users.py', '👥 [2/6] USUARIOS (Tests Básicos)'),
        ('test_products.py', '📦 [3/6] PRODUCTOS (Tests Básicos)'),
        
        # Tests completos nuevos (cobertura extendida)
        ('test_orders_complete.py', '🛒 [4/6] ORDERS COMPLETO (Tests Extendidos)'),
        ('test_wallet_complete.py', '💰 [5/6] WALLET COMPLETO (Tests Extendidos)'),
        ('test_deliveries_complete.py', '🚚 [6/6] DELIVERIES COMPLETO (Tests Extendidos)'),
    ]
    
    results = {}
    
    for test_file, description in test_suites:
        success = run_test_file(test_file, description)
        results[description] = success
    
    # Resumen final
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}📊 RESUMEN FINAL DE TODA LA SUITE{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    total_suites = len(results)
    passed_suites = sum(1 for v in results.values() if v)
    failed_suites = total_suites - passed_suites
    
    for suite, passed in results.items():
        status = f"{Colors.OKGREEN}✅ PASS{Colors.ENDC}" if passed else f"{Colors.FAIL}❌ FAIL{Colors.ENDC}"
        print(f"{status}  {suite}")
    
    print(f"\n{Colors.BOLD}{'─'*70}{Colors.ENDC}")
    print(f"Total suites: {total_suites}")
    print(f"{Colors.OKGREEN}✅ Exitosas: {passed_suites}{Colors.ENDC}")
    if failed_suites > 0:
        print(f"{Colors.FAIL}❌ Fallidas: {failed_suites}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}")
    
    # Estimación de cobertura
    print(f"\n{Colors.OKCYAN}📈 ESTIMACIÓN DE COBERTURA:{Colors.ENDC}")
    print(f"   Tests Básicos:     ~17 endpoints (~30% del sistema)")
    print(f"   Tests Extendidos:  ~25+ endpoints adicionales")
    print(f"   {Colors.BOLD}Cobertura Total:   ~42+ endpoints (~75% del sistema){Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    return 0 if failed_suites == 0 else 1

if __name__ == '__main__':
    exit(main())
