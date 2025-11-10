# 🔐 01. AUTENTICACIÓN Y AUTORIZACIÓN

## 📝 Descripción General

El sistema usa **JWT (JSON Web Tokens)** para autenticación. El flujo es:
1. Usuario envía credenciales (username/password)
2. Backend devuelve `access_token` y `refresh_token`
3. Frontend usa `access_token` en cada request
4. Cuando expira, usa `refresh_token` para obtener nuevo `access_token`

---

## 🔑 Endpoints de Autenticación

### 1. Login (Obtener Token)

**POST** `/api/token/`

**Request:**
```json
{
  "username": "juan_cliente",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Ejemplo JavaScript:**
```javascript
const login = async (username, password) => {
  const response = await fetch('http://localhost:8000/api/token/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password })
  });
  
  if (!response.ok) {
    throw new Error('Login failed');
  }
  
  const data = await response.json();
  
  // Guardar tokens en localStorage
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  
  return data;
};
```

---

### 2. Refresh Token (Renovar Token Expirado)

**POST** `/api/token/refresh/`

**Request:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Ejemplo JavaScript:**
```javascript
const refreshToken = async () => {
  const refresh = localStorage.getItem('refresh_token');
  
  const response = await fetch('http://localhost:8000/api/token/refresh/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh })
  });
  
  if (!response.ok) {
    // Token refresh falló, redirigir a login
    localStorage.clear();
    window.location.href = '/login';
    return;
  }
  
  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  return data.access;
};
```

---

### 3. Obtener Perfil de Usuario

**GET** `/api/users/profile/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": 49,
  "username": "juan_cliente",
  "email": "juan@email.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "role": null,  // o "MANAGER" o "ADMIN"
  "phone_number": "+591 12345678",
  "created_at": "2025-10-15T10:30:00Z"
}
```

**Ejemplo JavaScript:**
```javascript
const getUserProfile = async () => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/users/profile/', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (response.status === 401) {
    // Token expirado, intentar refresh
    await refreshToken();
    return getUserProfile(); // Reintentar
  }
  
  return await response.json();
};
```

---

## 👥 Roles y Permisos

### Roles Disponibles:

| Role | Valor | Descripción |
|------|-------|-------------|
| Cliente | `null` | Usuario normal que compra y solicita devoluciones |
| Manager | `"MANAGER"` | Gestiona devoluciones, aprueba/rechaza |
| Admin | `"ADMIN"` | Acceso completo al sistema |

### Verificar Rol en Frontend:

```javascript
const checkRole = (user) => {
  if (user.role === 'ADMIN') {
    return 'admin';
  } else if (user.role === 'MANAGER') {
    return 'manager';
  } else {
    return 'cliente';
  }
};

// Ejemplo de uso
const user = await getUserProfile();
const role = checkRole(user);

if (role === 'manager' || role === 'admin') {
  // Mostrar opciones de gestión
  showManagementPanel();
}
```

---

## 🔒 Interceptor para Peticiones HTTP (Recomendado)

### Axios Interceptor:

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// Request interceptor - Agregar token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Manejar token expirado
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si es 401 y no hemos reintentado
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refresh = localStorage.getItem('refresh_token');
        const response = await axios.post(
          'http://localhost:8000/api/token/refresh/',
          { refresh }
        );

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        // Reintentar request original
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh falló, cerrar sesión
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

---

## 🧪 Testing de Autenticación

### Usuarios de Prueba Disponibles:

| Username | Password | Role |
|----------|----------|------|
| `juan_cliente` | `password123` | Cliente |
| `carlos_manager` | `password123` | Manager |
| `admin` | `admin123` | Admin |

### Ejemplo de Test:

```javascript
// Test login
const testLogin = async () => {
  try {
    const result = await login('juan_cliente', 'password123');
    console.log('✅ Login exitoso:', result);
    
    const profile = await getUserProfile();
    console.log('✅ Perfil obtenido:', profile);
  } catch (error) {
    console.error('❌ Error:', error);
  }
};
```

---

## ⚠️ Errores Comunes

### Error 401 - Unauthorized
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [...]
}
```
**Solución:** Token expirado o inválido. Usar refresh token o pedir login nuevamente.

### Error 400 - Bad Request (Login)
```json
{
  "detail": "No active account found with the given credentials"
}
```
**Solución:** Usuario o contraseña incorrectos.

---

## 📦 Estado de Sesión (React Example)

```javascript
import { createContext, useState, useContext, useEffect } from 'react';
import api from './api'; // El interceptor de arriba

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const profile = await api.get('/users/profile/');
        setUser(profile.data);
      } catch (error) {
        localStorage.clear();
      }
    }
    setLoading(false);
  };

  const login = async (username, password) => {
    const response = await api.post('/token/', { username, password });
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    await checkAuth();
  };

  const logout = () => {
    localStorage.clear();
    setUser(null);
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

---

**Siguiente:** Ver `02_PRODUCTOS_Y_ORDENES.md` para gestión de productos y órdenes
