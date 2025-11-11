# tests_api/config.py
"""
Configuración centralizada para pruebas de API
"""
import os

# URL base de la API (cambiar según entorno)
API_BASE_URL = os.getenv('API_BASE_URL', 'https://backend-2ex-ecommerce.onrender.com/api')

# Credenciales de prueba
TEST_CREDENTIALS = {
    'admin': {
        'username': 'admin',
        'password': 'admin123'
    },
    'manager': {
        'username': 'manager1',
        'password': 'manager123'
    },
    'cajero': {
        'username': 'cajero1',
        'password': 'cajero123'
    },
    'cliente': {
        'username': 'cliente1',
        'password': 'cliente123'
    }
}

# Headers por defecto
DEFAULT_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Colores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
