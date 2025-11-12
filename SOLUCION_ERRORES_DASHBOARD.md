# 🚨 SOLUCIÓN A ERRORES DEL DASHBOARD ADMIN

**Fecha:** 11 de Noviembre, 2025  
**Errores detectados:** 5 endpoints fallando  
**Diagnóstico:** diagnose_dashboard.py

---

## ❌ ERRORES ENCONTRADOS

### 1. Wallet 404 Error
```
GET /wallet/my_wallet/ → 404
GET /wallet/ → 404
```

**Causa:** El usuario `admin` no tiene una billetera creada automáticamente.

**Solución A - Crear billetera para admin:**
```python
# En backend: seed_data.py o migration
from users.models import User
from shop_orders.models import Wallet

admin = User.objects.get(username='admin')
if not hasattr(admin, 'wallet'):
    Wallet.objects.create(user=admin, balance=0)
```

**Solución B - Frontend maneje el 404:**
```javascript
// En el frontend
async function getWallet() {
  try {
    const response = await fetch('/api/wallet/my_wallet/');
    if (response.status === 404) {
      // Usuario no tiene billetera, mostrar mensaje o crear
      console.log('Usuario sin billetera');
      return null;
    }
    return await response.json();
  } catch (error) {
    console.error('Error al obtener billetera:', error);
    return null;
  }
}
```

---

### 2. Reports 400 Error
```
GET /reports/sales/ → 400
Error: "Los parámetros 'start_date' y 'end_date' son requeridos"
```

**Causa:** Frontend llama al endpoint sin fechas obligatorias.

**Solución - Frontend debe enviar fechas:**
```javascript
// ❌ INCORRECTO:
fetch('/api/reports/sales/');

// ✅ CORRECTO:
const today = new Date();
const startDate = new Date(today.getFullYear(), 0, 1); // 1 de enero
const endDate = today;

const params = new URLSearchParams({
  start_date: startDate.toISOString().split('T')[0],  // YYYY-MM-DD
  end_date: endDate.toISOString().split('T')[0]       // YYYY-MM-DD
});

fetch(`/api/reports/sales/preview/?${params}`);
```

---

### 3. Endpoints Incorrectos (404)
```
GET /dashboard/ → 404
GET /stats/ → 404
```

**Causa:** Frontend usa URLs incorrectas.

**Solución - Usar endpoints correctos:**
```javascript
// ❌ INCORRECTO:
fetch('/api/dashboard/');
fetch('/api/stats/');

// ✅ CORRECTO:
fetch('/api/orders/admin/dashboard/');  // Dashboard de órdenes
fetch('/api/predictions/sales/');        // Estadísticas/predicciones
```

---

## 🔧 SCRIPT DE CORRECCIÓN PARA BACKEND

Ejecuta esto para crear billeteras faltantes:

```python
# create_missing_wallets.py
from django.core.management.base import BaseCommand
from users.models import User
from shop_orders.models import Wallet

def create_wallets():
    """Crea billeteras para usuarios que no tienen"""
    users_without_wallet = User.objects.filter(wallet__isnull=True)
    
    created = 0
    for user in users_without_wallet:
        Wallet.objects.create(user=user, balance=0)
        created += 1
        print(f"✅ Billetera creada para {user.username}")
    
    print(f"\n✅ Total billeteras creadas: {created}")

if __name__ == '__main__':
    create_wallets()
```

**Ejecutar:**
```bash
python create_missing_wallets.py
```

---

## 🎯 CORRECCIONES EN FRONTEND

### Archivo: `src/services/api.js` o similar

```javascript
// Configuración correcta de endpoints
const API_ENDPOINTS = {
  // Dashboard
  dashboard: '/orders/admin/dashboard/',  // ❌ NO: '/dashboard/'
  
  // Wallet
  wallet: '/wallet/my_wallet/',           // ❌ NO: '/wallet/'
  
  // Reports (requieren fechas)
  salesReport: (startDate, endDate) => 
    `/reports/sales/preview/?start_date=${startDate}&end_date=${endDate}`,
  
  // Estadísticas
  predictions: '/predictions/sales/',     // ❌ NO: '/stats/'
};

// Función helper para fechas
function getDefaultDateRange() {
  const today = new Date();
  const startOfYear = new Date(today.getFullYear(), 0, 1);
  return {
    start_date: startOfYear.toISOString().split('T')[0],
    end_date: today.toISOString().split('T')[0]
  };
}

// Uso en componentes
async function loadDashboard() {
  try {
    // Dashboard de órdenes
    const dashboard = await fetch(API_BASE + API_ENDPOINTS.dashboard);
    
    // Wallet (manejar 404)
    let wallet = null;
    try {
      const walletResponse = await fetch(API_BASE + API_ENDPOINTS.wallet);
      if (walletResponse.ok) {
        wallet = await walletResponse.json();
      }
    } catch (e) {
      console.log('Usuario sin billetera');
    }
    
    // Reports con fechas
    const dates = getDefaultDateRange();
    const salesReport = await fetch(
      API_BASE + API_ENDPOINTS.salesReport(dates.start_date, dates.end_date)
    );
    
    return { dashboard, wallet, salesReport };
    
  } catch (error) {
    console.error('Error loading dashboard:', error);
    // Manejar error en UI
  }
}
```

---

## 🛡️ MANEJO DE ERRORES MEJORADO

```javascript
// Wrapper para todas las llamadas API
async function apiCall(url, options = {}) {
  try {
    const response = await fetch(API_BASE + url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    
    // Manejar errores HTTP
    if (!response.ok) {
      if (response.status === 404) {
        console.warn(`⚠️ Recurso no encontrado: ${url}`);
        return null;
      }
      
      if (response.status === 400) {
        const error = await response.json();
        console.error(`❌ Error 400: ${error.error || 'Bad Request'}`);
        throw new Error(error.error || 'Bad Request');
      }
      
      if (response.status === 401) {
        console.error('❌ No autorizado - refrescar login');
        // Redirigir a login
        window.location.href = '/login';
        return null;
      }
      
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
    
  } catch (error) {
    console.error(`❌ API Error (${url}):`, error);
    // NO hacer throw - retornar null para que la app no crashee
    return null;
  }
}

// Uso:
const dashboard = await apiCall('/orders/admin/dashboard/');
if (dashboard) {
  // Procesar datos
} else {
  // Mostrar mensaje de error en UI
}
```

---

## ✅ CHECKLIST DE CORRECCIÓN

### Backend:
- [ ] Ejecutar `create_missing_wallets.py`
- [ ] Verificar que admin tenga billetera
- [ ] Confirmar seed_data.py crea billeteras para todos los usuarios

### Frontend:
- [ ] Cambiar `/dashboard/` → `/orders/admin/dashboard/`
- [ ] Cambiar `/stats/` → `/predictions/sales/`
- [ ] Cambiar `/wallet/` → `/wallet/my_wallet/`
- [ ] Agregar fechas a `/reports/sales/` y `/reports/products/`
- [ ] Implementar manejo de errores con try/catch
- [ ] Implementar fallbacks para 404 (especialmente wallet)

### Testing:
- [ ] Abrir DevTools > Network
- [ ] Verificar que no haya requests en rojo (failed)
- [ ] Verificar que no haya "Uncaught (in promise)" en console
- [ ] Probar dashboard con diferentes usuarios (admin, manager, cajero)

---

## 🚀 ORDEN DE IMPLEMENTACIÓN

1. **Backend primero** (5 min):
   ```bash
   cd backend_2ex
   python create_missing_wallets.py
   ```

2. **Frontend - Endpoints** (10 min):
   - Actualizar configuración de URLs
   - Agregar helper de fechas

3. **Frontend - Manejo de errores** (15 min):
   - Implementar wrapper de API
   - Agregar try/catch en componentes
   - Agregar fallbacks para 404

4. **Validar** (5 min):
   - Recargar dashboard
   - Verificar console sin errores
   - Verificar Network tab sin requests fallidos

---

## 📊 RESULTADO ESPERADO

Después de implementar las correcciones:

```
✅ Dashboard carga sin errores
✅ No hay "Uncaught (in promise)" en console
✅ Wallet aparece o muestra mensaje apropiado
✅ Reports se cargan con fechas correctas
✅ Todas las requests en Network tab con status 200
```

---

## 🎯 COMMIT SUGERIDO

```bash
git add .
git commit -m "fix: Corregir endpoints dashboard (wallet 404, reports 400, URLs incorrectas)"
git push origin main
```
