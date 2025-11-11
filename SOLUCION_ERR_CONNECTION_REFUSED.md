# 🚨 SOLUCIÓN DEFINITIVA - ERR_CONNECTION_REFUSED

## 🔴 **PROBLEMA IDENTIFICADO:**

```
Error: net::ERR_CONNECTION_REFUSED
URL: http://98.92.49.243/api/token/
```

**Causa:** 
- Frontend en HTTPS (Vercel) no puede hacer peticiones HTTP directas al backend
- El navegador bloquea peticiones HTTP desde páginas HTTPS (Mixed Content)
- El meta tag `upgrade-insecure-requests` intenta convertir a HTTPS, pero el backend no tiene SSL

---

## ✅ **SOLUCIÓN: Proxy de Vercel**

Usar Vercel como proxy para redirigir las peticiones del frontend al backend.

### **Arquitectura:**

```
Frontend (HTTPS)  →  Vercel Proxy (HTTPS)  →  Backend AWS (HTTP)
      ✅                    ✅                        ✅
```

---

## 🔧 **IMPLEMENTACIÓN:**

### **Paso 1: Crear `vercel.json` en la raíz del frontend**

Crea el archivo `vercel.json` con este contenido:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "http://98.92.49.243/api/:path*"
    }
  ],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Credentials",
          "value": "true"
        },
        {
          "key": "Access-Control-Allow-Origin",
          "value": "*"
        },
        {
          "key": "Access-Control-Allow-Methods",
          "value": "GET,OPTIONS,PATCH,DELETE,POST,PUT"
        },
        {
          "key": "Access-Control-Allow-Headers",
          "value": "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization"
        }
      ]
    }
  ]
}
```

**Explicación:**
- `rewrites`: Redirige todas las peticiones `/api/*` al backend AWS
- `headers`: Configura CORS para permitir las peticiones

---

### **Paso 2: Actualizar la configuración del API en el frontend**

**Opción A: Variable de entorno (RECOMENDADO)**

En Vercel Dashboard o en tu `.env.production`:

```env
# Usar ruta relativa (Vercel manejará el proxy)
REACT_APP_API_URL=/api

# O para Next.js:
NEXT_PUBLIC_API_URL=/api

# O para Vite:
VITE_API_URL=/api
```

**Opción B: Hardcodear en el código (si no usas variables de entorno)**

En tu `authService.js` o archivo similar:

```javascript
// ANTES (causaba ERR_CONNECTION_REFUSED):
const API_URL = 'http://98.92.49.243/api';  // ❌

// DESPUÉS (usa el proxy de Vercel):
const API_URL = '/api';  // ✅
```

---

### **Paso 3: Actualizar el archivo authService.js**

**Archivo completo corregido:**

```javascript
import axios from 'axios';

// Usar ruta relativa - Vercel la redirigirá al backend
const API_URL = process.env.REACT_APP_API_URL || '/api';

// Crear instancia de axios
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Función de login
export const login = async (username, password) => {
  try {
    console.log('🔷 [LOGIN] Llamando a:', `${API_URL}/token/`);
    
    const response = await api.post('/token/', {
      username,
      password,
    });
    
    console.log('✅ [LOGIN] Respuesta exitosa:', response.data);
    
    const { access, refresh } = response.data;
    
    // Guardar tokens
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    
    // Configurar header de autenticación
    api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
    
    return {
      success: true,
      token: access,
      refreshToken: refresh,
    };
  } catch (error) {
    console.error('❌ [LOGIN ERROR]:', error);
    console.error('❌ [LOGIN ERROR] Response:', error.response);
    return {
      success: false,
      error: error.response?.data?.detail || error.message || 'Error en el inicio de sesión',
    };
  }
};

// Resto de funciones...
export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  delete api.defaults.headers.common['Authorization'];
};

export const getAccessToken = () => {
  return localStorage.getItem('access_token');
};

export const isAuthenticated = () => {
  return !!getAccessToken();
};

export default api;
```

---

### **Paso 4: QUITAR el meta tag de upgrade-insecure-requests**

En tu `index.html`, **ELIMINA** esta línea:

```html
<!-- ❌ ELIMINAR ESTA LÍNEA -->
<meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
```

**Por qué:** El proxy de Vercel ya maneja todo en HTTPS, no necesitas forzar la conversión.

---

## 🚀 **PASOS PARA APLICAR:**

### **1. En tu proyecto frontend local:**

```bash
cd tu-proyecto-frontend

# Crear vercel.json
# (Ya lo creé en: C:\Users\asus\Documents\SISTEMAS DE INFORMACION 2\segundo examen SI2\backend_2ex\vercel.json)
# Cópialo a la raíz de tu proyecto frontend

# Crear/actualizar .env.production
echo "REACT_APP_API_URL=/api" > .env.production

# O si usas Vite:
echo "VITE_API_URL=/api" > .env.production

# O si usas Next.js:
echo "NEXT_PUBLIC_API_URL=/api" > .env.production
```

---

### **2. Actualizar authService.js:**

Cambia:
```javascript
const API_URL = 'http://98.92.49.243/api';  // ❌
```

Por:
```javascript
const API_URL = process.env.REACT_APP_API_URL || '/api';  // ✅
```

---

### **3. Eliminar meta tag en index.html:**

```html
<!-- ❌ ELIMINAR -->
<meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
```

---

### **4. Hacer commit y push:**

```bash
git add .
git commit -m "fix: Configurar proxy de Vercel para API"
git push origin main
```

---

### **5. Esperar redeploy automático de Vercel:**

Vercel detectará el `vercel.json` y reconfigurará el proxy automáticamente.

⏱️ Tiempo: 2-3 minutos

---

## 🧪 **VERIFICACIÓN:**

Después del deploy, las peticiones funcionarán así:

### **Antes (ERR_CONNECTION_REFUSED):**
```
Frontend → http://98.92.49.243/api/token/ ❌
(Bloqueado por Mixed Content)
```

### **Después (CON PROXY):**
```
Frontend → https://tu-app.vercel.app/api/token/ → http://98.92.49.243/api/token/ ✅
          (HTTPS)                                   (HTTP - interno)
```

---

## 📋 **CHECKLIST:**

```
□ Crear vercel.json en la raíz del proyecto frontend
□ Actualizar API_URL a '/api' (ruta relativa)
□ Eliminar meta tag upgrade-insecure-requests de index.html
□ Crear/actualizar .env.production con REACT_APP_API_URL=/api
□ git add, commit, push
□ Esperar redeploy de Vercel
□ Probar login desde la app
```

---

## 🎯 **RESUMEN:**

```
Problema:  Mixed Content (HTTPS → HTTP) bloqueado
Solución:  Proxy de Vercel (HTTPS → HTTPS → HTTP)
Archivo:   vercel.json en la raíz del frontend
Variable:  REACT_APP_API_URL=/api
Resultado: ✅ Login funcional sin errores
```

---

## 🔑 **CREDENCIALES PARA PROBAR:**

```
username: admin
password: admin123
```

---

## 🆘 **SI AÚN NO FUNCIONA:**

### 1. Verificar que vercel.json esté en la raíz:

```
tu-proyecto-frontend/
├── vercel.json          ← DEBE ESTAR AQUÍ
├── package.json
├── src/
└── public/
```

### 2. Verificar en DevTools Network:

```
Request URL: https://tu-app.vercel.app/api/token/  ✅
(Ya no debe ser http://98.92.49.243/...)
```

### 3. Verificar logs de Vercel:

```
1. Vercel Dashboard
2. Tu proyecto → Deployments
3. Latest → Function Logs
4. Buscar errores de proxy
```

---

**¡Copia el archivo `vercel.json` a tu proyecto frontend y haz push! Eso solucionará el problema.** 🚀
