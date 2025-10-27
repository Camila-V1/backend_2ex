# 🔐 GUÍA DE LOGIN - SOLUCIÓN ERROR 401

## ❌ Problema Actual

El frontend está recibiendo **401 Unauthorized** al intentar hacer login.

```
POST /api/token/ → 401 Unauthorized
```

## ✅ Diagnóstico Completo

### Backend: 100% Funcional
- ✅ Todos los usuarios están activos
- ✅ Todas las contraseñas funcionan correctamente
- ✅ Endpoint `/api/token/` responde correctamente

### Problema: Frontend enviando credenciales incorrectas
- ❌ Usuario o password con errores tipográficos
- ❌ Espacios en blanco adicionales
- ❌ Campo incorrecto (¿email en lugar de username?)
- ❌ Mayúsculas/minúsculas incorrectas

---

## 🎯 Solución: Formato Correcto

### Endpoint de Login
```
POST http://127.0.0.1:8000/api/token/
```

### Headers Requeridos
```
Content-Type: application/json
```

### Body del Request (JSON)
```json
{
  "username": "juan_cliente",
  "password": "juan123"
}
```

### Respuesta Exitosa (200 OK)
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 👥 Usuarios de Prueba Verificados

**⚠️ IMPORTANTE: Las contraseñas usan solo el NOMBRE, sin "_cliente"**

### Clientes (Sin rol especial)
| Username | Password | Email | ✅ Verificado |
|----------|----------|-------|---------------|
| `juan_cliente` | `juan123` ⚠️ | juan@email.com | ✅ Funciona |
| `laura_cliente` | `laura123` ⚠️ | laura@email.com | ✅ Funciona |
| `pedro_cliente` | `pedro123` ⚠️ | pedro@email.com | ✅ Funciona |
| `carmen_cliente` | `carmen123` ⚠️ | carmen@email.com | ✅ Funciona |
| `diego_cliente` | `diego123` ⚠️ | diego@email.com | ✅ Funciona |
| `elena_cliente` | `elena123` ⚠️ | elena@email.com | ✅ Funciona |

**Nota:** La contraseña es el **nombre** (primera parte) + "123"
- Username: `juan_cliente` → Password: `juan123` (NO `juan_cliente123`)
- Username: `laura_cliente` → Password: `laura123` (NO `laura_cliente123`)

### Administradores (ADMIN)
| Username | Password | Email |
|----------|----------|-------|
| `admin` | `admin123` | admin@ecommerce.com |
| `maria_admin` | `maria123` | maria.admin@ecommerce.com |

### Managers (MANAGER)
| Username | Password | Email |
|----------|----------|-------|
| `carlos_manager` | `carlos123` | carlos.manager@ecommerce.com |
| `ana_manager` | `ana123` | ana.manager@ecommerce.com |

### Cajeros (CAJERO)
| Username | Password | Email |
|----------|----------|-------|
| `luis_cajero` | `luis123` | luis.cajero@ecommerce.com |
| `sofia_cajero` | `sofia123` | sofia.cajero@ecommerce.com |

---

## 🧪 Pruebas con CURL

### Prueba 1: Login como Cliente
```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"juan_cliente\",\"password\":\"juan123\"}"
```

**Resultado esperado:** 
```json
{
  "refresh": "eyJ0eXAi...",
  "access": "eyJ0eXAi..."
}
```

### Prueba 2: Login como Admin
```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

### Prueba 3: Login Incorrecto (debe dar 401)
```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"juan_cliente\",\"password\":\"contraseña_incorrecta\"}"
```

**Resultado esperado:** 401 Unauthorized

---

## 🔍 Checklist para Frontend

### 1. Verificar el campo 'username'
```javascript
// ❌ INCORRECTO - Usando 'email'
{
  "email": "juan@email.com",
  "password": "juan123"
}

// ✅ CORRECTO - Usando 'username'
{
  "username": "juan_cliente",
  "password": "juan123"
}
```

### 2. Verificar espacios en blanco
```javascript
// ❌ INCORRECTO - Espacios adicionales
const username = " juan_cliente " // Tiene espacios
const password = "juan123 "       // Tiene espacio al final

// ✅ CORRECTO - Sin espacios
const username = "juan_cliente".trim()
const password = "juan123".trim()
```

### 3. Verificar mayúsculas/minúsculas
```javascript
// ❌ INCORRECTO
username: "Juan_Cliente"  // Mayúscula inicial
username: "JUAN_CLIENTE"  // Todo mayúsculas

// ✅ CORRECTO
username: "juan_cliente"  // Todo minúsculas
```

### 4. Código de ejemplo (React/JavaScript)
```javascript
// LoginForm.jsx o AuthService.js
const login = async (username, password) => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/token/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.trim(),  // Eliminar espacios
        password: password.trim(),  // Eliminar espacios
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login fallido');
    }

    const data = await response.json();
    // Guardar tokens
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    
    return data;
  } catch (error) {
    console.error('Error en login:', error);
    throw error;
  }
};
```

---

## 🐛 Debug del Frontend

### Ver qué está enviando el frontend
Agregar en el código del frontend antes del fetch:

```javascript
console.log('LOGIN REQUEST:', {
  url: 'http://127.0.0.1:8000/api/token/',
  method: 'POST',
  body: {
    username: username,
    password: password  // NO mostrar en producción
  }
});
```

### Ver la respuesta del servidor
```javascript
.catch(async (response) => {
  if (response.status === 401) {
    const errorData = await response.json();
    console.error('ERROR 401:', errorData);
    // Verificar si dice "No active account found with the given credentials"
  }
});
```

---

## ⚠️ Errores Comunes

### Error 1: "detail": "No active account found with the given credentials"
**Causa:** Username o password incorrectos

**Solución:**
- Verificar que el username sea exacto: `juan_cliente` (no `Juan_Cliente`)
- Verificar que el password sea exacto: `juan123` (no `Juan123`)
- Usar CREDENCIALES_ACCESO.txt como referencia

### Error 2: 400 Bad Request
**Causa:** JSON malformado o campos faltantes

**Solución:**
- Verificar que envías `username` y `password`
- Verificar que el Content-Type sea `application/json`
- Verificar que el body sea JSON válido

### Error 3: 403 Forbidden
**Causa:** CSRF token o CORS

**Solución:**
- CORS ya está configurado en el backend para localhost:5173
- No se requiere CSRF para JWT

---

## 📞 Soporte Rápido

Si el problema persiste, ejecutar estos comandos en el backend:

### Verificar usuarios en BD
```bash
cd backend_2ex
python test_login.py
```

### Ver archivo de credenciales
```bash
cat CREDENCIALES_ACCESO.txt
```

### Recrear usuarios si es necesario
```bash
python seed_data.py
```

---

## ✅ Test Final

Una vez corregido el frontend, deberías poder:

1. ✅ Hacer login con `juan_cliente` / `juan123`
2. ✅ Recibir tokens JWT válidos
3. ✅ Usar el access token para llamar a otros endpoints
4. ✅ Ver el perfil del usuario en `/api/users/profile/`

---

**Nota:** Todos los usuarios fueron probados y funcionan correctamente. El problema está 100% en el lado del frontend enviando credenciales incorrectas.
