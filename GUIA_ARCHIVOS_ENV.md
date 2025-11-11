# 📋 Guía de Archivos .env.production para Frontend

## 📦 Archivos Creados

He creado **4 archivos** `.env.production` listos para usar según tu framework:

---

## 🎯 ¿Cuál Archivo Usar?

### 1️⃣ **`.env.production.react`** → Para React (Create React App)
```bash
REACT_APP_API_URL=http://98.92.49.243/api
REACT_APP_API_BASE_URL=http://98.92.49.243
REACT_APP_ADMIN_URL=http://98.92.49.243/admin
```

---

### 2️⃣ **`.env.production.nextjs`** → Para Next.js
```bash
# Públicas (cliente)
NEXT_PUBLIC_API_URL=http://98.92.49.243/api
NEXT_PUBLIC_API_BASE_URL=http://98.92.49.243

# Privadas (servidor)
API_URL=http://98.92.49.243/api
```

---

### 3️⃣ **`.env.production.vue`** → Para Vue 3 + Vite
```bash
VITE_API_URL=http://98.92.49.243/api
VITE_API_BASE_URL=http://98.92.49.243
VITE_ADMIN_URL=http://98.92.49.243/admin
```

---

### 4️⃣ **`.env.production.frontend`** → Referencia completa
- Incluye configuración para TODOS los frameworks
- Documentación completa de endpoints
- Credenciales de prueba
- Instrucciones de uso

---

## 🚀 Cómo Usar

### Paso 1: Copiar al Proyecto Frontend

**Opción A - Copiar manualmente:**
1. Abre el archivo correspondiente a tu framework:
   - React: `.env.production.react`
   - Next.js: `.env.production.nextjs`
   - Vue/Vite: `.env.production.vue`

2. Copia todo el contenido

3. Ve a la **raíz** de tu proyecto frontend

4. Crea un archivo llamado `.env.production`

5. Pega el contenido

**Opción B - Copiar con PowerShell:**

**Para React:**
```powershell
# Desde la carpeta backend_2ex
Copy-Item .env.production.react "C:\ruta\a\tu\proyecto\frontend\.env.production"
```

**Para Next.js:**
```powershell
Copy-Item .env.production.nextjs "C:\ruta\a\tu\proyecto\frontend\.env.production"
```

**Para Vue/Vite:**
```powershell
Copy-Item .env.production.vue "C:\ruta\a\tu\proyecto\frontend\.env.production"
```

---

### Paso 2: Verificar la Estructura

Tu proyecto frontend debe verse así:

```
📁 mi-proyecto-frontend/
├── 📄 package.json
├── 📄 .env.production    ← NUEVO ARCHIVO AQUÍ
├── 📄 .gitignore
├── 📁 src/
│   ├── App.js (o App.jsx/App.vue)
│   └── ...
└── 📁 public/
```

---

### Paso 3: Actualizar tu Código

Asegúrate de que tu código use las variables de entorno:

**React:**
```javascript
const API_URL = process.env.REACT_APP_API_URL;
```

**Next.js:**
```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL;
```

**Vue/Vite:**
```javascript
const API_URL = import.meta.env.VITE_API_URL;
```

---

### Paso 4: Probar Localmente

```bash
npm run build
```

✅ Debe compilar sin errores

---

### Paso 5: Configurar en Vercel

Después de desplegar en Vercel, debes agregar las mismas variables en el dashboard:

1. Ve a tu proyecto en Vercel
2. **Settings** → **Environment Variables**
3. Agrega según tu framework:

**Para React:**
- Name: `REACT_APP_API_URL`
- Value: `http://98.92.49.243/api`

**Para Next.js:**
- Name: `NEXT_PUBLIC_API_URL`
- Value: `http://98.92.49.243/api`

**Para Vue/Vite:**
- Name: `VITE_API_URL`
- Value: `http://98.92.49.243/api`

4. Marca: ☑️ Production ☑️ Preview ☑️ Development
5. Click **"Add"**
6. **Redeploy** desde Deployments

---

### Paso 6: Configurar CORS

Después de desplegar, ejecuta:

```powershell
.\update_cors_for_vercel.ps1 -VercelDomain "tu-app.vercel.app"
```

---

## 📊 Información del Backend

**Backend desplegado en:**
- URL: `http://98.92.49.243`
- API: `http://98.92.49.243/api/`
- Admin: `http://98.92.49.243/admin/`

**Datos disponibles:**
- ✅ 37 productos
- ✅ 65 órdenes
- ✅ 35 devoluciones
- ✅ 18 usuarios

**Credenciales de prueba:**
```
Cliente:  juan_cliente / password123
Manager:  carlos_manager / manager123
Admin:    admin / admin123
```

---

## 🔍 Diferencias Entre Frameworks

| Framework | Prefijo Variable | Acceso en Código |
|-----------|-----------------|------------------|
| **React (CRA)** | `REACT_APP_*` | `process.env.REACT_APP_API_URL` |
| **Next.js** | `NEXT_PUBLIC_*` | `process.env.NEXT_PUBLIC_API_URL` |
| **Vue/Vite** | `VITE_*` | `import.meta.env.VITE_API_URL` |
| **Nuxt 3** | `NUXT_PUBLIC_*` | `process.env.NUXT_PUBLIC_API_URL` |
| **Astro** | `PUBLIC_*` | `import.meta.env.PUBLIC_API_URL` |

---

## ⚠️ Notas Importantes

### 1. Archivos .env NO se suben a Git

Verifica que tu `.gitignore` incluya:
```
.env
.env.local
.env.production
.env.development
```

### 2. Variables Públicas vs Privadas

**Públicas** (con prefijos como `REACT_APP_`, `NEXT_PUBLIC_`, `VITE_`):
- ✅ Se incluyen en el bundle del cliente
- ✅ Son visibles en el código JavaScript
- ❌ NO uses para información sensible

**Privadas** (sin prefijos públicos, solo en Next.js server-side):
- ✅ Solo accesibles en el servidor
- ✅ Seguras para información sensible
- ❌ NO accesibles en componentes del cliente

### 3. Cambiar Variables Requiere Rebuild

Si cambias una variable de entorno:
- **En desarrollo local:** Reinicia el servidor (`npm run dev`)
- **En Vercel:** Haz **Redeploy** desde el dashboard

---

## 🧪 Testing Rápido

### Probar conexión al backend

Abre la consola del navegador (F12) y ejecuta:

```javascript
fetch('http://98.92.49.243/api/products/')
  .then(r => r.json())
  .then(data => console.log('✅ Productos:', data))
  .catch(err => console.error('❌ Error:', err));
```

✅ Debe mostrar la lista de 37 productos

---

## 📝 Ejemplo Completo de Uso

### React con Axios

```javascript
// src/config/api.js
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  }
);

export default api;
```

```javascript
// src/services/authService.js
import api from '../config/api';

export const login = async (username, password) => {
  const response = await api.post('/users/login/', {
    username,
    password,
  });
  
  localStorage.setItem('access_token', response.data.access);
  localStorage.setItem('refresh_token', response.data.refresh);
  
  return response.data;
};

export const getProducts = async () => {
  const response = await api.get('/products/');
  return response.data;
};
```

---

## 🆘 Troubleshooting

### Error: "process.env.REACT_APP_API_URL is undefined"

**Solución:**
1. Verifica que el archivo se llame exactamente `.env.production`
2. Verifica que la variable tenga el prefijo correcto
3. Reinicia el servidor de desarrollo
4. Haz `npm run build` de nuevo

### Error: CORS al llamar la API

**Solución:**
```powershell
.\update_cors_for_vercel.ps1 -VercelDomain "tu-app.vercel.app"
```

### Variables no se cargan en Vercel

**Solución:**
1. Verifica que las agregaste en Vercel Dashboard
2. Verifica el nombre (con prefijo correcto)
3. Haz **Redeploy** desde Deployments

---

## ✅ Checklist

- [ ] Copié el archivo `.env.production` correcto a mi proyecto frontend
- [ ] El archivo está en la raíz del proyecto
- [ ] Mi código usa `process.env.REACT_APP_API_URL` (o equivalente)
- [ ] Probé con `npm run build` localmente
- [ ] Subí el código a GitHub
- [ ] Agregué las variables en Vercel Dashboard
- [ ] Desplegué en Vercel
- [ ] Ejecuté el script de CORS
- [ ] Probé que funciona en el navegador

---

## 📚 Documentación Adicional

- **VERCEL_EN_10_MINUTOS.md** - Guía rápida de despliegue
- **GUIA_PASO_A_PASO_VERCEL.md** - Guía detallada
- **frontend_config_example.js** - Ejemplos de código completos
- **VERCEL_CHEAT_SHEET.md** - Referencia rápida

---

**¡Listo para copiar y usar!** 🚀
