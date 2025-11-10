# 🚨 09. ERRORES COMUNES Y SOLUCIONES

## 📝 Descripción

Esta sección documenta los **errores más comunes** que puedes encontrar al integrar el frontend con el backend y **cómo solucionarlos**.

---

## 🔐 ERRORES DE AUTENTICACIÓN

### ❌ Error 401: "Las credenciales de autenticación no se proveyeron"

**Causas:**
1. No se envió el token en el header
2. Token inválido o expirado
3. Formato incorrecto del header

**Soluciones:**

```javascript
// ❌ MAL - Sin token
fetch('http://localhost:8000/api/deliveries/returns/');

// ❌ MAL - Formato incorrecto
fetch('http://localhost:8000/api/deliveries/returns/', {
  headers: {
    'Authorization': token  // Falta "Bearer "
  }
});

// ✅ BIEN - Token correcto
fetch('http://localhost:8000/api/deliveries/returns/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});

// ✅ MEJOR - Con interceptor de Axios
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api'
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

### ❌ Error: Token Expirado

**Síntoma:** Requests funcionaban pero ahora devuelven 401

**Solución:** Implementar refresh token automático

```javascript
const refreshAccessToken = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  
  const response = await fetch('http://localhost:8000/api/users/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: refreshToken })
  });

  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    return data.access;
  } else {
    // Refresh token también expiró
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
    return null;
  }
};

// Interceptor para auto-renovar token
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const newToken = await refreshAccessToken();
      
      if (newToken) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      }
    }

    return Promise.reject(error);
  }
);
```

---

## 🚫 ERRORES DE PERMISOS

### ❌ Error 403: "No tienes permiso para realizar esta acción"

**Causas:**
1. Usuario con rol incorrecto
2. Intentando acceder a recurso de otro usuario
3. Intentando hacer acción sin los permisos necesarios

**Soluciones:**

```javascript
// ❌ Cliente intentando aprobar devolución
const user = { role: 'CLIENTE' };
approveReturn();  // 403 Forbidden

// ✅ Verificar rol antes de mostrar botón
const ApproveButton = () => {
  const { user } = useAuth();

  if (!['MANAGER', 'ADMIN'].includes(user.role)) {
    return null;  // No mostrar botón
  }

  return <button onClick={approveReturn}>✅ Aprobar</button>;
};

// ✅ Verificar permisos en el componente
const ManagerPanel = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!['MANAGER', 'ADMIN'].includes(user.role)) {
      alert('No tienes acceso a esta sección');
      navigate('/');
    }
  }, [user]);

  return <div>Panel de Manager</div>;
};
```

---

## 📦 ERRORES AL SOLICITAR DEVOLUCIÓN

### ❌ Error 400: "La orden debe estar en estado DELIVERED"

**Causa:** Intentando devolver orden que no está entregada

**Solución:**

```javascript
// ✅ Validar antes de mostrar formulario
const canRequestReturn = (order) => {
  if (order.status !== 'DELIVERED') {
    return {
      allowed: false,
      message: 'La orden debe estar entregada'
    };
  }
  return { allowed: true };
};

// Componente:
const ReturnButton = ({ order }) => {
  const validation = canRequestReturn(order);

  if (!validation.allowed) {
    return (
      <button disabled title={validation.message}>
        ⚠️ No disponible
      </button>
    );
  }

  return <button onClick={() => requestReturn(order)}>↩️ Devolver</button>;
};
```

---

### ❌ Error 400: "Han pasado más de 30 días desde la entrega"

**Causa:** Intentando devolver después del plazo

**Solución:**

```javascript
const isWithin30Days = (order) => {
  const deliveryDate = new Date(order.updated_at);
  const now = new Date();
  const daysSince = (now - deliveryDate) / (1000 * 60 * 60 * 24);
  
  return daysSince <= 30;
};

// Componente con indicador visual:
const ReturnDeadline = ({ order }) => {
  const deliveryDate = new Date(order.updated_at);
  const now = new Date();
  const daysSince = Math.floor((now - deliveryDate) / (1000 * 60 * 60 * 24));
  const daysRemaining = 30 - daysSince;

  if (daysSince > 30) {
    return (
      <div className="deadline-expired">
        ❌ Plazo expirado (hace {daysSince - 30} días)
      </div>
    );
  }

  return (
    <div className={`deadline ${daysRemaining <= 5 ? 'urgent' : ''}`}>
      ⏰ {daysRemaining} días restantes
    </div>
  );
};
```

---

### ❌ Error 400: "Ya existe una devolución para este producto"

**Causa:** Intentando crear segunda devolución del mismo producto

**Solución:**

```javascript
const checkExistingReturn = async (orderId, productId) => {
  const response = await fetch(
    'http://localhost:8000/api/deliveries/returns/',
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );

  const data = await response.json();
  
  const existingReturn = data.results.find(ret => 
    ret.order_details.id === orderId && 
    ret.product_details.id === productId
  );

  return existingReturn;
};

// Uso:
const ReturnButton = ({ order, product }) => {
  const [existingReturn, setExistingReturn] = useState(null);

  useEffect(() => {
    checkExistingReturn(order.id, product.id).then(setExistingReturn);
  }, [order.id, product.id]);

  if (existingReturn) {
    return (
      <div className="already-returned">
        ✅ Ya solicitaste devolución
        <Link to={`/returns/${existingReturn.id}`}>Ver devolución</Link>
      </div>
    );
  }

  return <button onClick={requestReturn}>↩️ Solicitar Devolución</button>;
};
```

---

### ❌ Error 400: "La razón debe tener al menos 10 caracteres"

**Causa:** Razón demasiado corta

**Solución:**

```javascript
const [reason, setReason] = useState('');
const [error, setError] = useState('');

const validateReason = (text) => {
  if (text.length < 10) {
    setError('La razón debe tener al menos 10 caracteres');
    return false;
  }
  if (text.length > 500) {
    setError('La razón no puede exceder 500 caracteres');
    return false;
  }
  setError('');
  return true;
};

const handleSubmit = async (e) => {
  e.preventDefault();

  if (!validateReason(reason)) {
    return;  // No enviar si no es válido
  }

  // Enviar solicitud...
};

// Componente:
<textarea
  value={reason}
  onChange={(e) => {
    setReason(e.target.value);
    validateReason(e.target.value);
  }}
  minLength={10}
  maxLength={500}
/>
<div className="char-count">
  {reason.length} / 500
  {reason.length < 10 && (
    <span className="error"> (mínimo 10)</span>
  )}
</div>
{error && <span className="error-message">{error}</span>}
```

---

## 💰 ERRORES DE BILLETERA

### ❌ Error 404: "No tienes una billetera activa"

**Causa:** Cliente no tiene billetera aún (se crea al aprobar primera devolución)

**Solución:**

```javascript
const WalletBalance = () => {
  const [wallet, setWallet] = useState(null);
  const [hasWallet, setHasWallet] = useState(false);

  useEffect(() => {
    loadWallet();
  }, []);

  const loadWallet = async () => {
    const response = await fetch(
      'http://localhost:8000/api/users/wallets/my_balance/',
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    );

    if (response.status === 404) {
      setHasWallet(false);
    } else {
      const data = await response.json();
      setWallet(data);
      setHasWallet(true);
    }
  };

  if (!hasWallet) {
    return (
      <div className="no-wallet">
        <p>💰 Aún no tienes billetera</p>
        <p>Se creará automáticamente cuando aprueban tu primera devolución</p>
      </div>
    );
  }

  return (
    <div className="wallet-balance">
      Saldo: ${wallet.balance}
    </div>
  );
};
```

---

## 🔄 ERRORES DE ESTADO

### ❌ Error 400: "Solo puedes enviar a evaluación devoluciones en estado REQUESTED"

**Causa:** Intentando cambiar estado desde un estado incorrecto

**Solución:**

```javascript
const ReturnActions = ({ returnData }) => {
  const [return, setReturn] = useState(returnData);

  const sendToEvaluation = async () => {
    // Verificar estado antes de enviar
    if (return.status !== 'REQUESTED') {
      alert('Solo puedes enviar a evaluación devoluciones solicitadas');
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/api/deliveries/returns/${return.id}/send_to_evaluation/`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.ok) {
        const updated = await response.json();
        setReturn(updated);
        alert('✅ Enviado a evaluación');
      } else {
        const error = await response.json();
        alert(`❌ ${error.error}`);
      }
    } catch (error) {
      alert('Error al procesar solicitud');
    }
  };

  // Solo mostrar botón si el estado es correcto
  return (
    <div>
      {return.status === 'REQUESTED' && (
        <button onClick={sendToEvaluation}>
          📦 Enviar a Evaluación
        </button>
      )}

      {return.status === 'IN_EVALUATION' && (
        <>
          <button onClick={approve}>✅ Aprobar</button>
          <button onClick={reject}>❌ Rechazar</button>
        </>
      )}

      {['APPROVED', 'REJECTED'].includes(return.status) && (
        <div className="final-status">
          Estado final: {return.status_display}
        </div>
      )}
    </div>
  );
};
```

---

## 🌐 ERRORES DE CORS

### ❌ Error: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Causa:** Frontend corriendo en puerto diferente al backend

**Solución en Backend (settings.py):**

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React
    "http://localhost:5173",  # Vite
    "http://localhost:8080",  # Vue
]

# O permitir todos (SOLO DESARROLLO):
CORS_ALLOW_ALL_ORIGINS = True
```

**Solución Temporal (Frontend):**

```javascript
// Si usas proxy en package.json (React)
{
  "proxy": "http://localhost:8000"
}

// Luego usar rutas relativas:
fetch('/api/deliveries/returns/');  // En lugar de http://localhost:8000/api/...
```

---

## 📡 ERRORES DE CONEXIÓN

### ❌ Error: "NetworkError" o "Failed to fetch"

**Causas:**
1. Backend no está corriendo
2. URL incorrecta
3. Firewall bloqueando conexión

**Soluciones:**

```javascript
// 1. Verificar que backend está corriendo:
// En terminal: python manage.py runserver

// 2. Probar URL directamente en navegador:
// http://localhost:8000/api/deliveries/returns/

// 3. Agregar timeout y retry:
const fetchWithRetry = async (url, options, retries = 3) => {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url, options);
      return response;
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
};

// 4. Agregar indicador de loading:
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);

const loadReturns = async () => {
  setLoading(true);
  setError(null);

  try {
    const response = await fetchWithRetry(
      'http://localhost:8000/api/deliveries/returns/',
      { headers: { 'Authorization': `Bearer ${token}` } }
    );
    
    const data = await response.json();
    setReturns(data.results);
  } catch (error) {
    setError('No se pudo conectar al servidor. Verifica que esté corriendo.');
  } finally {
    setLoading(false);
  }
};
```

---

## 📝 ERRORES DE DATOS

### ❌ Error: "Cannot read property 'name' of null"

**Causa:** Intentando acceder a propiedad de objeto null/undefined

**Solución:**

```javascript
// ❌ MAL - Sin verificación
const ProductName = ({ return }) => {
  return <h3>{return.product_details.name}</h3>;
  // Error si product_details es null
};

// ✅ BIEN - Con optional chaining
const ProductName = ({ return }) => {
  return <h3>{return.product_details?.name || 'Sin nombre'}</h3>;
};

// ✅ MEJOR - Con verificación completa
const ProductName = ({ return }) => {
  if (!return) return null;
  if (!return.product_details) return <span>Producto no disponible</span>;
  
  return <h3>{return.product_details.name}</h3>;
};
```

---

## 🎨 ERRORES DE UI

### ❌ Problema: Estados no se actualizan en tiempo real

**Causa:** No hay polling ni websockets implementados

**Solución:**

```javascript
// Opción 1: Polling (actualizar cada X segundos)
const MyReturns = () => {
  const [returns, setReturns] = useState([]);

  useEffect(() => {
    loadReturns();

    // Actualizar cada 30 segundos
    const interval = setInterval(loadReturns, 30000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      {returns.map(ret => <ReturnCard key={ret.id} return={ret} />)}
      <button onClick={loadReturns}>🔄 Refrescar</button>
    </div>
  );
};

// Opción 2: Actualizar después de acción
const approveReturn = async (id) => {
  const response = await fetch(
    `http://localhost:8000/api/deliveries/returns/${id}/approve/`,
    { method: 'POST', ... }
  );

  if (response.ok) {
    // Recargar lista después de aprobar
    await loadReturns();
  }
};
```

---

## 🔍 DEBUG Y TROUBLESHOOTING

### Herramienta: Console Logs Estratégicos

```javascript
const createReturn = async (data) => {
  console.log('📤 Enviando solicitud de devolución:', data);

  try {
    const response = await fetch('http://localhost:8000/api/deliveries/returns/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    console.log('📥 Response status:', response.status);

    if (!response.ok) {
      const error = await response.json();
      console.error('❌ Error del servidor:', error);
      throw error;
    }

    const result = await response.json();
    console.log('✅ Devolución creada:', result);
    return result;
  } catch (error) {
    console.error('❌ Error al crear devolución:', error);
    throw error;
  }
};
```

---

### Herramienta: Componente de Debug

```jsx
const DebugPanel = ({ data }) => {
  if (process.env.NODE_ENV !== 'development') return null;

  return (
    <div className="debug-panel">
      <h4>🐛 Debug Info</h4>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
};

// Uso:
<DebugPanel data={{ user, returns, wallet }} />
```

---

### Herramienta: Error Boundary

```jsx
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error capturado:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>⚠️ Algo salió mal</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>
            Recargar página
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Uso:
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

---

## 📋 CHECKLIST DE PROBLEMAS COMUNES

Cuando algo no funciona, verifica:

- [ ] ✅ Backend está corriendo (`python manage.py runserver`)
- [ ] ✅ Token está presente en localStorage
- [ ] ✅ Token no ha expirado
- [ ] ✅ URL del endpoint es correcta
- [ ] ✅ Método HTTP es correcto (GET/POST/PUT/DELETE)
- [ ] ✅ Headers incluyen `Authorization` y `Content-Type`
- [ ] ✅ Body está en formato JSON correcto
- [ ] ✅ Usuario tiene los permisos necesarios
- [ ] ✅ Validaciones de negocio se cumplen
- [ ] ✅ CORS está configurado en backend
- [ ] ✅ No hay errores en consola del navegador
- [ ] ✅ No hay errores en consola del backend

---

## 🆘 Recursos Adicionales

### Verificar Estado del Backend:

```bash
# En PowerShell:
curl http://localhost:8000/api/deliveries/returns/ -H "Authorization: Bearer YOUR_TOKEN"

# O en navegador (para GET):
http://localhost:8000/api/deliveries/returns/
```

### Ver Logs del Backend:

```bash
# Los logs aparecen en la terminal donde corriste:
python manage.py runserver

# Buscar líneas con errores:
[ERROR] ...
Traceback ...
```

---

**¡Documentación completa!** 🎉

Vuelve al índice: `00_INDICE.md`
