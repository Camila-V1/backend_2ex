# 🚀 Guía de Despliegue Frontend en Vercel

## 📋 Información del Backend Desplegado

**Backend URL:** `http://98.92.49.243`

**Endpoints API disponibles:**
```
http://98.92.49.243/api/products/
http://98.92.49.243/api/categories/
http://98.92.49.243/api/users/login/
http://98.92.49.243/api/orders/
http://98.92.49.243/api/returns/
http://98.92.49.243/api/wallets/
http://98.92.49.243/api/audit-log/
http://98.92.49.243/admin/
```

---

## 🔧 Paso 1: Configurar Variables de Entorno en el Frontend

### Opción A: Si tu frontend usa `.env` (React, Vue, Next.js)

Crea o modifica el archivo `.env` o `.env.production` en tu proyecto frontend:

```bash
# .env.production
REACT_APP_API_URL=http://98.92.49.243/api
# o para Next.js:
NEXT_PUBLIC_API_URL=http://98.92.49.243/api
# o para Vue/Vite:
VITE_API_URL=http://98.92.49.243/api
```

### Opción B: Configuración directa en el código

Si tienes un archivo de configuración como `src/config.js` o `src/api/config.js`:

```javascript
// src/config.js
const config = {
  apiUrl: process.env.REACT_APP_API_URL || 'http://98.92.49.243/api',
  baseUrl: 'http://98.92.49.243',
};

export default config;
```

---

## 🌐 Paso 2: Configurar CORS en el Backend

**⚠️ IMPORTANTE:** Debes actualizar el backend para permitir peticiones desde tu dominio de Vercel.

### 2.1. Conectarse al servidor

```powershell
ssh -i django-backend-key.pem ubuntu@98.92.49.243
```

### 2.2. Editar el archivo .env

```bash
cd /var/www/django-backend
nano .env
```

### 2.3. Actualizar estas variables:

```bash
# Cambiar ALLOWED_HOSTS para incluir tu dominio de Vercel
ALLOWED_HOSTS=98.92.49.243,localhost,127.0.0.1,tu-app.vercel.app

# Configurar CORS para permitir tu frontend
CORS_ALLOWED_ORIGINS=https://tu-app.vercel.app,http://localhost:3000,http://localhost:5173

# O permitir todos los orígenes (solo para desarrollo/pruebas)
CORS_ALLOW_ALL_ORIGINS=True
```

### 2.4. Reiniciar Gunicorn

```bash
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
```

---

## 📦 Paso 3: Preparar el Frontend para Producción

### 3.1. Actualizar las llamadas a la API

Busca en tu frontend todos los archivos que hacen llamadas a la API y asegúrate de usar la variable de entorno:

**Ejemplo con Axios:**
```javascript
// src/api/axios.js
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://98.92.49.243/api';

const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default axiosInstance;
```

**Ejemplo con Fetch:**
```javascript
// src/api/fetchAPI.js
const API_URL = process.env.REACT_APP_API_URL || 'http://98.92.49.243/api';

export const fetchAPI = async (endpoint, options = {}) => {
  const token = localStorage.getItem('token');
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};
```

### 3.2. Verificar que el frontend compile sin errores

```powershell
# Desde tu carpeta del frontend
npm install
npm run build
# o
yarn build
```

---

## 🚀 Paso 4: Desplegar en Vercel

### Opción A: Despliegue desde GitHub (Recomendado)

#### 4.1. Subir tu frontend a GitHub

```powershell
# Desde la carpeta de tu frontend
git init
git add .
git commit -m "Preparar frontend para producción"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/TU-REPO-FRONTEND.git
git push -u origin main
```

#### 4.2. Conectar con Vercel

1. Ve a [vercel.com](https://vercel.com) e inicia sesión
2. Click en **"Add New Project"**
3. Selecciona **"Import Git Repository"**
4. Autoriza GitHub y selecciona tu repositorio frontend
5. Configura el proyecto:
   - **Framework Preset:** Detecta automáticamente (React, Next.js, Vue, etc.)
   - **Root Directory:** `.` (o la carpeta de tu frontend si está en subdirectorio)
   - **Build Command:** `npm run build` o `yarn build`
   - **Output Directory:** `build` (React) o `dist` (Vue/Vite) o `.next` (Next.js)

#### 4.3. Agregar Variables de Entorno en Vercel

En la configuración del proyecto en Vercel:

1. Ve a **Settings** → **Environment Variables**
2. Agrega estas variables:

```
REACT_APP_API_URL=http://98.92.49.243/api
```

O para Next.js:
```
NEXT_PUBLIC_API_URL=http://98.92.49.243/api
```

O para Vue/Vite:
```
VITE_API_URL=http://98.92.49.243/api
```

3. Click en **"Save"**
4. Ve a **Deployments** y haz **"Redeploy"**

### Opción B: Despliegue desde CLI de Vercel

#### 4.1. Instalar Vercel CLI

```powershell
npm install -g vercel
```

#### 4.2. Login en Vercel

```powershell
vercel login
```

#### 4.3. Desplegar

```powershell
# Desde tu carpeta del frontend
vercel

# Para producción:
vercel --prod
```

#### 4.4. Configurar variables de entorno

```powershell
vercel env add REACT_APP_API_URL
# Ingresa: http://98.92.49.243/api
# Selecciona: Production
```

---

## 🔒 Paso 5: Configurar HTTPS (Opcional pero Recomendado)

Vercel automáticamente proporciona HTTPS, pero tu backend está en HTTP. Esto puede causar **errores de contenido mixto** (Mixed Content).

### Solución 1: Usar HTTPS en el Backend (Recomendado)

Instalar SSL en el servidor AWS con Let's Encrypt:

```bash
# En el servidor AWS
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

### Solución 2: Permitir contenido mixto temporalmente

En tu frontend, agrega en el `index.html`:

```html
<!-- SOLO PARA DESARROLLO - NO RECOMENDADO EN PRODUCCIÓN -->
<meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
```

---

## 🧪 Paso 6: Probar el Despliegue

### 6.1. Probar endpoints desde tu frontend desplegado

Una vez desplegado en Vercel, abre la consola del navegador en tu sitio y prueba:

```javascript
// Test de login
fetch('http://98.92.49.243/api/users/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
})
.then(r => r.json())
.then(console.log)
.catch(console.error);

// Test de productos
fetch('http://98.92.49.243/api/products/')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);
```

### 6.2. Verificar CORS

Si ves errores de CORS en la consola, vuelve al **Paso 2** y actualiza las configuraciones de CORS en el backend.

---

## 📝 Paso 7: Actualizar ALLOWED_HOSTS y CORS después del despliegue

Una vez que tengas tu URL de Vercel (ejemplo: `mi-ecommerce.vercel.app`):

### 7.1. Conectarse al servidor

```powershell
ssh -i django-backend-key.pem ubuntu@98.92.49.243
```

### 7.2. Editar .env

```bash
cd /var/www/django-backend
sudo nano .env
```

### 7.3. Actualizar con tu dominio real

```bash
ALLOWED_HOSTS=98.92.49.243,localhost,127.0.0.1,mi-ecommerce.vercel.app
CORS_ALLOWED_ORIGINS=https://mi-ecommerce.vercel.app
```

### 7.4. Reiniciar servicios

```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

## 🎯 Checklist Final

- [ ] ✅ Variables de entorno configuradas en el frontend
- [ ] ✅ Frontend hace llamadas a `http://98.92.49.243/api`
- [ ] ✅ CORS configurado en el backend para permitir tu dominio Vercel
- [ ] ✅ ALLOWED_HOSTS actualizado con tu dominio Vercel
- [ ] ✅ Frontend desplegado en Vercel
- [ ] ✅ Login funciona desde el frontend en Vercel
- [ ] ✅ Puedes ver productos desde el frontend en Vercel
- [ ] ✅ No hay errores de CORS en la consola del navegador

---

## 🔑 Credenciales de Prueba

```
👤 Cliente: juan_cliente / password123
👔 Manager: carlos_manager / manager123
⚙️  Admin: admin / admin123
```

---

## 🆘 Solución de Problemas Comunes

### Error: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solución:** Actualiza `CORS_ALLOWED_ORIGINS` en el backend incluyendo tu URL de Vercel.

### Error: "Invalid HTTP_HOST header"

**Solución:** Agrega tu dominio de Vercel a `ALLOWED_HOSTS` en el backend.

### Error: "Mixed Content" (contenido mixto)

**Solución:** Configura HTTPS en el backend o usa la meta tag para desarrollo.

### El frontend no encuentra el backend

**Solución:** Verifica que la variable de entorno `REACT_APP_API_URL` (o equivalente) esté correctamente configurada en Vercel.

### Los tokens JWT no se guardan

**Solución:** Verifica que estés usando `localStorage` o `sessionStorage` correctamente en el frontend.

---

## 📚 Recursos Adicionales

- [Documentación de Vercel](https://vercel.com/docs)
- [Variables de entorno en Vercel](https://vercel.com/docs/environment-variables)
- [Django CORS Headers](https://github.com/adamchainz/django-cors-headers)
- [Let's Encrypt para SSL](https://letsencrypt.org/)

---

## 🎉 ¡Listo!

Una vez completados todos los pasos, tu frontend estará desplegado en Vercel y conectado al backend en AWS.

**URLs finales:**
- Frontend: `https://tu-app.vercel.app`
- Backend API: `http://98.92.49.243/api`
- Admin Panel: `http://98.92.49.243/admin`
