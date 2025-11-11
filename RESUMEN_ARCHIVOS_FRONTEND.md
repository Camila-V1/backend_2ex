# 📦 Resumen de Archivos para Despliegue Frontend

## 🎯 Archivos Creados

Se han creado **5 archivos** para ayudarte a desplegar tu frontend en Vercel y conectarlo con el backend en AWS:

---

## 📄 1. GUIA_DESPLIEGUE_FRONTEND_VERCEL.md

**📋 Descripción:** Guía completa paso a paso para desplegar el frontend en Vercel.

**📝 Contenido:**
- Información del backend desplegado (IP, endpoints)
- Configuración de variables de entorno para cada framework
- Instrucciones para configurar CORS en el backend
- Preparación del código frontend
- Despliegue en Vercel (GitHub y CLI)
- Configuración de HTTPS
- Pruebas y verificación
- Solución de problemas comunes

**👥 Para quién:** Desarrolladores que van a desplegar el frontend por primera vez.

**⏱️ Tiempo estimado:** 20-30 minutos siguiendo la guía.

---

## 📄 2. frontend_config_example.js

**📋 Descripción:** Ejemplos de código para configurar la conexión con el backend.

**📝 Contenido:**
- Configuración de API para React (Create React App)
- Configuración de API para Next.js
- Configuración de API para Vue 3 + Vite
- Configuración de interceptores Axios
- Manejo de tokens JWT
- Refresh token automático
- Ejemplos de uso en componentes
- Lista completa de endpoints disponibles
- Servicio de autenticación completo

**👥 Para quién:** Desarrolladores que necesitan implementar la conexión en su código.

**⏱️ Tiempo estimado:** Copiar y adaptar código (10-15 minutos).

---

## 📄 3. VARIABLES_ENTORNO_FRONTEND.env

**📋 Descripción:** Plantilla de variables de entorno para todos los frameworks.

**📝 Contenido:**
- Variables para React (REACT_APP_*)
- Variables para Next.js (NEXT_PUBLIC_*)
- Variables para Vue/Vite (VITE_*)
- Variables para Angular
- Variables para Svelte
- Variables para Nuxt 3
- Variables para Astro
- Instrucciones para configurar en Vercel Dashboard
- Instrucciones para configurar con Vercel CLI
- Lista completa de endpoints del backend
- Credenciales de prueba
- Ejemplos de uso

**👥 Para quién:** Desarrolladores configurando variables de entorno.

**⏱️ Tiempo estimado:** 5 minutos para copiar y configurar.

---

## 📄 4. update_cors_for_vercel.ps1

**📋 Descripción:** Script de PowerShell para actualizar CORS automáticamente (Windows).

**📝 Contenido:**
- Script automático para configurar CORS en el backend
- Actualiza ALLOWED_HOSTS
- Actualiza CORS_ALLOWED_ORIGINS
- Reinicia servicios (Gunicorn y Nginx)
- Verifica estado de servicios
- Muestra resumen de cambios

**👥 Para quién:** Usuarios de Windows después de desplegar en Vercel.

**⏱️ Tiempo estimado:** 1-2 minutos de ejecución automática.

**🚀 Uso:**
```powershell
.\update_cors_for_vercel.ps1 -VercelDomain "tu-app.vercel.app"
```

---

## 📄 5. update_cors_for_vercel.sh

**📋 Descripción:** Script de Bash para actualizar CORS automáticamente (Linux/Mac).

**📝 Contenido:**
- Mismo contenido que el script PowerShell pero para Linux/Mac
- Script automático para configurar CORS
- Actualiza configuración del backend
- Reinicia servicios
- Verificación de estado

**👥 Para quién:** Usuarios de Linux/Mac después de desplegar en Vercel.

**⏱️ Tiempo estimado:** 1-2 minutos de ejecución automática.

**🚀 Uso:**
```bash
chmod +x update_cors_for_vercel.sh
./update_cors_for_vercel.sh tu-app.vercel.app
```

---

## 📄 6. CHECKLIST_DESPLIEGUE_FRONTEND.md

**📋 Descripción:** Checklist completo con todos los pasos del despliegue.

**📝 Contenido:**
- Lista de verificación paso a paso
- 6 partes organizadas:
  1. Preparación del Frontend
  2. Despliegue en Vercel
  3. Configurar Backend para CORS
  4. Pruebas y Verificación
  5. Seguridad y Optimización
  6. Post-Despliegue
- Sección de troubleshooting con problemas comunes
- Enlaces a recursos adicionales

**👥 Para quién:** Todos - usar como guía principal de referencia.

**⏱️ Tiempo estimado:** 30-45 minutos completar todo el checklist.

---

## 🎯 Flujo de Trabajo Recomendado

### Para Desplegar por Primera vez:

```
1. Lee: GUIA_DESPLIEGUE_FRONTEND_VERCEL.md
   ↓
2. Usa: CHECKLIST_DESPLIEGUE_FRONTEND.md (ve marcando cada paso)
   ↓
3. Configura código con: frontend_config_example.js
   ↓
4. Copia variables de: VARIABLES_ENTORNO_FRONTEND.env
   ↓
5. Despliega en Vercel
   ↓
6. Ejecuta: update_cors_for_vercel.ps1 (Windows)
   o update_cors_for_vercel.sh (Linux/Mac)
   ↓
7. ¡Listo! 🎉
```

---

## 📊 Información del Backend Desplegado

**URL Base:** http://98.92.49.243
**API Endpoints:** http://98.92.49.243/api/
**Admin Panel:** http://98.92.49.243/admin/

**Servidor:** AWS EC2 (t3.micro, Ubuntu 24.04)
**IP:** 98.92.49.243
**Región:** us-east-1

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

## 📚 Endpoints Principales del Backend

### Autenticación
- `POST /api/users/login/` - Login
- `POST /api/users/register/` - Registro
- `POST /api/users/token/refresh/` - Refrescar token

### Productos
- `GET /api/products/` - Listar productos (37 productos disponibles)
- `GET /api/categories/` - Listar categorías (10 categorías)

### Órdenes
- `GET /api/orders/` - Listar órdenes (65 órdenes de prueba)
- `POST /api/orders/` - Crear orden

### Devoluciones
- `GET /api/returns/` - Listar devoluciones (35 devoluciones de prueba)
- `POST /api/returns/` - Solicitar devolución
- `POST /api/returns/{id}/approve/` - Aprobar (Manager)
- `POST /api/returns/{id}/reject/` - Rechazar (Manager)

### Billeteras
- `GET /api/wallets/` - Listar billeteras (7 billeteras con saldo)
- `GET /api/wallet-transactions/` - Transacciones

---

## 🔧 Frameworks Soportados

✅ **React** (Create React App)
✅ **Next.js** (13+)
✅ **Vue 3** (+ Vite)
✅ **Angular**
✅ **Svelte** (+ Vite)
✅ **Nuxt 3**
✅ **Astro**

---

## 🎨 Variables de Entorno por Framework

| Framework | Variable | Valor |
|-----------|----------|-------|
| React | `REACT_APP_API_URL` | `http://98.92.49.243/api` |
| Next.js | `NEXT_PUBLIC_API_URL` | `http://98.92.49.243/api` |
| Vue/Vite | `VITE_API_URL` | `http://98.92.49.243/api` |
| Nuxt 3 | `NUXT_PUBLIC_API_URL` | `http://98.92.49.243/api` |
| Astro | `PUBLIC_API_URL` | `http://98.92.49.243/api` |

---

## 🚀 Despliegue Rápido

### Opción 1: Con Script (Recomendado)

**Windows:**
```powershell
# 1. Despliega en Vercel (obtienes URL)
vercel --prod

# 2. Ejecuta script con tu URL de Vercel
.\update_cors_for_vercel.ps1 -VercelDomain "tu-app-xyz.vercel.app"
```

**Linux/Mac:**
```bash
# 1. Despliega en Vercel
vercel --prod

# 2. Ejecuta script
chmod +x update_cors_for_vercel.sh
./update_cors_for_vercel.sh tu-app-xyz.vercel.app
```

### Opción 2: Manual

```powershell
# 1. Conectarse al servidor
ssh -i django-backend-key.pem ubuntu@98.92.49.243

# 2. Editar configuración
cd /var/www/django-backend
sudo nano .env

# 3. Actualizar estas líneas:
ALLOWED_HOSTS=98.92.49.243,localhost,tu-app.vercel.app
CORS_ALLOWED_ORIGINS=https://tu-app.vercel.app

# 4. Reiniciar servicios
sudo systemctl restart gunicorn nginx
```

---

## ✅ Verificación Final

Después del despliegue, verifica:

- [ ] Frontend carga en Vercel: ✅
- [ ] Login funciona: ✅
- [ ] Lista de productos se muestra: ✅
- [ ] No hay errores de CORS en consola: ✅
- [ ] Puedes crear una orden: ✅
- [ ] Tokens se guardan correctamente: ✅

---

## 🆘 Soporte

Si tienes problemas:

1. **Revisa:** `CHECKLIST_DESPLIEGUE_FRONTEND.md` - Sección Troubleshooting
2. **Consulta:** `GUIA_DESPLIEGUE_FRONTEND_VERCEL.md` - Solución de problemas
3. **Verifica logs:**
   - Vercel: Dashboard → Deployments → View Function Logs
   - Backend: `ssh` → `sudo journalctl -u gunicorn -n 50`

---

## 📝 Notas Importantes

### Seguridad
- ⚠️ El backend actualmente usa **HTTP** (no HTTPS)
- ⚠️ Vercel usa **HTTPS** automáticamente
- ⚠️ Esto puede causar errores de "Mixed Content" en algunos navegadores
- ✅ **Solución:** Configurar SSL en el backend (ver guía)

### Variables de Entorno
- ✅ Las variables con prefijos públicos (`REACT_APP_`, `NEXT_PUBLIC_`, `VITE_`) son visibles en el código del cliente
- ❌ NO expongas claves API privadas o secrets con estos prefijos
- ✅ Usa variables de servidor para datos sensibles

### Redeploy
- Si cambias variables de entorno en Vercel, debes hacer **Redeploy**
- Settings → Deployments → (tres puntos) → Redeploy

---

## 🎉 ¡Todo Listo!

Con estos archivos tienes todo lo necesario para:

✅ Configurar tu frontend
✅ Desplegarlo en Vercel
✅ Conectarlo con el backend en AWS
✅ Resolver problemas comunes
✅ Optimizar la configuración

**Tiempo total estimado:** 30-45 minutos para despliegue completo

**¡Buena suerte con tu despliegue!** 🚀
