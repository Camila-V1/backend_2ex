# 🔴 Solución: Error 403 para Rol CAJERO

## 📋 Diagnóstico

### ✅ Backend funcionando correctamente
El backend está rechazando correctamente las peticiones. Los errores 403 son **ESPERADOS** y **CORRECTOS**.

### ❌ Frontend tiene error de lógica

**Usuario**: `luis_cajero`  
**Rol**: `CAJERO`  
**is_staff**: `true`  
**Problema**: Frontend lo está redirigiendo erróneamente a `/admin/dashboard`

---

## 🔍 Análisis de Logs

```javascript
🔍 [AUTHCONTEXT 10] DEBUG - role: CAJERO
🔍 [LOGIN 7] DEBUG - result.user?.is_staff: true
🔍 [LOGIN 8] DEBUG - result.user?.role: CAJERO
✅ [LOGIN 9] Usuario es ADMIN - Redirigiendo a /admin/dashboard  // ❌ INCORRECTO
```

**Error en el código del frontend**:
El código está usando solo `is_staff === true` para determinar si redirigir a admin, cuando debería verificar el **rol específico**.

---

## 🎭 Roles y Permisos del Sistema

### Backend - Permisos Definidos

```python
# users/permissions.py

class IsAdminOrManager(permissions.BasePermission):
    """
    Solo ADMIN y MANAGER pueden acceder
    """
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.role in ['ADMIN', 'MANAGER']  # ✅ CAJERO NO INCLUIDO
        )
```

### Endpoints Protegidos con IsAdminOrManager

| Endpoint | Requiere | CAJERO Acceso |
|----------|----------|---------------|
| `/api/predictions/sales/` | ADMIN o MANAGER | ❌ **403 CORRECTO** |
| `/api/orders/admin/dashboard/` | ADMIN o MANAGER | ❌ **403 CORRECTO** |
| `/api/orders/admin/` | ADMIN o MANAGER | ❌ **403 CORRECTO** |
| `/api/reports/*` | ADMIN o MANAGER | ❌ **403 CORRECTO** |
| `/api/audit/*` | ADMIN o MANAGER | ❌ **403 CORRECTO** |
| `/api/users/` (list) | ADMIN o MANAGER | ❌ **403 CORRECTO** |

---

## 📊 Jerarquía de Roles

```
ADMIN (máximo poder)
  ├── Acceso a todo
  └── Django Admin Panel

MANAGER (gestión operativa)
  ├── Dashboard /admin/dashboard
  ├── Gestión de órdenes /admin/orders
  ├── Gestión de devoluciones
  ├── Reportes y predicciones
  └── Ver usuarios

CAJERO (punto de venta) ⚠️ ROL LIMITADO
  ├── Ver productos
  ├── Crear órdenes (para clientes en tienda)
  └── Ver órdenes propias
  ❌ NO acceso a admin dashboard
  ❌ NO acceso a reportes
  ❌ NO acceso a predicciones

CUSTOMER (cliente)
  ├── Ver productos
  ├── Crear órdenes
  ├── Ver órdenes propias
  ├── Solicitar devoluciones
  └── Billetera virtual
```

---

## 🔧 Solución - Cambios en Frontend

### ❌ Código Actual (Incorrecto)

```javascript
// En login.jsx o AuthContext.jsx
if (result.user?.is_staff) {  // ❌ INCORRECTO
    console.log('✅ [LOGIN 9] Usuario es ADMIN - Redirigiendo a /admin/dashboard');
    router.push('/admin/dashboard');
} else {
    console.log('ℹ️ [LOGIN 10] Usuario regular - Redirigiendo a /products');
    router.push('/products');
}
```

**Problema**: Todos los usuarios con `is_staff=true` son tratados como admin, incluyendo CAJERO.

---

### ✅ Código Corregido (Correcto)

```javascript
// OPCIÓN 1: Verificar rol específico (RECOMENDADO)
const role = result.user?.role;
const isStaff = result.user?.is_staff;

if (role === 'ADMIN' || role === 'MANAGER') {
    console.log(`✅ [LOGIN 9] Usuario ${role} - Redirigiendo a /admin/dashboard`);
    router.push('/admin/dashboard');
} else if (role === 'CAJERO') {
    console.log('ℹ️ [LOGIN 10] Usuario CAJERO - Redirigiendo a /products');
    router.push('/products'); // O crear página específica /cajero/pos
} else {
    console.log('ℹ️ [LOGIN 11] Usuario regular - Redirigiendo a /products');
    router.push('/products');
}
```

---

### ✅ Código Alternativo (Con Dashboard Específico para Cajero)

```javascript
const role = result.user?.role;

switch(role) {
    case 'ADMIN':
    case 'MANAGER':
        console.log(`✅ Usuario ${role} - Redirigiendo a admin`);
        router.push('/admin/dashboard');
        break;
    
    case 'CAJERO':
        console.log('✅ Usuario CAJERO - Redirigiendo a punto de venta');
        router.push('/cajero/pos'); // Página específica para cajeros
        break;
    
    case 'DELIVERY':
        console.log('✅ Usuario DELIVERY - Redirigiendo a entregas');
        router.push('/delivery/orders');
        break;
    
    default:
        console.log('ℹ️ Usuario regular - Redirigiendo a productos');
        router.push('/products');
}
```

---

## 🛠️ Archivos a Modificar

### 1. **AuthContext.jsx** o donde se maneje el login

Buscar la lógica de redirección después del login exitoso:

```javascript
// Buscar algo como:
// 🔍 [LOGIN 9] Usuario es ADMIN
// if (result.user?.is_staff)

// Reemplazar con verificación de rol
```

### 2. **ProtectedRoute.jsx** (si existe)

Si hay rutas protegidas, también verificar el rol:

```javascript
// ❌ Antes
if (!user?.is_staff) {
    return <Navigate to="/products" />;
}

// ✅ Después
const allowedRoles = ['ADMIN', 'MANAGER'];
if (!allowedRoles.includes(user?.role)) {
    return <Navigate to="/products" />;
}
```

### 3. **Navbar.jsx** o **Sidebar.jsx**

Ocultar enlaces de admin para CAJERO:

```javascript
{(user?.role === 'ADMIN' || user?.role === 'MANAGER') && (
    <Link to="/admin/dashboard">Dashboard</Link>
)}

{user?.role === 'CAJERO' && (
    <Link to="/cajero/pos">Punto de Venta</Link>
)}
```

---

## 📝 Testing de la Solución

### Test 1: Login como CAJERO

```bash
# 1. Abrir frontend en navegador
https://web-2ex.vercel.app/login

# 2. Login con:
Usuario: luis_cajero
Password: luis123

# 3. Verificar:
✅ No debe redirigir a /admin/dashboard
✅ Debe redirigir a /products (o /cajero/pos si se implementó)
✅ No debe ver opciones de admin en el menú
```

### Test 2: Login como MANAGER

```bash
# 1. Login con:
Usuario: carlos_manager
Password: carlos123

# 2. Verificar:
✅ Debe redirigir a /admin/dashboard
✅ Dashboard debe cargar sin errores 403
✅ Puede acceder a reportes y predicciones
```

### Test 3: Login como ADMIN

```bash
# 1. Login con:
Usuario: admin
Password: admin123

# 2. Verificar:
✅ Debe redirigir a /admin/dashboard
✅ Acceso total a todas las funcionalidades
```

---

## 🔒 Resumen de Accesos por Rol

### CAJERO - Funcionalidades Permitidas

| Funcionalidad | Endpoint | Acceso |
|--------------|----------|--------|
| Ver productos | `/api/products/` | ✅ Permitido |
| Ver categorías | `/api/products/categories/` | ✅ Permitido |
| Crear órdenes | `/api/orders/` | ✅ Permitido |
| Ver mis órdenes | `/api/orders/my_orders/` | ✅ Permitido |
| Ver mi billetera | `/api/users/wallets/my_balance/` | ✅ Permitido |
| **Dashboard Admin** | `/api/orders/admin/dashboard/` | ❌ **403** |
| **Reportes** | `/api/reports/*` | ❌ **403** |
| **Predicciones** | `/api/predictions/*` | ❌ **403** |
| **Gestión usuarios** | `/api/users/` | ❌ **403** |
| **Auditoría** | `/api/audit/*` | ❌ **403** |

---

## 🎯 Página Sugerida para CAJERO

Si quieren dar funcionalidad específica a los cajeros, pueden crear:

### `/cajero/pos` (Punto de Venta)

```javascript
// pages/cajero/pos.jsx
import React, { useState } from 'react';
import ProductSearch from '@/components/cajero/ProductSearch';
import Cart from '@/components/cajero/Cart';
import PaymentMethods from '@/components/cajero/PaymentMethods';

export default function PuntoDeVenta() {
    const [cart, setCart] = useState([]);
    
    return (
        <div className="cajero-layout">
            <h1>🛒 Punto de Venta</h1>
            
            {/* Búsqueda y selección de productos */}
            <ProductSearch onAddToCart={(product) => setCart([...cart, product])} />
            
            {/* Carrito con productos seleccionados */}
            <Cart items={cart} onUpdateCart={setCart} />
            
            {/* Métodos de pago */}
            <PaymentMethods cart={cart} onCheckout={handleCheckout} />
        </div>
    );
}

// Características sugeridas:
// - Búsqueda rápida de productos por código o nombre
// - Agregar productos al carrito sin navegar a /products
// - Calcular total en tiempo real
// - Crear orden directamente
// - Ver órdenes del día
```

---

## ✅ Checklist de Implementación

- [ ] **1. Modificar lógica de login**
  - Archivo: `AuthContext.jsx` o `login.jsx`
  - Cambiar: `if (is_staff)` → `if (role === 'ADMIN' || role === 'MANAGER')`

- [ ] **2. Actualizar rutas protegidas**
  - Archivo: `ProtectedRoute.jsx` o similar
  - Verificar rol específico, no solo is_staff

- [ ] **3. Actualizar navegación**
  - Archivo: `Navbar.jsx` o `Sidebar.jsx`
  - Mostrar opciones según rol

- [ ] **4. Crear página para CAJERO** (opcional)
  - Crear: `/pages/cajero/pos.jsx`
  - Redirigir cajeros ahí en lugar de /products

- [ ] **5. Testing**
  - Probar login con luis_cajero
  - Verificar redirección correcta
  - Confirmar accesos permitidos/denegados

---

## 📚 Credenciales de Prueba

```bash
# ADMIN
Username: admin
Password: admin123
Esperado: Redirigir a /admin/dashboard ✅

# MANAGER
Username: carlos_manager
Password: carlos123
Esperado: Redirigir a /admin/dashboard ✅

# CAJERO
Username: luis_cajero
Password: luis123
Esperado: Redirigir a /products ✅ (o /cajero/pos si se implementa)

# CUSTOMER
Username: juan_cliente
Password: juan123
Esperado: Redirigir a /products ✅
```

---

## 🔍 Cómo Identificar el Código del Frontend

### Buscar en el código del frontend:

```bash
# Buscar logs de login
grep -r "LOGIN 9" src/
grep -r "Usuario es ADMIN" src/

# Buscar verificación de is_staff
grep -r "is_staff" src/
grep -r "user?.is_staff" src/

# Buscar redirecciones
grep -r "router.push('/admin" src/
grep -r "navigate('/admin" src/
```

### Palabras clave a buscar:

- `is_staff`
- `Usuario es ADMIN`
- `router.push('/admin/dashboard')`
- `navigate('/admin/dashboard')`
- `LOGIN 9`
- `AUTHCONTEXT`

---

## 📖 Documentación Relacionada

- **Definición de roles**: `users/models.py` → `Role.choices`
- **Permisos backend**: `users/permissions.py`
- **Credenciales completas**: `CREDENCIALES_ACCESO.txt`
- **Funcionalidades por rol**: `FUNCIONALIDADES_POR_ROL.md` (necesita actualización)

---

## ⚠️ Nota Importante

**El backend NO tiene ningún error**. Los errores 403 son el comportamiento correcto y esperado. El rol CAJERO fue diseñado para:

- ✅ Ver y vender productos en punto de venta físico
- ✅ Crear órdenes para clientes que compran en tienda
- ❌ **NO** tiene acceso administrativo
- ❌ **NO** puede ver reportes o dashboard de admin

Si necesitan dar acceso a dashboard a los cajeros, tienen 2 opciones:

1. **Cambiar el rol a MANAGER** (recomendado si necesitan acceso)
2. **Modificar IsAdminOrManager** para incluir CAJERO (NO recomendado - rompe separación de roles)

---

**Última actualización**: 12 de noviembre de 2025  
**Problema**: Error de lógica en redirección del frontend  
**Solución**: Verificar `role` en lugar de solo `is_staff`  
**Estado Backend**: ✅ Funcionando correctamente  
**Estado Frontend**: ❌ Necesita corrección en login/redirección
