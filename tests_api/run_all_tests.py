#!/usr/bin/env python3
# tests_api/run_all_tests.py
"""
Script principal que ejecuta todos los tests de la API
"""
import sys
import os
from datetime import datetime

# Agregar el directorio actual al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Colors, API_BASE_URL
import test_auth
import test_users
import test_products
import test_orders
import test_predictions

def print_header():
    """Imprime el header principal"""
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}🚀 EJECUTANDO SUITE COMPLETA DE PRUEBAS API{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}🌐 API Base URL: {API_BASE_URL}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")

def print_summary(all_results):
    """Imprime el resumen final de todas las pruebas"""
    total_tests = sum(r['total'] for r in all_results.values())
    total_passed = sum(r['passed'] for r in all_results.values())
    total_failed = sum(r['failed'] for r in all_results.values())
    
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}📊 RESUMEN FINAL{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    
    for module_name, results in all_results.items():
        color = Colors.OKGREEN if results['failed'] == 0 else Colors.WARNING
        print(f"{color}{module_name}: {results['passed']}/{results['total']} pruebas exitosas{Colors.ENDC}")
    
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    
    color = Colors.OKGREEN if success_rate >= 80 else Colors.WARNING if success_rate >= 50 else Colors.FAIL
    print(f"{color}{Colors.BOLD}TOTAL: {total_passed}/{total_tests} pruebas exitosas ({success_rate:.1f}%){Colors.ENDC}")
    print(f"{Colors.OKGREEN}✅ Exitosas: {total_passed}{Colors.ENDC}")
    print(f"{Colors.FAIL}❌ Fallidas: {total_failed}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}\n")
    
    return success_rate >= 80

def main():
    """Ejecuta todos los módulos de pruebas"""
    print_header()
    
    all_results = {}
    
    # Módulo 1: Autenticación
    try:
        print(f"\n{Colors.BOLD}[1/5] Ejecutando pruebas de autenticación...{Colors.ENDC}")
        all_results['Autenticación'] = test_auth.run_tests()
    except Exception as e:
        print(f"{Colors.FAIL}Error en módulo de autenticación: {str(e)}{Colors.ENDC}")
        all_results['Autenticación'] = {'total': 0, 'passed': 0, 'failed': 0}
    
    # Módulo 2: Usuarios
    try:
        print(f"\n{Colors.BOLD}[2/5] Ejecutando pruebas de usuarios...{Colors.ENDC}")
        all_results['Usuarios'] = test_users.run_tests()
    except Exception as e:
        print(f"{Colors.FAIL}Error en módulo de usuarios: {str(e)}{Colors.ENDC}")
        all_results['Usuarios'] = {'total': 0, 'passed': 0, 'failed': 0}
    
    # Módulo 3: Productos
    try:
        print(f"\n{Colors.BOLD}[3/5] Ejecutando pruebas de productos...{Colors.ENDC}")
        all_results['Productos'] = test_products.run_tests()
    except Exception as e:
        print(f"{Colors.FAIL}Error en módulo de productos: {str(e)}{Colors.ENDC}")
        all_results['Productos'] = {'total': 0, 'passed': 0, 'failed': 0}
    
    # Módulo 4: Órdenes
    try:
        print(f"\n{Colors.BOLD}[4/5] Ejecutando pruebas de órdenes...{Colors.ENDC}")
        all_results['Órdenes'] = test_orders.run_tests()
    except Exception as e:
        print(f"{Colors.FAIL}Error en módulo de órdenes: {str(e)}{Colors.ENDC}")
        all_results['Órdenes'] = {'total': 0, 'passed': 0, 'failed': 0}
    
    # Módulo 5: Predicciones
    try:
        print(f"\n{Colors.BOLD}[5/5] Ejecutando pruebas de predicciones...{Colors.ENDC}")
        all_results['Predicciones'] = test_predictions.run_tests()
    except Exception as e:
        print(f"{Colors.FAIL}Error en módulo de predicciones: {str(e)}{Colors.ENDC}")
        all_results['Predicciones'] = {'total': 0, 'passed': 0, 'failed': 0}
    
    # Imprimir resumen final
    success = print_summary(all_results)
    
    # Retornar código de salida apropiado
    return 0 if success else 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
