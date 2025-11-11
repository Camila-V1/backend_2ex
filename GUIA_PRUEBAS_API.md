# 🧪 Sistema de Pruebas API - Guía Rápida

## 📌 ¿Qué hace este sistema?

Este sistema te permite **probar todos los endpoints de tu API** de forma automatizada. Cada vez que despliegas, la base de datos se limpia y repuebla con los mismos datos, garantizando consistencia en las pruebas.

## 🚀 Uso Rápido

### Windows (PowerShell)
```powershell
.\test_api_quick.ps1
```

### Windows/Linux/Mac (Python)
```bash
python test_api_quick.py
```

### Ejecutar módulos individuales
```bash
cd tests_api
python test_auth.py        # Solo autenticación
python test_users.py       # Solo usuarios
python test_products.py    # Solo productos
python test_orders.py      # Solo órdenes
python test_predictions.py # Solo predicciones ML
```

## 📊 ¿Qué prueba?

### 🔐 Autenticación (`test_auth.py`)
- ✅ Login con admin/manager/cajero/cliente
- ✅ Refresh token
- ✅ Obtener perfil de usuario

### 👥 Usuarios (`test_users.py`)
- ✅ Listar todos los usuarios
- ✅ Obtener detalle de usuario
- ✅ Crear nuevo usuario

### 📦 Productos (`test_products.py`)
- ✅ Listar productos
- ✅ Buscar productos
- ✅ Filtrar por categoría
- ✅ Listar categorías

### 🛒 Órdenes (`test_orders.py`)
- ✅ Listar órdenes del usuario
- ✅ Obtener detalle de orden
- ✅ Dashboard de administrador

### 📈 Predicciones ML (`test_predictions.py`)
- ✅ Predicciones de ventas

## ⚙️ Configuración

### Cambiar URL de la API

**Opción 1: Variable de entorno**
```powershell
# PowerShell
$env:API_BASE_URL = "http://localhost:8000/api"
python tests_api/run_all_tests.py

# Bash
export API_BASE_URL=http://localhost:8000/api
python tests_api/run_all_tests.py
```

**Opción 2: Editar `tests_api/config.py`**
```python
API_BASE_URL = 'http://localhost:8000/api'  # Para local
# API_BASE_URL = 'https://backend-2ex-ecommerce.onrender.com/api'  # Para producción
```

## 🔄 Deploy Automático

Cada vez que haces `git push`, Render automáticamente:

1. 🗑️ **Limpia la BD** (`python manage.py flush --no-input`)
2. 🌱 **Repuebla datos** (`python seed_data.py`)
3. ✅ **Deploy completo**

Esto garantiza que **siempre tengas los mismos datos** para pruebas consistentes.

## 👥 Usuarios de Prueba

```python
# Admin (acceso total)
username: admin
password: admin123

# Manager (gestión de inventario)
username: manager1
password: manager123

# Cajero (punto de venta)
username: cajero1
password: cajero123

# Cliente (compras)
username: cliente1
password: cliente123
```

## 📝 Resultados

```
======================================================================
📊 RESUMEN FINAL
======================================================================
Autenticación: 5/5 pruebas exitosas
Usuarios: 3/3 pruebas exitosas
Productos: 5/5 pruebas exitosas
Órdenes: 3/3 pruebas exitosas
Predicciones: 1/1 pruebas exitosas
======================================================================
TOTAL: 17/17 pruebas exitosas (100.0%)
✅ Exitosas: 17
❌ Fallidas: 0
======================================================================
```

## 🛠️ Agregar Nuevas Pruebas

1. **Crea** `tests_api/test_<modulo>.py`
2. **Copia la estructura** de un test existente
3. **Define tus funciones** de prueba
4. **Agrega** el módulo a `run_all_tests.py`

Ejemplo:
```python
from config import API_BASE_URL, DEFAULT_HEADERS, Colors
from test_auth import test_login, print_result

def test_mi_endpoint(access_token):
    response = requests.get(
        f"{API_BASE_URL}/mi-endpoint/",
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    if response.status_code == 200:
        print_result("Mi test", True, "Todo bien!")
    else:
        print_result("Mi test", False, f"Error: {response.status_code}")
```

## 🐛 Troubleshooting

### Error: `Connection refused`
- Verifica que la API esté corriendo
- Revisa la URL en `config.py`

### Error: `401 Unauthorized`
- Verifica las credenciales en `config.py`
- Asegúrate que los usuarios existan en la BD

### Error: `404 Not Found`
- Verifica que el endpoint exista
- Revisa las URLs en `urls.py`

## 📚 Documentación Completa

Ver `tests_api/README.md` para documentación detallada.

## 🎯 Tips

- ✅ Ejecuta las pruebas **después de cada deploy**
- ✅ Usa las pruebas para **detectar errores temprano**
- ✅ Agrega nuevas pruebas cuando **crees nuevos endpoints**
- ✅ Mantén las pruebas **simples y enfocadas**

---

¿Dudas? Revisa el código en `tests_api/` - está bien comentado! 🚀
