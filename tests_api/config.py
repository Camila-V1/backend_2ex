# tests_api/config.py
"""
Configuración centralizada para pruebas de API
"""
import os

# URL base de la API (cambiar según entorno)
API_BASE_URL = os.getenv('API_BASE_URL', 'https://backend-2ex-ecommerce.onrender.com/api')

# Credenciales de prueba (deben coincidir EXACTAMENTE con seed_data.py)
TEST_CREDENTIALS = {
    'admin': {
        'username': 'admin',
        'password': 'admin123'
    },
    'manager': {
        'username': 'carlos_manager',
        'password': 'carlos123'  # Contraseña real de seed_data.py
    },
    'cajero': {
        'username': 'luis_cajero',
        'password': 'luis123'  # Contraseña real de seed_data.py
    },
    'delivery': {
        'username': 'pedro_delivery',
        'password': 'pedro123'  # Contraseña real de seed_data.py
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
