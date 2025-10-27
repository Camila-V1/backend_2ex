# 🌱 Seed Data - Guía de Uso

## 📋 Descripción

Script completo para poblar la base de datos del e-commerce con datos de prueba, incluyendo suficientes registros para entrenar el modelo de Machine Learning.

## 🚀 Uso Rápido

### 1️⃣ Poblar Base de Datos

```bash
python seed_data.py
```

Este script:
- ✅ Limpia todos los datos existentes
- ✅ Crea 12 usuarios con diferentes roles
- ✅ Crea 8 categorías de productos
- ✅ Crea 35 productos variados
- ✅ Genera ~150 reviews de clientes
- ✅ Genera 150-200 órdenes (80% PAID para ML)
- ✅ Crea órdenes con fechas de los últimos 12 meses
- ✅ Genera archivo `CREDENCIALES_ACCESO.txt` con todos los usuarios

### 2️⃣ Entrenar Modelo de ML

```bash
python manage.py train_sales_model
```

Entrena el modelo Random Forest con las órdenes PAID generadas.

## 👥 Usuarios Creados

### 👑 Administradores (ADMIN)
| Usuario | Email | Password | Permisos |
|---------|-------|----------|----------|
| `admin` | admin@ecommerce.com | `admin123` | Superusuario, acceso total |
| `maria_admin` | maria.admin@ecommerce.com | `maria123` | Admin sin superusuario |

### 👔 Managers (MANAGER)
| Usuario | Email | Password | Permisos |
|---------|-------|----------|----------|
| `carlos_manager` | carlos.manager@ecommerce.com | `carlos123` | Gestión órdenes, productos, reportes |
| `ana_manager` | ana.manager@ecommerce.com | `ana123` | Gestión órdenes, productos, reportes |

### 💰 Cajeros (CAJERO)
| Usuario | Email | Password | Permisos |
|---------|-------|----------|----------|
| `luis_cajero` | luis.cajero@ecommerce.com | `luis123` | Ver órdenes y productos |
| `sofia_cajero` | sofia.cajero@ecommerce.com | `sofia123` | Ver órdenes y productos |

### 👥 Clientes
| Usuario | Email | Password |
|---------|-------|----------|
| `juan_cliente` | juan@email.com | `juan123` |
| `laura_cliente` | laura@email.com | `laura123` |
| `pedro_cliente` | pedro@email.com | `pedro123` |
| `carmen_cliente` | carmen@email.com | `carmen123` |
| `diego_cliente` | diego@email.com | `diego123` |
| `elena_cliente` | elena@email.com | `elena123` |

## 📊 Datos Generados

### Categorías (8)
- Electrónica
- Computadoras
- Celulares
- Audio
- Gaming
- Hogar
- Oficina
- Deportes

### Productos (35)
Productos variados en todas las categorías con:
- Nombres descriptivos
- Precios realistas ($299.99 - $15,999.99)
- Stock variable (8-100 unidades)
- Información de garantía
- Reviews de clientes (promedio 4.3/5 estrellas)

### Órdenes (150-200)
- **80% PAID** - Para entrenamiento de ML
- **10% PENDING** - Órdenes pendientes
- **5% SHIPPED** - Órdenes enviadas
- **5% CANCELLED** - Órdenes canceladas
- Fechas distribuidas en los últimos 12 meses
- 1-5 productos por orden
- Total: ~500+ items en órdenes

### Reviews (~150)
- Calificaciones: 1-5 estrellas (ponderadas hacia 4-5)
- Comentarios realistas según la calificación
- Una review por usuario-producto (constraint respetado)

## 🤖 Machine Learning

### Datos para Entrenamiento
- ✅ **138+ órdenes PAID** (mínimo requerido: 10)
- ✅ **432+ items** en órdenes pagadas
- ✅ **12 meses** de historial de ventas
- ✅ **35 productos** en 8 categorías
- ✅ **Variedad** de cantidades y precios

### Entrenar Modelo

```bash
python manage.py train_sales_model
```

**Output esperado:**
```
Iniciando el entrenamiento del modelo de predicción de ventas...
¡Éxito! Modelo entrenado y guardado exitosamente.
  - Guardado en: .../predictions/sales_model.joblib
  - MSE: ~0.77
  - Muestras usadas: 432+
```

### Obtener Predicciones

**Endpoint:** `GET /api/predictions/sales-forecast/`

**Requiere autenticación:** Sí (Token JWT)

**Respuesta:**
```json
{
  "predictions": [
    {"date": "2025-10-26", "predicted_sales": 15.2},
    {"date": "2025-10-27", "predicted_sales": 12.8},
    ...
  ]
}
```

## 🔐 Autenticación

### Login

```bash
POST /api/users/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Respuesta:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJh...",
  "access": "eyJ0eXAiOiJKV1QiLCJh...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@ecommerce.com",
    "role": "ADMIN"
  }
}
```

### Usar Token

```bash
GET /api/products/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJh...
```

## 📁 Archivos Generados

### `CREDENCIALES_ACCESO.txt`
Archivo completo con:
- ✅ Todos los usuarios y contraseñas
- ✅ Roles y permisos de cada usuario
- ✅ Estadísticas de la base de datos
- ✅ Instrucciones de autenticación
- ✅ Enlaces útiles (Swagger, ReDoc, Admin)
- ✅ Guía de Machine Learning

### `predictions/sales_model.joblib`
Modelo entrenado de Random Forest para predicciones.

## 🔄 Re-poblar Base de Datos

Si necesitas regenerar todos los datos:

```bash
python seed_data.py
```

⚠️ **ADVERTENCIA:** Este comando **BORRA TODOS LOS DATOS** existentes antes de crear nuevos.

## 🧪 Probar el Sistema

### 1. Poblar datos
```bash
python seed_data.py
```

### 2. Entrenar ML
```bash
python manage.py train_sales_model
```

### 3. Iniciar servidor
```bash
python manage.py runserver
```

### 4. Probar endpoints
```bash
# Ver productos
curl http://127.0.0.1:8000/api/products/

# Login como admin
curl -X POST http://127.0.0.1:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Obtener predicciones (con token)
curl http://127.0.0.1:8000/api/predictions/sales-forecast/ \
  -H "Authorization: Bearer <TOKEN>"
```

## 📝 Personalización

### Cambiar cantidad de órdenes

Edita `seed_data.py`, línea 378:

```python
# Crear entre 150-200 órdenes
num_orders = random.randint(150, 200)  # Cambiar estos números
```

### Cambiar distribución de estados

Edita `seed_data.py`, línea 387:

```python
status = random.choices(
    [PAID, PENDING, SHIPPED, CANCELLED],
    weights=[80, 10, 5, 5]  # Cambiar estos pesos (deben sumar 100)
)[0]
```

### Agregar más productos

Agrega al array `products_data` en `seed_data.py`, línea 136.

## ⚠️ Notas Importantes

1. **Solo para desarrollo:** Estas credenciales son para pruebas
2. **Patrón de contraseñas:** Todas siguen `<nombre>123`
3. **Datos aleatorios:** Las órdenes y reviews son generadas aleatoriamente
4. **Timezone:** Las órdenes usan fechas con zona horaria activa
5. **Constraint respetado:** Un usuario solo puede hacer una review por producto

## 🐛 Troubleshooting

### Error: "No module named 'django'"
```bash
pip install -r requirements.txt
```

### Error: "No such table"
```bash
python manage.py migrate
```

### ML requiere más datos
Edita el script para generar más órdenes (aumenta `num_orders`).

## 📚 Referencias

- **API Docs:** http://127.0.0.1:8000/api/docs/
- **ReDoc:** http://127.0.0.1:8000/api/redoc/
- **Django Admin:** http://127.0.0.1:8000/admin/
- **Archivo de credenciales:** `CREDENCIALES_ACCESO.txt`

## 🎯 Próximos Pasos

1. ✅ Ejecutar `python seed_data.py`
2. ✅ Revisar `CREDENCIALES_ACCESO.txt`
3. ✅ Entrenar modelo: `python manage.py train_sales_model`
4. ✅ Iniciar servidor: `python manage.py runserver`
5. ✅ Probar login con usuario `admin` / `admin123`
6. ✅ Explorar API en http://127.0.0.1:8000/api/docs/
7. ✅ Verificar predicciones en `/api/predictions/sales-forecast/`

---

¡Base de datos lista para desarrollo y Machine Learning! 🚀
