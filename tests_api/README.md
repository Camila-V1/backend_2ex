# 🧪 Suite de Pruebas API - E-commerce Backend

Sistema completo de pruebas automatizadas para validar todos los endpoints de la API.

## 📁 Estructura

```
tests_api/
├── config.py              # Configuración centralizada (URL, credenciales, colores)
├── run_all_tests.py       # Script principal que ejecuta todos los tests
├── test_auth.py           # Pruebas de autenticación (login, refresh, profile)
├── test_users.py          # Pruebas de endpoints de usuarios
├── test_products.py       # Pruebas de endpoints de productos
├── test_orders.py         # Pruebas de endpoints de órdenes
├── test_predictions.py    # Pruebas de predicciones ML
└── README.md             # Esta documentación
```

## 🚀 Uso

### Ejecutar todas las pruebas

```bash
# Desde la raíz del proyecto
python tests_api/run_all_tests.py

# O desde la carpeta tests_api
cd tests_api
python run_all_tests.py
```

### Ejecutar pruebas individuales

```bash
# Solo autenticación
python tests_api/test_auth.py

# Solo usuarios
python tests_api/test_users.py

# Solo productos
python tests_api/test_products.py

# Solo órdenes
python tests_api/test_orders.py

# Solo predicciones
python tests_api/test_predictions.py
```

## ⚙️ Configuración

Edita `config.py` para cambiar:

```python
# URL de la API (por defecto usa Render)
API_BASE_URL = 'https://backend-2ex-ecommerce.onrender.com/api'

# Para pruebas locales
API_BASE_URL = 'http://localhost:8000/api'
```

También puedes usar variable de entorno:

```bash
export API_BASE_URL=http://localhost:8000/api
python tests_api/run_all_tests.py
```

## 📊 Resultados

El script imprime:
- ✅ **Pruebas exitosas** en verde
- ❌ **Pruebas fallidas** en rojo
- 📊 **Resumen final** con porcentaje de éxito

Ejemplo de salida:

```
======================================================================
🚀 EJECUTANDO SUITE COMPLETA DE PRUEBAS API
======================================================================
🌐 API Base URL: https://backend-2ex-ecommerce.onrender.com/api
📅 Fecha: 2025-11-11 12:30:45
======================================================================

[1/5] Ejecutando pruebas de autenticación...
✅ Login admin
✅ Get profile
✅ Token refresh
✅ Login manager
✅ Login cajero

[2/5] Ejecutando pruebas de usuarios...
✅ List users (Total usuarios: 12)
✅ Get user detail (Usuario: admin - Email: admin@ecommerce.com)
✅ Create user (Usuario creado: test_user_api)

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

## 🔐 Credenciales de Prueba

Definidas en `config.py`:

```python
TEST_CREDENTIALS = {
    'admin': {'username': 'admin', 'password': 'admin123'},
    'manager': {'username': 'manager1', 'password': 'manager123'},
    'cajero': {'username': 'cajero1', 'password': 'cajero123'},
    'cliente': {'username': 'cliente1', 'password': 'cliente123'}
}
```

## 📝 Agregar Nuevas Pruebas

1. Crea un nuevo archivo `test_<modulo>.py`
2. Importa las utilidades:
   ```python
   from config import API_BASE_URL, DEFAULT_HEADERS, Colors
   from test_auth import test_login, print_result
   ```
3. Define tus funciones de prueba
4. Crea la función `run_tests()` que retorna resultados
5. Agrega el módulo a `run_all_tests.py`

## 🎯 Cobertura de Pruebas

- **Autenticación**: Login, refresh token, obtener perfil
- **Usuarios**: Listar, crear, obtener detalle
- **Productos**: Listar, buscar, filtrar por categoría
- **Órdenes**: Listar, crear, dashboard admin
- **Predicciones**: Predicciones de ventas con ML

## 📦 Dependencias

```bash
pip install requests
```

## 🔄 Integración con CI/CD

Puedes usar estos tests en pipelines de CI/CD:

```yaml
# Ejemplo GitHub Actions
- name: Run API Tests
  run: python tests_api/run_all_tests.py
```

El script retorna código de salida:
- `0` si el 80% o más de pruebas pasan
- `1` si menos del 80% de pruebas pasan
