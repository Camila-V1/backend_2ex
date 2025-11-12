# 🔧 SOLUCIÓN: Peticiones Duplicadas al Endpoint de Balance

## 🚨 Problema Detectado

El frontend está haciendo **12+ peticiones consecutivas** al endpoint `/users/wallets/my_balance/` en la misma página, causando:
- Sobrecarga del servidor
- Consumo innecesario de recursos
- Lentitud en la aplicación

## ✅ Solución: Hook Personalizado con Caché

### 1. Crear Hook `useBalance.js`

```javascript
// src/hooks/useBalance.js
import { useState, useEffect, useCallback, useRef } from 'react';
import api from '../api/axios';

// Caché global para compartir entre componentes
let balanceCache = null;
let cacheTimestamp = null;
const CACHE_DURATION = 30000; // 30 segundos

const useBalance = (autoFetch = true) => {
  const [balance, setBalance] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fetchingRef = useRef(false);

  const fetchBalance = useCallback(async (forceRefresh = false) => {
    // Evitar peticiones duplicadas simultáneas
    if (fetchingRef.current && !forceRefresh) {
      console.log('⏸️ [BALANCE] Petición ya en curso, evitando duplicado');
      return balanceCache;
    }

    // Usar caché si está disponible y es reciente
    if (!forceRefresh && balanceCache && cacheTimestamp) {
      const cacheAge = Date.now() - cacheTimestamp;
      if (cacheAge < CACHE_DURATION) {
        console.log(`✅ [BALANCE] Usando caché (${Math.round(cacheAge / 1000)}s)`);
        setBalance(balanceCache);
        return balanceCache;
      }
    }

    fetchingRef.current = true;
    setLoading(true);
    setError(null);

    try {
      console.log('🔄 [BALANCE] Obteniendo balance del servidor...');
      const response = await api.get('/users/wallets/my_balance/');
      
      // Actualizar caché global
      balanceCache = response.data;
      cacheTimestamp = Date.now();
      
      setBalance(response.data);
      console.log('✅ [BALANCE] Balance actualizado:', response.data.balance);
      return response.data;
    } catch (err) {
      console.error('❌ [BALANCE] Error al obtener balance:', err);
      setError(err);
      return null;
    } finally {
      setLoading(false);
      fetchingRef.current = false;
    }
  }, []);

  // Auto-fetch al montar (si autoFetch=true)
  useEffect(() => {
    if (autoFetch) {
      fetchBalance();
    }
  }, [autoFetch, fetchBalance]);

  // Función para invalidar caché
  const invalidateCache = useCallback(() => {
    console.log('🗑️ [BALANCE] Invalidando caché');
    balanceCache = null;
    cacheTimestamp = null;
  }, []);

  return {
    balance: balance?.balance || '0.00',
    walletId: balance?.wallet_id,
    isActive: balance?.is_active,
    loading,
    error,
    refetch: () => fetchBalance(true),
    invalidateCache,
  };
};

export default useBalance;
```

### 2. Actualizar el Header (Balance visible)

```javascript
// src/components/Header.jsx
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import useBalance from '../hooks/useBalance';

function Header() {
  const { balance, loading, refetch } = useBalance(); // ✅ Una sola instancia
  const navigate = useNavigate();

  return (
    <header className="header">
      <nav className="navbar">
        <Link to="/" className="logo">🛒 E-Commerce</Link>
        
        <div className="nav-links">
          <Link to="/products">Productos</Link>
          <Link to="/orders">Mis Órdenes</Link>
          
          {/* Balance con botón de refresh */}
          <div className="balance-display">
            <span>💰 Saldo: ${loading ? '...' : balance}</span>
            <button 
              onClick={refetch} 
              className="refresh-btn"
              title="Actualizar balance"
            >
              🔄
            </button>
          </div>
          
          <Link to="/cart">🛒 Carrito</Link>
          <button onClick={() => {
            localStorage.clear();
            navigate('/login');
          }}>
            Cerrar Sesión
          </button>
        </div>
      </nav>
    </header>
  );
}

export default Header;
```

### 3. NO hacer fetch del balance en cada componente hijo

**❌ ANTES (Mal - causa duplicados):**
```javascript
// En ProductCard, ProductList, etc.
function ProductCard() {
  const [balance, setBalance] = useState(null);
  
  useEffect(() => {
    // ❌ Cada componente hace su propia petición
    api.get('/users/wallets/my_balance/').then(res => setBalance(res.data));
  }, []);
  
  return <div>...</div>;
}
```

**✅ DESPUÉS (Bien - usa caché compartido):**
```javascript
// Solo el Header hace el fetch, otros componentes usan caché
function ProductCard() {
  const { balance } = useBalance(false); // autoFetch=false, usa caché
  
  // No hace petición, solo lee el caché compartido
  return <div>...</div>;
}
```

### 4. Invalidar caché después de compras

```javascript
// src/pages/Checkout.jsx
import useBalance from '../hooks/useBalance';

function Checkout() {
  const { refetch, invalidateCache } = useBalance(false);
  
  const handlePayment = async () => {
    try {
      // Procesar pago
      await api.post('/orders/create/', orderData);
      
      // ✅ Invalidar caché y refrescar
      invalidateCache();
      await refetch();
      
      toast.success('Compra exitosa');
    } catch (error) {
      toast.error('Error en el pago');
    }
  };
  
  return <button onClick={handlePayment}>Pagar</button>;
}
```

---

## 📊 Resultados Esperados

### Antes (❌):
```
🔷 [AXIOS REQUEST] users/wallets/my_balance/
🔷 [AXIOS REQUEST] users/wallets/my_balance/
🔷 [AXIOS REQUEST] users/wallets/my_balance/
... (12+ peticiones)
```

### Después (✅):
```
🔄 [BALANCE] Obteniendo balance del servidor...
✅ [BALANCE] Balance actualizado: 0.00
✅ [BALANCE] Usando caché (3s)
✅ [BALANCE] Usando caché (5s)
```

---

## 🎯 Mejoras Adicionales (Opcional)

### Opción A: Context API para Balance Global

```javascript
// src/context/BalanceContext.jsx
import React, { createContext, useContext } from 'react';
import useBalance from '../hooks/useBalance';

const BalanceContext = createContext();

export const BalanceProvider = ({ children }) => {
  const balanceData = useBalance(true); // Solo fetch aquí
  
  return (
    <BalanceContext.Provider value={balanceData}>
      {children}
    </BalanceContext.Provider>
  );
};

export const useBalanceContext = () => useContext(BalanceContext);

// App.jsx
import { BalanceProvider } from './context/BalanceContext';

function App() {
  return (
    <BalanceProvider>
      <Router>
        {/* rutas */}
      </Router>
    </BalanceProvider>
  );
}
```

### Opción B: React Query (Recomendado para apps grandes)

```bash
npm install @tanstack/react-query
```

```javascript
// src/hooks/useBalance.js
import { useQuery } from '@tanstack/react-query';
import api from '../api/axios';

const useBalance = () => {
  return useQuery({
    queryKey: ['balance'],
    queryFn: async () => {
      const { data } = await api.get('/users/wallets/my_balance/');
      return data;
    },
    staleTime: 30000, // 30 segundos
    cacheTime: 300000, // 5 minutos
    refetchOnWindowFocus: false,
  });
};

export default useBalance;
```

---

## 🔍 Verificación

Después de implementar, verifica en la consola:

```javascript
// Debe ver SOLO 1 petición inicial
✅ [AXIOS RESPONSE] Status: 200 - users/wallets/my_balance/

// Luego, solo mensajes de caché
✅ [BALANCE] Usando caché (5s)
✅ [BALANCE] Usando caché (10s)
```

---

## 📝 Checklist de Implementación

- [ ] Crear `src/hooks/useBalance.js` con caché
- [ ] Actualizar Header para usar el hook
- [ ] Remover llamadas a `/my_balance/` de otros componentes
- [ ] Agregar `refetch()` después de compras
- [ ] Verificar en consola que solo hay 1 petición inicial
- [ ] (Opcional) Implementar Context API o React Query

---

**Resultado Final:** De 12+ peticiones → 1 petición cada 30 segundos ✅
