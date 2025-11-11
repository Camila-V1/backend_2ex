# 📋 Cheat Sheet: Vercel - Comandos y Referencia Rápida

## 🎯 Configuración Inicial

### Variables de Entorno por Framework

```env
# React (Create React App)
REACT_APP_API_URL=http://98.92.49.243/api

# Next.js
NEXT_PUBLIC_API_URL=http://98.92.49.243/api

# Vue + Vite
VITE_API_URL=http://98.92.49.243/api

# Nuxt 3
NUXT_PUBLIC_API_URL=http://98.92.49.243/api

# Astro
PUBLIC_API_URL=http://98.92.49.243/api
```

---

## 🚀 Comandos Rápidos

### Despliegue

```bash
# Primera vez (instalar CLI)
npm install -g vercel

# Login
vercel login

# Desplegar a preview
vercel

# Desplegar a producción
vercel --prod

# Desplegar con build específico
vercel --prod --build-env NODE_ENV=production
```

---

### Variables de Entorno (CLI)

```bash
# Agregar variable
vercel env add REACT_APP_API_URL
# Luego ingresar valor: http://98.92.49.243/api
# Seleccionar: Production

# Listar variables
vercel env ls

# Remover variable
vercel env rm REACT_APP_API_URL production

# Pull variables al local
vercel env pull
```

---

### Proyectos

```bash
# Listar proyectos
vercel list

# Ver información del proyecto
vercel inspect

# Remover proyecto
vercel remove mi-proyecto
```

---

### Logs

```bash
# Ver logs en tiempo real
vercel logs

# Ver logs de deployment específico
vercel logs [deployment-url]

# Ver logs de función específica
vercel logs --filter=api/hello
```

---

## 🔧 Configuración Backend (CORS)

### Script PowerShell (Windows)

```powershell
# Actualizar CORS automáticamente
.\update_cors_for_vercel.ps1 -VercelDomain "tu-app.vercel.app"

# Ejemplo
.\update_cors_for_vercel.ps1 -VercelDomain "ecommerce-xyz.vercel.app"
```

---

### Configuración Manual

```bash
# 1. Conectar al servidor
ssh -i django-backend-key.pem ubuntu@98.92.49.243

# 2. Editar .env
cd /var/www/django-backend
sudo nano .env

# 3. Actualizar estas líneas:
ALLOWED_HOSTS=98.92.49.243,localhost,tu-app.vercel.app
CORS_ALLOWED_ORIGINS=https://tu-app.vercel.app,http://localhost:3000
CORS_ALLOW_ALL_ORIGINS=False

# 4. Reiniciar servicios
sudo systemctl restart gunicorn nginx

# 5. Salir
exit
```

---

## 🌐 URLs y Endpoints

### URLs del Sistema

```
Frontend:    https://tu-proyecto.vercel.app
Backend:     http://98.92.49.243
API:         http://98.92.49.243/api/
Admin:       http://98.92.49.243/admin/
```

---

### Endpoints API Principales

```
POST   /api/users/login/              # Login
POST   /api/users/register/           # Registro
POST   /api/users/token/refresh/      # Refresh token

GET    /api/products/                 # Listar productos
GET    /api/products/{id}/            # Detalle producto
GET    /api/categories/               # Categorías

GET    /api/orders/                   # Listar órdenes
POST   /api/orders/                   # Crear orden
GET    /api/orders/{id}/              # Detalle orden

GET    /api/returns/                  # Listar devoluciones
POST   /api/returns/                  # Solicitar devolución
POST   /api/returns/{id}/approve/     # Aprobar (Manager)
POST   /api/returns/{id}/reject/      # Rechazar (Manager)

GET    /api/wallets/                  # Billeteras
GET    /api/wallet-transactions/      # Transacciones
```

---

## 🔑 Credenciales de Prueba

```
👤 Cliente:
   Username: juan_cliente
   Password: password123

👔 Manager:
   Username: carlos_manager
   Password: manager123

⚙️ Admin:
   Username: admin
   Password: admin123
```

---

## 🧪 Testing Rápido

### En Consola del Navegador (F12)

```javascript
// Test de conexión al backend
fetch('http://98.92.49.243/api/products/')
  .then(r => r.json())
  .then(data => console.log('✅ Productos:', data))
  .catch(err => console.error('❌ Error:', err));

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
  .then(data => console.log('✅ Login:', data))
  .catch(err => console.error('❌ Error:', err));
```

---

### Desde PowerShell

```powershell
# Test API
$response = Invoke-WebRequest -Uri "http://98.92.49.243/api/products/" -UseBasicParsing
$response.Content | ConvertFrom-Json | Select-Object -First 3

# Test con autenticación
$headers = @{
    "Content-Type" = "application/json"
}
$body = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://98.92.49.243/api/users/login/" `
    -Method POST `
    -Headers $headers `
    -Body $body
```

---

## 📦 Archivos Importantes

### package.json - Scripts Necesarios

```json
{
  "scripts": {
    "dev": "vite",           // o "react-scripts start"
    "build": "vite build",   // o "react-scripts build"
    "preview": "vite preview"
  }
}
```

---

### vercel.json - Configuración Opcional

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "s-maxage=0" }
      ]
    }
  ]
}
```

---

## 🔄 Workflow de Desarrollo

### Desarrollo Local → Producción

```bash
# 1. Desarrollo local
npm run dev

# 2. Probar build
npm run build

# 3. Commit cambios
git add .
git commit -m "Feature: nueva funcionalidad"

# 4. Push a GitHub
git push origin main

# 5. Vercel despliega automáticamente ✨
```

---

### Con Branches

```bash
# 1. Crear rama
git checkout -b feature/nueva-funcionalidad

# 2. Hacer cambios y commit
git add .
git commit -m "Add nueva funcionalidad"

# 3. Push de la rama
git push origin feature/nueva-funcionalidad

# 4. Vercel crea un Preview Deployment automáticamente
#    URL: https://tu-proyecto-git-feature-nueva-fun-user.vercel.app

# 5. Cuando esté listo, merge a main
git checkout main
git merge feature/nueva-funcionalidad
git push origin main

# 6. Vercel despliega a producción ✨
```

---

## ❌ Errores Comunes y Soluciones

### Error de CORS

```
❌ CORS policy: No 'Access-Control-Allow-Origin' header
```

**Solución:**
```powershell
.\update_cors_for_vercel.ps1 -VercelDomain "tu-app.vercel.app"
```

---

### Variable de Entorno No Funciona

```
❌ process.env.REACT_APP_API_URL is undefined
```

**Solución:**
1. Vercel Dashboard → Settings → Environment Variables
2. Verificar nombre correcto (`REACT_APP_*`, `NEXT_PUBLIC_*`, `VITE_*`)
3. Verificar valor: `http://98.92.49.243/api`
4. Deployments → Redeploy

---

### Build Falla

```
❌ Command "npm run build" exited with 1
```

**Solución:**
1. Local: `npm run build` (probar)
2. Ver logs de error en Vercel
3. Común: Dependencias faltantes en `package.json`
4. Fix → commit → push

---

### 404 Not Found en Rutas

```
❌ Refreshing page shows 404
```

**Solución:** Crear `vercel.json`:
```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/" }]
}
```

---

## 🎛️ Settings en Vercel Dashboard

### General

- **Project Name:** Cambiar nombre del proyecto
- **Root Directory:** Cambiar si frontend está en subdirectorio
- **Build & Output Settings:** Framework, build command, output directory

---

### Domains

- **Production Domain:** `tu-proyecto.vercel.app`
- **Add Domain:** Agregar dominio personalizado
- **Redirect:** Redirigir dominio antiguo a nuevo

---

### Environment Variables

- **Add New:** Agregar variable
- **Environments:** Production, Preview, Development
- **Edit/Delete:** Modificar o eliminar variables existentes

---

### Git

- **Connected Git Repository:** Ver repo conectado
- **Production Branch:** Cambiar rama de producción (default: main)
- **Ignored Build Step:** Configurar cuando NO hacer build

---

### Deployments

- **View:** Ver todos los deployments
- **Redeploy:** Volver a desplegar un deployment anterior
- **Promote to Production:** Promover preview a producción
- **Delete:** Eliminar deployment

---

## 📊 Monitoring

### Analytics

```
Vercel Dashboard → Analytics

- Page Views
- Visitors
- Top Pages
- Top Referrers
- Devices
- Browsers
```

---

### Logs

```
Vercel Dashboard → Deployment → View Function Logs

- Runtime Logs
- Build Logs
- Error Logs
```

---

## 🔐 Seguridad

### Variables Sensibles

```bash
# ✅ CORRECTO - Variables del servidor (Next.js)
DB_PASSWORD=secret123           # NO expuesto al cliente

# ❌ INCORRECTO - Variables públicas
NEXT_PUBLIC_DB_PASSWORD=secret  # EXPUESTO en el bundle
```

---

### HTTPS

```
✅ Vercel proporciona HTTPS automáticamente
✅ Certificado SSL gratuito
✅ Renovación automática
```

---

## 🚀 Performance

### Edge Functions

```javascript
// api/hello.js
export const config = {
  runtime: 'edge', // Ejecutar en Edge
};

export default function handler(req) {
  return new Response('Hello from the Edge!');
}
```

---

### ISR (Next.js)

```javascript
// pages/products.js
export async function getStaticProps() {
  return {
    props: { products },
    revalidate: 60, // Revalidar cada 60 segundos
  };
}
```

---

## 📱 Preview Deployments

```
Cada push a cualquier rama crea un preview:

main → https://tu-proyecto.vercel.app (producción)
feature/login → https://tu-proyecto-git-feature-login.vercel.app (preview)
develop → https://tu-proyecto-git-develop.vercel.app (preview)
```

---

## 🎨 Personalización

### Dominio Personalizado

```
1. Vercel → Settings → Domains → Add
2. Ingresar: www.mitienda.com
3. Configurar DNS según instrucciones Vercel
4. Actualizar CORS:
   .\update_cors_for_vercel.ps1 -VercelDomain "www.mitienda.com"
```

---

### Redirects

```json
// vercel.json
{
  "redirects": [
    {
      "source": "/old-page",
      "destination": "/new-page",
      "permanent": true
    }
  ]
}
```

---

## 📞 Soporte

### Documentación Oficial

- **Vercel Docs:** https://vercel.com/docs
- **Guides:** https://vercel.com/guides
- **Templates:** https://vercel.com/templates

---

### Community

- **GitHub Discussions:** https://github.com/vercel/vercel/discussions
- **Twitter:** @vercel
- **Discord:** discord.gg/vercel

---

## ✅ Quick Checklist

```
□ Crear .env.production
□ Subir a GitHub
□ Crear cuenta Vercel
□ Importar proyecto
□ Agregar variables de entorno
□ Deploy
□ Ejecutar script CORS
□ Probar login
□ Verificar consola (sin errores)
```

---

## 🎯 Enlaces Útiles

```
Dashboard:    https://vercel.com/dashboard
CLI Docs:     https://vercel.com/docs/cli
Status:       https://www.vercel-status.com
Blog:         https://vercel.com/blog
```

---

**Última actualización:** 11 de noviembre, 2025
**Backend:** http://98.92.49.243
**Documentación completa:** `GUIA_PASO_A_PASO_VERCEL.md`
