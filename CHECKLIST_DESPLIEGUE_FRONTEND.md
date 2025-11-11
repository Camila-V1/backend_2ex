# ✅ Checklist: Despliegue Frontend en Vercel

## 📋 Lista de Verificación Completa

### 🔧 Parte 1: Preparación del Frontend (Antes de Desplegar)

- [ ] **1.1. Instalar dependencias**
  ```bash
  npm install
  # o
  yarn install
  ```

- [ ] **1.2. Crear archivo de variables de entorno**
  - [ ] Para React: Crear `.env.production` con `REACT_APP_API_URL=http://98.92.49.243/api`
  - [ ] Para Next.js: Crear `.env.production` con `NEXT_PUBLIC_API_URL=http://98.92.49.243/api`
  - [ ] Para Vue/Vite: Crear `.env.production` con `VITE_API_URL=http://98.92.49.243/api`

- [ ] **1.3. Verificar configuración de API**
  - [ ] Todas las llamadas a la API usan la variable de entorno
  - [ ] Implementado manejo de tokens JWT
  - [ ] Interceptores de Axios configurados (si aplica)
  - [ ] Manejo de errores 401 para tokens expirados

- [ ] **1.4. Probar build localmente**
  ```bash
  npm run build
  # Verificar que compile sin errores
  ```

- [ ] **1.5. Subir a GitHub** (si usas integración Git)
  ```bash
  git add .
  git commit -m "Configurar para producción"
  git push origin main
  ```

---

### 🚀 Parte 2: Despliegue en Vercel

- [ ] **2.1. Crear cuenta en Vercel**
  - [ ] Ir a [vercel.com](https://vercel.com)
  - [ ] Registrarse con GitHub/GitLab/Bitbucket o email

- [ ] **2.2. Importar proyecto**
  - [ ] Click en "Add New Project"
  - [ ] Seleccionar repositorio de GitHub (o subir manualmente)
  - [ ] Configurar Framework Preset (detecta automáticamente)

- [ ] **2.3. Configurar Build Settings**
  - [ ] **Build Command:** `npm run build` (o detectado automáticamente)
  - [ ] **Output Directory:** 
    - React: `build`
    - Next.js: `.next`
    - Vue/Vite: `dist`
  - [ ] **Install Command:** `npm install` (o detectado automáticamente)

- [ ] **2.4. Agregar Variables de Entorno en Vercel**
  - [ ] Ir a Settings → Environment Variables
  - [ ] Para React:
    - [ ] Name: `REACT_APP_API_URL`
    - [ ] Value: `http://98.92.49.243/api`
    - [ ] Environment: Production ✓, Preview ✓, Development ✓
  - [ ] Para Next.js:
    - [ ] Name: `NEXT_PUBLIC_API_URL`
    - [ ] Value: `http://98.92.49.243/api`
    - [ ] Environment: Production ✓, Preview ✓, Development ✓
  - [ ] Para Vue/Vite:
    - [ ] Name: `VITE_API_URL`
    - [ ] Value: `http://98.92.49.243/api`
    - [ ] Environment: Production ✓, Preview ✓, Development ✓

- [ ] **2.5. Iniciar despliegue**
  - [ ] Click en "Deploy"
  - [ ] Esperar a que termine el build (2-5 minutos)
  - [ ] Verificar que el despliegue sea exitoso ✅

- [ ] **2.6. Obtener URL de Vercel**
  - [ ] Copiar la URL asignada (ej: `https://mi-app-abc123.vercel.app`)

---

### 🔧 Parte 3: Configurar Backend para CORS

- [ ] **3.1. Actualizar CORS con script PowerShell**
  ```powershell
  .\update_cors_for_vercel.ps1 -VercelDomain "mi-app-abc123.vercel.app"
  ```
  
  **O manualmente:**

- [ ] **3.2. Conectarse al servidor**
  ```powershell
  ssh -i django-backend-key.pem ubuntu@98.92.49.243
  ```

- [ ] **3.3. Editar archivo .env**
  ```bash
  cd /var/www/django-backend
  sudo nano .env
  ```

- [ ] **3.4. Actualizar estas líneas:**
  ```bash
  ALLOWED_HOSTS=98.92.49.243,localhost,127.0.0.1,mi-app-abc123.vercel.app
  CORS_ALLOWED_ORIGINS=https://mi-app-abc123.vercel.app,http://localhost:3000
  CORS_ALLOW_ALL_ORIGINS=False
  ```

- [ ] **3.5. Guardar y salir** (`Ctrl+X`, `Y`, `Enter`)

- [ ] **3.6. Reiniciar servicios**
  ```bash
  sudo systemctl restart gunicorn
  sudo systemctl restart nginx
  ```

- [ ] **3.7. Verificar servicios activos**
  ```bash
  sudo systemctl status gunicorn
  sudo systemctl status nginx
  ```

---

### 🧪 Parte 4: Pruebas y Verificación

- [ ] **4.1. Probar frontend desplegado**
  - [ ] Abrir URL de Vercel en el navegador
  - [ ] Verificar que la página carga correctamente
  - [ ] Abrir DevTools → Console (F12)
  - [ ] Verificar que no hay errores en la consola

- [ ] **4.2. Probar conexión con el backend**
  - [ ] Ir a página de login
  - [ ] Intentar iniciar sesión con: `admin` / `admin123`
  - [ ] Verificar que el login funciona
  - [ ] Verificar que se guarda el token

- [ ] **4.3. Probar endpoints principales**
  - [ ] Ver lista de productos
  - [ ] Ver detalle de un producto
  - [ ] Ver órdenes (si estás logueado)
  - [ ] Crear una orden de prueba

- [ ] **4.4. Verificar en la consola del navegador**
  ```javascript
  // Probar llamada a la API
  fetch('http://98.92.49.243/api/products/')
    .then(r => r.json())
    .then(data => console.log('Productos:', data))
    .catch(err => console.error('Error:', err));
  ```

- [ ] **4.5. Verificar que NO hay errores de CORS**
  - [ ] No debe aparecer: "CORS policy: No 'Access-Control-Allow-Origin'"
  - [ ] Si aparece, verificar configuración de CORS en el backend

- [ ] **4.6. Probar funcionalidades principales**
  - [ ] Login como cliente (`juan_cliente` / `password123`)
  - [ ] Login como manager (`carlos_manager` / `manager123`)
  - [ ] Login como admin (`admin` / `admin123`)
  - [ ] Navegación entre páginas
  - [ ] Carga de imágenes (si aplica)

---

### 🔒 Parte 5: Seguridad y Optimización (Opcional)

- [ ] **5.1. Configurar dominio personalizado** (opcional)
  - [ ] En Vercel: Settings → Domains
  - [ ] Agregar tu dominio personalizado
  - [ ] Actualizar DNS según instrucciones
  - [ ] Actualizar CORS en backend con nuevo dominio

- [ ] **5.2. Configurar HTTPS en el backend** (recomendado)
  - [ ] Instalar Certbot en el servidor
  - [ ] Obtener certificado SSL gratuito
  - [ ] Actualizar variable de entorno a `https://98.92.49.243/api`

- [ ] **5.3. Optimizar configuración de Vercel**
  - [ ] Revisar Analytics en Vercel Dashboard
  - [ ] Configurar Redirects si es necesario
  - [ ] Configurar Headers personalizados

- [ ] **5.4. Monitoring y Logs**
  - [ ] Revisar logs de despliegue en Vercel
  - [ ] Configurar alertas de error (opcional)
  - [ ] Monitorear logs del backend en AWS

---

### 📊 Parte 6: Post-Despliegue

- [ ] **6.1. Documentar URLs**
  - [ ] Frontend: `https://mi-app-abc123.vercel.app`
  - [ ] Backend API: `http://98.92.49.243/api`
  - [ ] Admin Panel: `http://98.92.49.243/admin`

- [ ] **6.2. Compartir credenciales de prueba**
  ```
  Cliente: juan_cliente / password123
  Manager: carlos_manager / manager123
  Admin: admin / admin123
  ```

- [ ] **6.3. Actualizar README del proyecto**
  - [ ] Agregar URLs de producción
  - [ ] Documentar proceso de despliegue
  - [ ] Agregar instrucciones para desarrolladores

- [ ] **6.4. Crear backup de configuración**
  - [ ] Exportar variables de entorno de Vercel
  - [ ] Documentar configuración de CORS
  - [ ] Guardar logs de despliegue

---

## 🆘 Troubleshooting - Problemas Comunes

### ❌ Error: "CORS policy: No 'Access-Control-Allow-Origin'"
**Solución:**
1. Verificar que agregaste tu dominio de Vercel en `CORS_ALLOWED_ORIGINS`
2. Reiniciar Gunicorn: `sudo systemctl restart gunicorn`
3. Limpiar caché del navegador

### ❌ Error: "Invalid HTTP_HOST header"
**Solución:**
1. Agregar dominio de Vercel a `ALLOWED_HOSTS` en el backend
2. Reiniciar servicios

### ❌ Error: "Mixed Content" (contenido mixto)
**Solución:**
1. Configurar HTTPS en el backend (recomendado)
2. O agregar en `index.html`: `<meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">`

### ❌ El frontend no encuentra el backend
**Solución:**
1. Verificar variable de entorno en Vercel Dashboard
2. Hacer redeploy después de cambiar variables
3. Verificar que la variable tenga el prefijo correcto (`REACT_APP_`, `NEXT_PUBLIC_`, `VITE_`)

### ❌ Tokens no se guardan
**Solución:**
1. Verificar que usas `localStorage` o `sessionStorage`
2. Verificar que el interceptor de Axios esté configurado
3. Verificar que el backend devuelve tokens correctamente

### ❌ Build falla en Vercel
**Solución:**
1. Revisar logs de build en Vercel Dashboard
2. Verificar que `package.json` tiene scripts correctos
3. Probar build localmente: `npm run build`
4. Verificar versión de Node.js en Vercel

---

## 📞 Soporte

**Backend desplegado en:** AWS EC2 (98.92.49.243)
**Frontend desplegado en:** Vercel

**Documentación adicional:**
- `GUIA_DESPLIEGUE_FRONTEND_VERCEL.md` - Guía detallada completa
- `frontend_config_example.js` - Ejemplos de configuración
- `VARIABLES_ENTORNO_FRONTEND.env` - Variables de entorno

**Scripts útiles:**
- `update_cors_for_vercel.ps1` - Actualizar CORS automáticamente (Windows)
- `update_cors_for_vercel.sh` - Actualizar CORS automáticamente (Linux/Mac)

---

## ✅ Resumen Final

Una vez completado todo el checklist:

✅ Frontend desplegado en Vercel
✅ Variables de entorno configuradas
✅ CORS configurado en el backend
✅ Conexión frontend-backend funcionando
✅ Login y autenticación operativos
✅ Todas las funcionalidades probadas

🎉 **¡Tu aplicación está en producción!**
