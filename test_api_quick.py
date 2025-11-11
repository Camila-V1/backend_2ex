#!/usr/bin/env python3
"""
Script rápido para ejecutar tests de la API
Uso: python test_api_quick.py
"""
import subprocess
import sys
import os

print("🚀 Ejecutando pruebas de API...")
print("=" * 70)

# Cambiar al directorio de tests
tests_dir = os.path.join(os.path.dirname(__file__), 'tests_api')
os.chdir(tests_dir)

# Ejecutar el script principal
result = subprocess.run([sys.executable, 'run_all_tests.py'])

sys.exit(result.returncode)
