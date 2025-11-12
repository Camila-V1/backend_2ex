# 🔍 ANÁLISIS DE POTENCIALES ERRORES EN FRONTEND (web_2ex)

**Fecha de análisis:** 11 de Noviembre, 2025  
**Backend testeado:** ✅ 59/59 tests pasando (100%)  
**Frontend repo:** https://github.com/Camila-V1/web_2ex  
**URL Producción:** https://web-2ex.vercel.app

---

## 🎯 ERRORES POTENCIALES DETECTADOS

Basándome en los tests funcionales exitosos del backend y commits recientes del frontend, estos son los **errores más probables**:

---

### 🚨 ERROR 1: Endpoints Incorrectos en Frontend

**Problema:** El frontend puede estar llamando endpoints que **no existen** o con **parámetros incorrectos**.

#### ✅ Endpoints CORRECTOS validados por tests:

```javascript
// ✅ AUTENTICACIÓN
POST /api/token/                    // Login (username, password)
POST /api/token/refresh/            // Refresh (refresh token)
GET  /api/users/profile/            // Perfil autenticado

// ✅ PRODUCTOS
GET  /api/products/                 // Listar (con paginación)
GET  /api/products/{id}/            // Detalle
GET  /api/products/categories/      // Categorías
GET  /api/products/?search=         // Búsqueda
GET  /api/products/?category=       // Filtro

// ✅ ÓRDENES
POST /api/orders/create/            // Crear orden
GET  /api/orders/                   // Mis órdenes
GET  /api/orders/{id}/              // Detalle
GET  /api/orders/admin/             // Admin todas (admin/manager)
PATCH /api/orders/admin/{id}/       // Admin actualizar
POST /api/orders/nlp-cart/          // NLP (campo: "prompt")

// ✅ WALLET
GET  /api/wallet/my_wallet/         // Mi billetera
POST /api/wallet/{id}/deposit/      // Depósito (amount)
POST /api/wallet/{id}/withdraw/     // Retiro (amount)
GET  /api/wallet/{id}/transactions/ // Transacciones

// ✅ DELIVERIES
GET  /api/deliveries/               // Listar
GET  /api/deliveries/zones/         // Zonas
GET  /api/deliveries/warranties/    // Garantías
GET  /api/deliveries/returns/       // Devoluciones

// ✅ REPORTS
GET  /api/reports/sales/preview/?start_date=&end_date=    // Preview
GET  /api/reports/products/preview/                       // Preview
GET  /api/reports/sales/?format=pdf&start_date=&end_date= // PDF
GET  /api/reports/orders/{id}/invoice/                    // Factura

// ✅ AUDIT
GET  /api/audit/                    // Logs
GET  /api/audit/?user=              // Filtro usuario
GET  /api/audit/?action=            // Filtro acción
```

#### ❌ Errores comunes en el frontend:

```javascript
// ❌ INCORRECTO:
POST /api/orders/          // No existe - debe ser /api/orders/create/
GET  /api/wallet/          // No existe - debe ser /api/wallet/my_wallet/
POST /api/wallet/deposit/  // Falta el ID - debe ser /api/wallet/{id}/deposit/
POST /api/orders/nlp-cart/ { text: "..." }  // Campo incorrecto - debe ser "prompt"

// ✅ CORRECTO:
POST /api/orders/create/   { items: [...] }
GET  /api/wallet/my_wallet/
POST /api/wallet/1/deposit/ { amount: 100 }
POST /api/orders/nlp-cart/ { prompt: "agrega laptop" }
```

---

### 🚨 ERROR 2: Permisos y Autenticación

**Problema:** El frontend puede tener lógica de permisos **incorrecta** basándose en el bug 403 corregido.

#### ✅ Permisos CORRECTOS validados:

```javascript
// ✅ Crear órdenes - CUALQUIER usuario autenticado
// BUG CORREGIDO: Ya no requiere rol CAJERO
if (isAuthenticated) {
  // Admin, Manager, Cajero, Cliente - TODOS pueden crear órdenes
  createOrder();
}

// ❌ INCORRECTO en frontend:
if (role === 'CAJERO') {  // ¡Ya no es necesario!
  createOrder();
}

// ✅ CORRECTO:
if (isAuthenticated) {  // Suficiente con estar autenticado
  createOrder();
}
```

#### 🔐 Roles y permisos correctos:

```javascript
// ADMIN + MANAGER:
- Ver órdenes de todos (GET /api/orders/admin/)
- Actualizar órdenes (PATCH /api/orders/admin/{id}/)
- Ver dashboard (GET /api/orders/admin/dashboard/)
- Ver reportes (GET /api/reports/*)
- Ver auditoría (GET /api/audit/)

// CAJERO:
- Crear órdenes (POST /api/orders/create/)
- Ver sus propias órdenes (GET /api/orders/)

// CLIENTE:
- Crear órdenes (POST /api/orders/create/)
- Ver sus propias órdenes (GET /api/orders/)
- Wallet completo (deposit, withdraw, transactions)

// DELIVERY:
- Ver entregas asignadas (GET /api/deliveries/my-deliveries/)
- Actualizar estado de entregas
```

---

### 🚨 ERROR 3: Manejo de Estados de Órdenes

**Problema:** El frontend puede estar usando **estados incorrectos** de órdenes.

#### ✅ Estados VÁLIDOS confirmados por backend:

```python
# Estados correctos en shop_orders/models.py:
ORDER_STATUS_CHOICES = [
    ('PENDING', 'Pendiente'),
    ('PROCESSING', 'En Proceso'),    # ⚠️ NO usar en tests
    ('SHIPPED', 'Enviado'),           # ✅ Usar este
    ('DELIVERED', 'Entregado'),
    ('CANCELLED', 'Cancelado'),
]
```

#### ❌ Error común:

```javascript
// ❌ Frontend usando estados no válidos:
const statuses = ['PENDING', 'PROCESSING', 'COMPLETED'];  // 'COMPLETED' no existe

// ✅ Correcto:
const statuses = ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED'];
```

---

### 🚨 ERROR 4: Formato de Fechas en Reports

**Problema:** Reports requieren **fechas obligatorias** en formato específico.

#### ✅ Formato correcto validado:

```javascript
// ✅ CORRECTO:
const params = {
  start_date: '2024-01-01',  // YYYY-MM-DD
  end_date: '2024-12-31',    // YYYY-MM-DD
  format: 'pdf'              // 'pdf' o 'excel'
};

fetch(`/api/reports/sales/?${new URLSearchParams(params)}`);

// ❌ INCORRECTO:
fetch('/api/reports/sales/');  // ⚠️ Error 400 - faltan fechas obligatorias
fetch('/api/reports/sales/?format=pdf');  // ⚠️ Error 400 - faltan fechas
```

---

### 🚨 ERROR 5: Headers de Autenticación

**Problema:** Token JWT puede estar mal formateado en headers.

#### ✅ Formato correcto:

```javascript
// ✅ CORRECTO:
const token = localStorage.getItem('access_token');
headers: {
  'Authorization': `Bearer ${token}`,  // Espacio después de "Bearer"
  'Content-Type': 'application/json'
}

// ❌ INCORRECTO:
headers: {
  'Authorization': token,              // Falta "Bearer "
  'Authorization': `Token ${token}`,   // "Token" incorrecto - debe ser "Bearer"
  'Authorization': `bearer ${token}`,  // "bearer" en minúscula puede fallar
}
```

---

### 🚨 ERROR 6: Manejo de Paginación

**Problema:** La paginación puede no estar implementada correctamente.

#### ✅ Respuesta paginada del backend:

```javascript
// Respuesta real del backend:
{
  "count": 76,
  "next": "http://.../api/products/?page=2",
  "previous": null,
  "results": [
    { id: 1, name: "Producto 1", ... },
    // ... más productos
  ]
}

// ✅ Frontend correcto:
const response = await fetch('/api/products/');
const data = await response.json();
const products = data.results;  // Extraer "results"
const total = data.count;
const hasNext = data.next !== null;

// ❌ Frontend incorrecto:
const products = await response.json();  // Asume array directo
// Error: products es objeto con {count, next, previous, results}
```

---

### 🚨 ERROR 7: CORS y Proxy de Vercel

**Problema:** Commits recientes muestran problemas de **CORS** y **proxy**.

#### Archivos sospechosos:
- `vercel.json` - Última modificación: 5 horas atrás
- `.env.production` - Configuración de proxy
- Múltiples scripts de actualización CORS

#### ✅ Configuración correcta:

```javascript
// vercel.json - Debe tener:
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://backend-2ex-ecommerce.onrender.com/api/:path*"
    }
  ]
}

// O en frontend - usar URL completa:
const API_BASE_URL = 'https://backend-2ex-ecommerce.onrender.com/api';
```

---

### 🚨 ERROR 8: Credenciales de Prueba

**Problema:** El frontend puede usar **credenciales incorrectas** para testing.

#### ✅ Credenciales CORRECTAS validadas:

```javascript
// ✅ CORRECTO (validado por 59 tests):
const testUsers = {
  admin: {
    username: 'admin',
    password: 'admin123'
  },
  manager: {
    username: 'carlos_manager',
    password: 'carlos123'  // ⚠️ NO 'manager123'
  },
  cajero: {
    username: 'luis_cajero',
    password: 'luis123'    // ⚠️ NO 'cajero123'
  },
  delivery: {
    username: 'pedro_delivery',
    password: 'pedro123'
  }
};

// ❌ INCORRECTO (credenciales antiguas):
password: 'manager123'  // Ya no funciona
password: 'cajero123'   // Ya no funciona
```

---

### 🚨 ERROR 9: NLP Cart - Campo Incorrecto

**Problema:** El endpoint NLP usa **"prompt"** no **"text"**.

```javascript
// ❌ INCORRECTO:
POST /api/orders/nlp-cart/
{
  "text": "agrega 2 laptops"  // Campo incorrecto
}

// ✅ CORRECTO:
POST /api/orders/nlp-cart/
{
  "prompt": "agrega 2 laptops"  // Campo correcto
}
```

---

### 🚨 ERROR 10: Wallet Endpoints

**Problema:** Los endpoints de wallet tienen **estructura específica**.

```javascript
// ❌ INCORRECTO:
GET  /api/wallet/               // No existe
POST /api/wallet/deposit/       // Falta ID
POST /api/wallet/withdraw/      // Falta ID

// ✅ CORRECTO:
GET  /api/wallet/my_wallet/     // Obtener mi billetera primero
// Response: { id: 1, balance: "100.00", ... }

POST /api/wallet/1/deposit/     // Usar ID de la respuesta anterior
{ amount: 50 }

POST /api/wallet/1/withdraw/
{ amount: 25 }

GET  /api/wallet/1/transactions/
```

---

## 🔧 SCRIPT DE VALIDACIÓN PARA FRONTEND

Crea este script en el frontend para validar endpoints:

```javascript
// validate_endpoints.js
const API_BASE = 'https://backend-2ex-ecommerce.onrender.com/api';

const tests = [
  // Login
  {
    name: 'Login admin',
    method: 'POST',
    url: '/token/',
    body: { username: 'admin', password: 'admin123' },
    expectedStatus: 200
  },
  
  // Productos
  {
    name: 'List products',
    method: 'GET',
    url: '/products/',
    expectedStatus: 200,
    expectPagination: true  // Debe tener {count, results}
  },
  
  // Órdenes
  {
    name: 'Create order',
    method: 'POST',
    url: '/orders/create/',  // ⚠️ NO /orders/
    body: { items: [] },
    requiresAuth: true,
    expectedStatus: 201
  },
  
  // Wallet
  {
    name: 'My wallet',
    method: 'GET',
    url: '/wallet/my_wallet/',  // ⚠️ NO /wallet/
    requiresAuth: true,
    expectedStatus: 200
  },
  
  // Reports (con fechas)
  {
    name: 'Sales report preview',
    method: 'GET',
    url: '/reports/sales/preview/?start_date=2024-01-01&end_date=2024-12-31',
    requiresAuth: true,
    expectedStatus: 200
  }
];

// Ejecutar tests
tests.forEach(async (test) => {
  const options = {
    method: test.method,
    headers: {
      'Content-Type': 'application/json',
      ...(test.requiresAuth && { 'Authorization': `Bearer ${token}` })
    },
    ...(test.body && { body: JSON.stringify(test.body) })
  };
  
  const response = await fetch(API_BASE + test.url, options);
  const status = response.status;
  
  if (status !== test.expectedStatus) {
    console.error(`❌ ${test.name}: Expected ${test.expectedStatus}, got ${status}`);
  } else {
    console.log(`✅ ${test.name}: OK`);
  }
  
  if (test.expectPagination) {
    const data = await response.json();
    if (!data.results || !data.count) {
      console.error(`❌ ${test.name}: Missing pagination (results/count)`);
    }
  }
});
```

---

## 📋 CHECKLIST DE VALIDACIÓN

Revisa estos puntos en el código del frontend:

### Configuración
- [ ] `vercel.json` tiene proxy correcto o usa URL completa
- [ ] `.env.production` tiene `VITE_API_URL` correcto
- [ ] Headers de autenticación usan `Bearer ${token}`

### Endpoints
- [ ] Órdenes usa `/api/orders/create/` no `/api/orders/`
- [ ] Wallet usa `/api/wallet/my_wallet/` no `/api/wallet/`
- [ ] Deposit/Withdraw incluyen ID: `/api/wallet/{id}/deposit/`
- [ ] NLP usa campo `prompt` no `text`
- [ ] Reports incluyen `start_date` y `end_date`

### Permisos
- [ ] Crear orden solo requiere `isAuthenticated` (no rol específico)
- [ ] Admin/Manager pueden ver `/api/orders/admin/`
- [ ] Manager puede ver `/api/reports/` y `/api/audit/`

### Datos
- [ ] Estados de órdenes son: PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED
- [ ] Respuestas paginadas extraen `data.results` no `data` directamente
- [ ] Fechas en formato YYYY-MM-DD

### Credenciales
- [ ] Manager: carlos123 (NO manager123)
- [ ] Cajero: luis123 (NO cajero123)

---

## 🚀 PRÓXIMOS PASOS

1. **Clonar el repositorio del frontend localmente**
2. **Buscar estos errores en el código**:
   ```bash
   # Buscar endpoints incorrectos
   grep -r "/api/orders/" src/
   grep -r "/api/wallet/" src/
   grep -r '"text":' src/
   
   # Buscar permisos incorrectos
   grep -r "IsCajeroUser" src/
   grep -r "role === 'CAJERO'" src/
   ```

3. **Validar configuración**:
   - Revisar `vercel.json`
   - Revisar `.env.production`
   - Revisar archivos de configuración API

4. **Crear tests E2E en el frontend** basados en los 59 tests exitosos del backend

---

## 📊 RESUMEN

**Probabilidad de errores:**
- 🔴 **ALTA**: Endpoints incorrectos (orders/, wallet/)
- 🔴 **ALTA**: Reports sin fechas obligatorias
- 🟡 **MEDIA**: Permisos basados en bug 403 antiguo
- 🟡 **MEDIA**: Campo "text" en lugar de "prompt" (NLP)
- 🟢 **BAJA**: Headers de autenticación (probablemente correcto)

**Archivos críticos a revisar:**
- `src/services/api.js` o `src/api/`
- `src/utils/auth.js` o `src/services/auth.js`
- `vercel.json`
- `.env.production`

---

**Con 59 tests exitosos en backend, cualquier error está en el frontend** 🎯
