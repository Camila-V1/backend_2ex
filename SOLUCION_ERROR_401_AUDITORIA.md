# 🔧 Solución: Error 401 en Sistema de Auditoría

## 🎯 Diagnóstico

**Problema:** Frontend muestra error 401 (Unauthorized) al intentar acceder a `/api/audit/`

**Causa raíz:** El token JWT no se está guardando correctamente en `localStorage` después del login, o no se está enviando en las peticiones.

**Estado del Backend:** ✅ **Funcionando perfectamente**
- Login retorna tokens correctos
- Endpoints de auditoría responden con 200
- Paginación configurada correctamente
- Hay 3 logs registrados en la base de datos

---

## ✅ Verificación del Backend

Test ejecutado con éxito:

```bash
python test_token_audit.py
```

**Resultados:**
- ✅ Login: 200 OK
- ✅ `/api/audit/`: 200 OK (3 logs encontrados)
- ✅ `/api/audit/stats/`: 200 OK
- ✅ Token válido generado correctamente

---

## 🔧 Solución: Modificaciones en el Frontend

### 1️⃣ Verificar que el token se guarda después del login

En tu componente de **Login** (ej: `Login.jsx`), después de un login exitoso:

```javascript
// ❌ INCORRECTO - Si está faltando esto:
const handleLogin = async (e) => {
  e.preventDefault();
  
  const response = await fetch('http://localhost:8000/api/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  if (response.ok) {
    const data = await response.json();
    // ⚠️ FALTA GUARDAR EL TOKEN
    navigate('/dashboard');
  }
};

// ✅ CORRECTO - Guardar token en localStorage:
const handleLogin = async (e) => {
  e.preventDefault();
  
  const response = await fetch('http://localhost:8000/api/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  if (response.ok) {
    const data = await response.json();
    
    // ✅ GUARDAR TOKENS
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    
    // ✅ OPCIONAL: Guardar info del usuario
    localStorage.setItem('user', JSON.stringify({
      username: data.username,
      role: data.role,
      is_staff: data.is_staff
    }));
    
    navigate('/dashboard');
  }
};
```

---

### 2️⃣ Verificar que AdminAudit.jsx envía el token correctamente

En tu archivo `AdminAudit.jsx`, línea 77 aproximadamente:

```javascript
// ❌ PROBLEMA COMÚN: Token no se carga correctamente
const fetchLogs = async () => {
  const token = localStorage.getItem('access_token'); // ← Podría ser null
  
  console.log('🔍 Token:', token); // ← AGREGAR ESTE LOG
  
  if (!token) {
    console.error('❌ No hay token en localStorage');
    return;
  }
  
  const response = await fetch(`${API_URL}/audit/?${params.toString()}`, {
    headers: {
      'Authorization': `Bearer ${token}`, // ← Debe incluir "Bearer "
      'Content-Type': 'application/json'
    }
  });
  
  // ... resto del código
};
```

**Verifica esto en la consola del navegador:**

```javascript
// Abre la consola (F12) y ejecuta:
console.log('Token:', localStorage.getItem('access_token'));

// ❌ Si retorna null → El problema es el login
// ✅ Si retorna el token → El problema es cómo se envía
```

---

### 3️⃣ Crear un servicio de autenticación centralizado

Crea un archivo `src/services/authService.js`:

```javascript
// src/services/authService.js

const API_URL = 'http://localhost:8000';

class AuthService {
  // Login
  async login(username, password) {
    const response = await fetch(`${API_URL}/api/token/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    if (!response.ok) {
      throw new Error('Login fallido');
    }

    const data = await response.json();
    
    // Guardar tokens
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    
    return data;
  }

  // Logout
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  // Obtener token
  getToken() {
    return localStorage.getItem('access_token');
  }

  // Verificar si está autenticado
  isAuthenticated() {
    return !!this.getToken();
  }

  // Obtener headers con autorización
  getAuthHeaders() {
    const token = this.getToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    };
  }

  // Refresh token
  async refreshToken() {
    const refresh = localStorage.getItem('refresh_token');
    
    if (!refresh) {
      throw new Error('No refresh token');
    }

    const response = await fetch(`${API_URL}/api/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh })
    });

    if (!response.ok) {
      this.logout();
      throw new Error('Token expirado');
    }

    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    
    return data.access;
  }
}

export default new AuthService();
```

---

### 4️⃣ Usar el servicio en AdminAudit.jsx

```javascript
// AdminAudit.jsx
import authService from '../services/authService';

const AdminAudit = () => {
  // ... otros estados

  const fetchLogs = async () => {
    try {
      // ✅ Usar el servicio de autenticación
      if (!authService.isAuthenticated()) {
        console.error('❌ Usuario no autenticado');
        navigate('/login');
        return;
      }

      const response = await fetch(
        `${API_URL}/audit/?${params.toString()}`,
        {
          headers: authService.getAuthHeaders() // ✅ Headers con token
        }
      );

      if (response.status === 401) {
        // Token expirado, intentar refresh
        console.log('⚠️ Token expirado, renovando...');
        try {
          await authService.refreshToken();
          // Reintentar la petición
          return fetchLogs();
        } catch (error) {
          console.error('❌ No se pudo renovar token');
          authService.logout();
          navigate('/login');
          return;
        }
      }

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('🔷 [AUDIT] Response completa:', data);
      
      setLogs(data.results || []);
      setTotalLogs(data.count || 0);
      
    } catch (error) {
      console.error('Error fetching logs:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // ... resto del código
};
```

---

### 5️⃣ Actualizar el componente de Login

```javascript
// Login.jsx
import authService from '../services/authService';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    try {
      // ✅ Usar el servicio de autenticación
      const data = await authService.login(username, password);
      
      console.log('✅ Login exitoso:', data);
      
      // Verificar que el token se guardó
      const savedToken = authService.getToken();
      console.log('✅ Token guardado:', savedToken ? 'Sí' : 'No');
      
      // Redirigir al dashboard
      navigate('/dashboard');
      
    } catch (error) {
      console.error('❌ Error en login:', error);
      setError('Usuario o contraseña incorrectos');
    }
  };

  return (
    <form onSubmit={handleLogin}>
      {error && <div className="error">{error}</div>}
      
      <input
        type="text"
        placeholder="Usuario"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        required
      />
      
      <input
        type="password"
        placeholder="Contraseña"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      
      <button type="submit">Iniciar Sesión</button>
    </form>
  );
};

export default Login;
```

---

## 🧪 Verificación Manual en el Navegador

### 1. Abre la consola del navegador (F12)

### 2. Después de hacer login, ejecuta:

```javascript
// Verificar que el token está guardado
console.log('Token:', localStorage.getItem('access_token'));

// Debería mostrar algo como:
// Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. Si el token está guardado, prueba manualmente:

```javascript
const token = localStorage.getItem('access_token');

fetch('http://localhost:8000/api/audit/?page=1', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
  .then(res => res.json())
  .then(data => console.log('✅ Respuesta:', data))
  .catch(err => console.error('❌ Error:', err));
```

**Resultado esperado:**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 3,
      "action": "LOGIN",
      "username": "Anónimo",
      "timestamp": "2025-10-26T18:14:12.342981Z",
      // ... más campos
    },
    // ... más logs
  ]
}
```

---

## 🔍 Debugging: Pasos para identificar el problema

### Paso 1: Verificar que el login funciona

```javascript
// En Login.jsx, agregar logs:
const handleLogin = async (e) => {
  e.preventDefault();
  
  console.log('1️⃣ Intentando login...');
  
  const response = await fetch('http://localhost:8000/api/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  console.log('2️⃣ Response status:', response.status);
  
  const data = await response.json();
  console.log('3️⃣ Response data:', data);
  
  localStorage.setItem('access_token', data.access);
  console.log('4️⃣ Token guardado:', localStorage.getItem('access_token'));
  
  navigate('/dashboard');
};
```

### Paso 2: Verificar que AdminAudit usa el token

```javascript
// En AdminAudit.jsx, línea ~77:
const fetchLogs = async () => {
  const token = localStorage.getItem('access_token');
  
  console.log('🔍 [DEBUG] Token:', token ? 'Existe' : 'NO EXISTE');
  console.log('🔍 [DEBUG] Token length:', token ? token.length : 0);
  
  if (!token) {
    console.error('❌ No hay token, redirigiendo a login...');
    navigate('/login');
    return;
  }
  
  const url = `${API_URL}/audit/?${params.toString()}`;
  console.log('🔍 [DEBUG] URL:', url);
  
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
  console.log('🔍 [DEBUG] Headers:', headers);
  
  const response = await fetch(url, { headers });
  console.log('🔍 [DEBUG] Response status:', response.status);
  
  // ... resto del código
};
```

---

## 📝 Checklist de Verificación

Marca cada item después de verificarlo:

- [ ] **Login guarda el token en localStorage**
  ```javascript
  localStorage.setItem('access_token', data.access);
  ```

- [ ] **Token se puede leer en AdminAudit**
  ```javascript
  const token = localStorage.getItem('access_token');
  console.log('Token:', token); // ← Debe existir
  ```

- [ ] **Header incluye "Bearer " antes del token**
  ```javascript
  'Authorization': `Bearer ${token}` // ← "Bearer " con espacio
  ```

- [ ] **No hay espacios extra en el token**
  ```javascript
  const token = localStorage.getItem('access_token').trim();
  ```

- [ ] **El backend está corriendo**
  ```bash
  python manage.py runserver
  ```

- [ ] **No hay problemas de CORS**
  - Verifica en settings.py que `CORS_ALLOW_ALL_ORIGINS = True` (desarrollo)
  - O configura `CORS_ALLOWED_ORIGINS` correctamente

---

## 🚀 Token de Prueba Válido

Si quieres probar rápido, usa este token recién generado (válido por 5 minutos desde las 14:14 de hoy):

```javascript
// En la consola del navegador:
localStorage.setItem('access_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxNTAyNzUyLCJpYXQiOjE3NjE1MDI0NTIsImp0aSI6ImZjMjYyMTA4MmJhNzRlOWRhZTA1NTYwOWJmODE1NDkyIiwidXNlcl9pZCI6NDN9.NOuR_pThRcySsWSvddEdlYLX7qcECYAEQH-2w2ykamU');

// Luego refresca la página de auditoría
location.reload();
```

⚠️ **Nota:** Este token expira rápido, es solo para pruebas. El login debe generar tokens nuevos.

---

## 📞 Resumen

**El problema NO es del backend** ✅ (backend funciona perfectamente)

**El problema ES del frontend** ❌ (token no se guarda/envía)

**Soluciones:**
1. Guardar token después del login
2. Verificar que se lee correctamente en AdminAudit
3. Enviar con el formato correcto: `Bearer ${token}`
4. Implementar refresh automático cuando expire

---

## 🎯 Próximos pasos

1. **Verifica** que el login guarda el token con `console.log()`
2. **Verifica** que AdminAudit lee el token con `console.log()`
3. **Implementa** el servicio de autenticación centralizado
4. **Prueba** la aplicación completa

**¡El backend está listo! Solo falta ajustar el frontend.** 🚀
