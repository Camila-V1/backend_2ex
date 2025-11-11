# 🚀 Guía Paso a Paso: Desplegar Frontend en Vercel

## 📋 Requisitos Previos

Antes de empezar, asegúrate de tener:
- ✅ Tu proyecto frontend terminado (React, Next.js, Vue, etc.)
- ✅ Cuenta en GitHub (para conectar con Vercel)
- ✅ Backend desplegado en AWS: `http://98.92.49.243`

---

## 🎯 PARTE 1: Preparar tu Proyecto Frontend

### Paso 1.1: Agregar Variable de Entorno

En la **raíz de tu proyecto frontend**, crea un archivo llamado **`.env.production`**:

**Para React (Create React App):**
```env
REACT_APP_API_URL=http://98.92.49.243/api
```

**Para Next.js:**
```env
NEXT_PUBLIC_API_URL=http://98.92.49.243/api
```

**Para Vue/Vite:**
```env
VITE_API_URL=http://98.92.49.243/api
```

---

### Paso 1.2: Verificar que tu Código use la Variable

En tu código, las llamadas a la API deben usar esta variable:

**React:**
```javascript
const API_URL = process.env.REACT_APP_API_URL;
fetch(`${API_URL}/products/`)
```

**Next.js:**
```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL;
fetch(`${API_URL}/products/`)
```

**Vue/Vite:**
```javascript
const API_URL = import.meta.env.VITE_API_URL;
fetch(`${API_URL}/products/`)
```

---

### Paso 1.3: Probar Build Local

Abre tu terminal en la carpeta del frontend y ejecuta:

```bash
npm install
npm run build
```

✅ Si compile sin errores, estás listo para continuar.
❌ Si hay errores, corrígelos antes de desplegar.

---

### Paso 1.4: Subir a GitHub

**Si ya tienes tu proyecto en GitHub, salta al Paso 2.**

**Si NO está en GitHub:**

```bash
# Inicializar Git (si no lo has hecho)
git init

# Agregar todos los archivos
git add .

# Crear commit
git commit -m "Preparar para producción"

# Crear repositorio en GitHub y conectar
git remote add origin https://github.com/TU-USUARIO/TU-REPO-FRONTEND.git
git branch -M main
git push -u origin main
```

---

## 🌐 PARTE 2: Crear Cuenta y Proyecto en Vercel

### Paso 2.1: Crear Cuenta en Vercel

1. Ve a **[https://vercel.com](https://vercel.com)**
2. Click en **"Sign Up"** (Registrarse)
3. Elige **"Continue with GitHub"** (Continuar con GitHub)
4. Autoriza a Vercel para acceder a tu cuenta de GitHub

![Vercel Sign Up](https://assets.vercel.com/image/upload/v1/frontends/assets/home/signup.png)

---

### Paso 2.2: Importar tu Proyecto

1. Una vez en el dashboard, click en **"Add New..."** → **"Project"**
2. Verás una lista de tus repositorios de GitHub
3. Busca tu repositorio frontend
4. Click en **"Import"** al lado del repositorio

![Import Project](https://assets.vercel.com/image/upload/v1/frontends/assets/home/import-git.png)

---

### Paso 2.3: Configurar el Proyecto

Vercel detecta automáticamente el framework. Verifica que sea correcto:

**Framework Preset:**
- ✅ **Create React App** (si usas React)
- ✅ **Next.js** (si usas Next.js)
- ✅ **Vite** (si usas Vue/Vite)

**Build Settings** (generalmente auto-detectados):
- **Build Command:** `npm run build` o `yarn build`
- **Output Directory:** 
  - `build` (para React)
  - `.next` (para Next.js)
  - `dist` (para Vue/Vite)
- **Install Command:** `npm install` o `yarn install`

> ⚠️ **NO cambies nada si dice "Detected automatically" - Vercel ya lo configuró correctamente**

---

### Paso 2.4: Agregar Variables de Entorno en Vercel

**🔴 IMPORTANTE:** Aquí agregas las variables de entorno que necesita tu frontend.

1. En la página de configuración, busca la sección **"Environment Variables"**
2. Click en **"Add"** o ver el formulario
3. Agrega esta variable según tu framework:

**Para React:**
- **Name:** `REACT_APP_API_URL`
- **Value:** `http://98.92.49.243/api`
- **Environment:** Marca las 3 opciones:
  - ☑️ Production
  - ☑️ Preview
  - ☑️ Development

**Para Next.js:**
- **Name:** `NEXT_PUBLIC_API_URL`
- **Value:** `http://98.92.49.243/api`
- **Environment:** Marca las 3 opciones

**Para Vue/Vite:**
- **Name:** `VITE_API_URL`
- **Value:** `http://98.92.49.243/api`
- **Environment:** Marca las 3 opciones

![Environment Variables](https://assets.vercel.com/image/upload/v1/frontends/assets/home/env-vars.png)

4. Click en **"Add"** para guardar la variable

---

### Paso 2.5: Desplegar

1. Click en **"Deploy"** (botón azul grande)
2. Espera mientras Vercel construye tu proyecto (2-5 minutos)
3. ✅ Verás "Congratulations!" cuando termine

![Deploy Success](https://assets.vercel.com/image/upload/v1/frontends/assets/home/deploy-success.png)

---

### Paso 2.6: Obtener tu URL

1. En la pantalla de éxito, verás tu URL de Vercel:
   - Ejemplo: `https://mi-proyecto-abc123.vercel.app`
2. **📝 COPIA ESTA URL** - la necesitarás en el siguiente paso

![Vercel URL](https://assets.vercel.com/image/upload/v1/frontends/assets/home/domain.png)

---

## 🔧 PARTE 3: Configurar CORS en el Backend

### Paso 3.1: Usar el Script Automático (Recomendado)

Abre **PowerShell** en la carpeta `backend_2ex` y ejecuta:

```powershell
.\update_cors_for_vercel.ps1 -VercelDomain "mi-proyecto-abc123.vercel.app"
```

> ⚠️ **Reemplaza `mi-proyecto-abc123.vercel.app` con TU URL real de Vercel (sin https://)**

**Ejemplo:**
```powershell
.\update_cors_for_vercel.ps1 -VercelDomain "ecommerce-frontend-xyz789.vercel.app"
```

El script automáticamente:
- ✅ Actualiza ALLOWED_HOSTS
- ✅ Configura CORS_ALLOWED_ORIGINS
- ✅ Reinicia servicios
- ✅ Verifica que todo esté funcionando

---

### Paso 3.2: Configuración Manual (Si el script no funciona)

**3.2.1. Conectarse al servidor:**

```powershell
ssh -i django-backend-key.pem ubuntu@98.92.49.243
```

**3.2.2. Editar archivo .env:**

```bash
cd /var/www/django-backend
sudo nano .env
```

**3.2.3. Buscar y modificar estas líneas:**

Cambia:
```bash
ALLOWED_HOSTS=98.92.49.243,localhost,127.0.0.1
```

Por (reemplaza con TU dominio de Vercel):
```bash
ALLOWED_HOSTS=98.92.49.243,localhost,127.0.0.1,mi-proyecto-abc123.vercel.app
```

Y cambia:
```bash
CORS_ALLOW_ALL_ORIGINS=True
```

Por (reemplaza con TU dominio de Vercel):
```bash
CORS_ALLOWED_ORIGINS=https://mi-proyecto-abc123.vercel.app,http://localhost:3000
CORS_ALLOW_ALL_ORIGINS=False
```

**3.2.4. Guardar y salir:**
- Presiona `Ctrl + X`
- Presiona `Y` (Yes)
- Presiona `Enter`

**3.2.5. Reiniciar servicios:**

```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

**3.2.6. Verificar que estén activos:**

```bash
sudo systemctl status gunicorn
sudo systemctl status nginx
```

Debe decir "active (running)" en verde.

**3.2.7. Salir del servidor:**

```bash
exit
```

---

## 🧪 PARTE 4: Probar tu Aplicación

### Paso 4.1: Abrir tu Frontend

Abre tu navegador y ve a tu URL de Vercel:
```
https://mi-proyecto-abc123.vercel.app
```

---

### Paso 4.2: Abrir Consola del Navegador

1. Presiona **F12** o **Ctrl+Shift+I**
2. Ve a la pestaña **"Console"**
3. Busca errores rojos

---

### Paso 4.3: Verificar que NO haya Errores de CORS

✅ **CORRECTO:** La consola está limpia o solo tiene warnings amarillos.

❌ **ERROR:** Si ves esto:
```
Access to fetch at 'http://98.92.49.243/api/...' from origin 'https://tu-app.vercel.app' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
```

**Solución:** Vuelve a la **Parte 3** y verifica que agregaste tu dominio de Vercel correctamente.

---

### Paso 4.4: Probar Login

1. Ve a la página de login de tu aplicación
2. Intenta iniciar sesión con estas credenciales:

```
Username: admin
Password: admin123
```

**O como cliente:**
```
Username: juan_cliente
Password: password123
```

✅ Si el login funciona, ¡todo está bien!

---

### Paso 4.5: Probar API desde la Consola

En la consola del navegador (F12), ejecuta:

```javascript
fetch('http://98.92.49.243/api/products/')
  .then(r => r.json())
  .then(data => console.log('Productos:', data))
  .catch(err => console.error('Error:', err));
```

✅ Debe mostrar la lista de 37 productos.

---

## 🎨 PARTE 5: Personalizar (Opcional)

### Cambiar el Nombre del Proyecto

1. En Vercel dashboard, ve a **Settings** → **General**
2. En "Project Name", cambia el nombre
3. Tu nueva URL será: `https://nuevo-nombre.vercel.app`

---

### Agregar Dominio Personalizado

1. En Vercel dashboard, ve a **Settings** → **Domains**
2. Click en **"Add"**
3. Ingresa tu dominio (ej: `www.mitienda.com`)
4. Sigue las instrucciones para configurar DNS
5. **⚠️ IMPORTANTE:** Después debes actualizar CORS en el backend con tu nuevo dominio:

```powershell
.\update_cors_for_vercel.ps1 -VercelDomain "www.mitienda.com"
```

---

## 🔄 PARTE 6: Actualizar tu Aplicación

### Cuando hagas cambios en tu código:

1. **Haz commit y push a GitHub:**
   ```bash
   git add .
   git commit -m "Actualización de funcionalidad"
   git push
   ```

2. **Vercel automáticamente:**
   - ✅ Detecta el cambio
   - ✅ Construye el nuevo código
   - ✅ Despliega automáticamente

3. **Ver el progreso:**
   - Ve al dashboard de Vercel
   - Click en tu proyecto
   - Ve la pestaña **"Deployments"**
   - Verás el estado del nuevo despliegue

---

### Si necesitas cambiar variables de entorno:

1. En Vercel dashboard, ve a **Settings** → **Environment Variables**
2. Edita la variable que necesites
3. **⚠️ IMPORTANTE:** Debes hacer **Redeploy** para que tome efecto:
   - Ve a **Deployments**
   - Click en los tres puntos `...` del último deployment
   - Click en **"Redeploy"**

---

## ❌ Solución de Problemas Comunes

### ❌ Problema 1: Error de CORS

**Síntoma:**
```
CORS policy: No 'Access-Control-Allow-Origin' header
```

**Solución:**
1. Verifica que ejecutaste el script: `.\update_cors_for_vercel.ps1`
2. Verifica que usaste tu URL de Vercel correcta (sin `https://`)
3. Limpia la caché del navegador (Ctrl+Shift+Delete)

---

### ❌ Problema 2: "Invalid HTTP_HOST header"

**Síntoma:** Página en blanco o error 400

**Solución:**
1. Conectarte al servidor: `ssh -i django-backend-key.pem ubuntu@98.92.49.243`
2. Verificar ALLOWED_HOSTS: `cd /var/www/django-backend && grep ALLOWED_HOSTS .env`
3. Debe incluir tu dominio de Vercel

---

### ❌ Problema 3: Variables de entorno no funcionan

**Síntoma:** La aplicación no encuentra el backend

**Solución:**
1. Ve a Vercel → Settings → Environment Variables
2. Verifica que el **nombre** de la variable sea correcto:
   - `REACT_APP_API_URL` para React
   - `NEXT_PUBLIC_API_URL` para Next.js
   - `VITE_API_URL` para Vue/Vite
3. Verifica que el **valor** sea: `http://98.92.49.243/api`
4. Haz **Redeploy** desde Deployments

---

### ❌ Problema 4: Build falla en Vercel

**Síntoma:** Error durante el despliegue

**Solución:**
1. Ve a Vercel → Deployments → Click en el deployment fallido
2. Lee el error en los logs
3. Usualmente es:
   - Falta dependencia en `package.json`
   - Error de sintaxis en el código
   - Variable de entorno faltante

4. Corrige el error localmente:
   ```bash
   npm run build  # Probar localmente
   git add .
   git commit -m "Fix build error"
   git push
   ```

---

### ❌ Problema 5: Página carga pero no hay datos

**Síntoma:** El sitio carga pero listas vacías

**Solución:**
1. Abre consola del navegador (F12)
2. Ve a pestaña **Network**
3. Recarga la página
4. Busca las peticiones a la API
5. Click en una petición y ve la respuesta
6. Si dice "CORS error", vuelve a configurar CORS (Parte 3)

---

## 📊 Información del Backend

**URL Backend:** `http://98.92.49.243`
**API Endpoints:** `http://98.92.49.243/api/`

### Datos disponibles:
- ✅ 37 productos en 10 categorías
- ✅ 65 órdenes de prueba
- ✅ 35 devoluciones
- ✅ 18 usuarios (10 clientes, 6 managers, 2 admins)
- ✅ 7 billeteras con saldo

### Credenciales de prueba:
```
Cliente:  juan_cliente / password123
Manager:  carlos_manager / manager123
Admin:    admin / admin123
```

---

## ✅ Checklist Final

Antes de considerar terminado, verifica:

- [ ] ✅ Frontend desplegado en Vercel y accesible
- [ ] ✅ Variables de entorno configuradas en Vercel
- [ ] ✅ CORS configurado en el backend (ejecutaste el script)
- [ ] ✅ Login funciona correctamente
- [ ] ✅ Lista de productos se muestra
- [ ] ✅ NO hay errores de CORS en consola
- [ ] ✅ Puedes navegar por la aplicación
- [ ] ✅ Guardaste la URL de Vercel para compartir

---

## 📱 URLs Finales

Después de completar todo:

**Frontend:** `https://tu-proyecto-abc123.vercel.app`
**Backend API:** `http://98.92.49.243/api/`
**Admin Panel:** `http://98.92.49.243/admin/`

---

## 🎉 ¡Felicitaciones!

Tu aplicación está desplegada en producción. Ahora puedes:
- ✅ Compartir la URL con otros
- ✅ Acceder desde cualquier dispositivo
- ✅ Hacer cambios y Vercel los desplegará automáticamente

---

## 📚 Recursos Adicionales

**Documentación oficial:**
- [Vercel Docs](https://vercel.com/docs)
- [Despliegue de React](https://vercel.com/guides/deploying-react-with-vercel)
- [Despliegue de Next.js](https://vercel.com/docs/frameworks/nextjs)
- [Despliegue de Vue](https://vercel.com/guides/deploying-vuejs-to-vercel)

**Ayuda:**
- [Vercel Community](https://github.com/vercel/vercel/discussions)
- [Status de Vercel](https://www.vercel-status.com/)

---

## 💡 Consejos Pro

1. **Monitoreo:** Revisa regularmente Vercel Analytics para ver el tráfico
2. **Logs:** Si algo no funciona, revisa Function Logs en Vercel
3. **Caché:** Si ves datos viejos, limpia caché del navegador
4. **Preview Deployments:** Cada push a una rama crea un preview deployment
5. **Production:** Solo la rama `main` se despliega a producción

---

**¿Necesitas ayuda?** Revisa la sección de "Solución de Problemas Comunes" arriba. 🚀
