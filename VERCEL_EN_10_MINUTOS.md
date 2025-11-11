# 🎯 Guía Visual Rápida: Vercel en 10 Minutos

## ⏱️ Tiempo Total: 10-15 minutos

---

## 📦 LO QUE NECESITAS ANTES DE EMPEZAR

```
✅ Tu proyecto frontend en tu computadora
✅ Cuenta de GitHub
✅ Backend funcionando: http://98.92.49.243
```

---

## 🚀 PASO 1: Preparar tu Proyecto (3 minutos)

### 1.1 Crear archivo `.env.production`

En la **raíz** de tu proyecto frontend, crea este archivo:

```
📁 mi-proyecto-frontend/
├── 📄 package.json
├── 📄 .env.production  ← CREAR ESTE ARCHIVO
├── 📁 src/
└── 📁 public/
```

**Contenido del archivo según tu framework:**

| Framework | Contenido |
|-----------|-----------|
| **React** | `REACT_APP_API_URL=http://98.92.49.243/api` |
| **Next.js** | `NEXT_PUBLIC_API_URL=http://98.92.49.243/api` |
| **Vue/Vite** | `VITE_API_URL=http://98.92.49.243/api` |

---

### 1.2 Subir a GitHub

```bash
# Abre terminal en tu carpeta del frontend
git init
git add .
git commit -m "Configurar para producción"

# Crea un repositorio en GitHub.com y luego:
git remote add origin https://github.com/TU-USUARIO/TU-REPO.git
git push -u origin main
```

**✅ Listo, continúa al Paso 2**

---

## 🌐 PASO 2: Crear Cuenta en Vercel (2 minutos)

### 2.1 Ir a Vercel

Abre tu navegador: **https://vercel.com**

---

### 2.2 Registrarse

```
┌─────────────────────────────────────┐
│         Vercel                      │
│                                     │
│   [Continue with GitHub]  ← CLICK  │
│                                     │
│   [Continue with GitLab]           │
│   [Continue with Bitbucket]        │
└─────────────────────────────────────┘
```

Autoriza a Vercel en GitHub cuando te lo pida.

**✅ Ahora estás en el Dashboard de Vercel**

---

## 📂 PASO 3: Importar Proyecto (3 minutos)

### 3.1 Agregar Nuevo Proyecto

```
Dashboard de Vercel:
┌────────────────────────────────────────┐
│  [Add New...] ▼  ← CLICK AQUÍ        │
│    └─ Project    ← SELECCIONA ESTO    │
└────────────────────────────────────────┘
```

---

### 3.2 Seleccionar Repositorio

Verás una lista de tus repos de GitHub:

```
Import Git Repository
┌────────────────────────────────────────┐
│ 🔍 Search...                          │
│                                        │
│ ✓ Camila-V1/mi-proyecto-frontend      │
│   [Import] ← CLICK                    │
│                                        │
│ ✓ Camila-V1/otro-proyecto             │
│   [Import]                            │
└────────────────────────────────────────┘
```

**✅ Click en [Import] de tu proyecto frontend**

---

### 3.3 Configurar Build (Automático)

Vercel detecta automáticamente todo:

```
Configure Project
┌────────────────────────────────────────┐
│ Framework Preset                       │
│ ✓ Create React App (detected) ✓       │
│                                        │
│ Build Command                          │
│ npm run build ✓                        │
│                                        │
│ Output Directory                       │
│ build ✓                                │
└────────────────────────────────────────┘

⚠️ NO CAMBIES NADA - Ya está bien configurado
```

---

### 3.4 Agregar Variables de Entorno

**🔴 IMPORTANTE - No te saltes esto:**

Baja hasta ver "Environment Variables":

```
Environment Variables
┌────────────────────────────────────────┐
│ Name                                   │
│ [____________________________]         │
│                                        │
│ Value                                  │
│ [____________________________]         │
│                                        │
│ Environment                            │
│ ☑️ Production                          │
│ ☑️ Preview                             │
│ ☑️ Development                         │
│                                        │
│ [Add] ← CLICK después de llenar       │
└────────────────────────────────────────┘
```

**Llena según tu framework:**

**Para React:**
- Name: `REACT_APP_API_URL`
- Value: `http://98.92.49.243/api`
- Marca las 3 casillas ☑️

**Para Next.js:**
- Name: `NEXT_PUBLIC_API_URL`
- Value: `http://98.92.49.243/api`
- Marca las 3 casillas ☑️

**Para Vue/Vite:**
- Name: `VITE_API_URL`
- Value: `http://98.92.49.243/api`
- Marca las 3 casillas ☑️

**✅ Click en [Add] para guardar**

---

### 3.5 Desplegar

```
┌────────────────────────────────────────┐
│                                        │
│         [Deploy] ← CLICK AQUÍ         │
│                                        │
└────────────────────────────────────────┘
```

**Espera 2-5 minutos...**

```
Building...
████████████████░░░░░░░░░░░░░░ 60%

Instalando dependencias...
Construyendo aplicación...
Optimizando assets...
```

**✅ Cuando veas "Congratulations!", copia tu URL:**

```
┌────────────────────────────────────────┐
│  🎉 Congratulations!                   │
│                                        │
│  https://mi-proyecto-abc123.vercel.app │
│  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^│
│          COPIA ESTA URL                │
└────────────────────────────────────────┘
```

**📝 URL copiada: `mi-proyecto-abc123.vercel.app`**
(sin `https://`)

---

## 🔧 PASO 4: Configurar CORS (2 minutos)

### 4.1 Ejecutar Script

Abre **PowerShell** en la carpeta `backend_2ex`:

```powershell
.\update_cors_for_vercel.ps1 -VercelDomain "mi-proyecto-abc123.vercel.app"
```

**⚠️ Reemplaza `mi-proyecto-abc123.vercel.app` con TU URL real**

**Ejemplo real:**
```powershell
.\update_cors_for_vercel.ps1 -VercelDomain "ecommerce-frontend-xyz789.vercel.app"
```

**Verás algo como:**

```
============================================================================
  Actualización de CORS para Frontend en Vercel
============================================================================

📝 Configuración:
  • Dominio Vercel: https://mi-proyecto-abc123.vercel.app
  • Servidor Backend: 98.92.49.243

🔄 Conectando al servidor...
   ✓ ALLOWED_HOSTS actualizado
   ✓ CORS_ALLOWED_ORIGINS actualizado

🔄 Reiniciando servicios...
   ✓ Gunicorn reiniciado
   ✓ Nginx reiniciado

✅ CONFIGURACIÓN COMPLETADA
```

**✅ ¡Listo!**

---

## 🧪 PASO 5: Probar (2 minutos)

### 5.1 Abrir tu Aplicación

En tu navegador:
```
https://mi-proyecto-abc123.vercel.app
```

---

### 5.2 Abrir Consola del Navegador

Presiona **F12** o **Ctrl+Shift+I**

```
┌─────────────────────────────────────┐
│ Elements  Console  Network  ...    │ ← Click en Console
├─────────────────────────────────────┤
│ [No hay errores rojos] ✅           │
│                                     │
│ ⚠️ Warning: ... (amarillo) OK      │
└─────────────────────────────────────┘
```

**✅ Si NO hay errores rojos de CORS, está bien**

**❌ Si ves error de CORS:**
```
❌ CORS policy: No 'Access-Control-Allow-Origin'
```
→ Vuelve al Paso 4 y ejecuta el script nuevamente

---

### 5.3 Probar Login

Usa estas credenciales de prueba:

```
👤 Admin:
   Username: admin
   Password: admin123

👤 Cliente:
   Username: juan_cliente
   Password: password123
```

**✅ Si el login funciona, ¡todo está perfecto!**

---

## 🎉 ¡TERMINASTE!

```
┌─────────────────────────────────────────┐
│                                         │
│   ✅ Tu aplicación está en PRODUCCIÓN  │
│                                         │
│   🌐 URL: https://tu-app.vercel.app    │
│                                         │
│   📊 Backend: http://98.92.49.243      │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🔄 Actualizaciones Futuras

Cuando hagas cambios:

```bash
# 1. Edita tu código
# 2. Haz commit y push
git add .
git commit -m "Nueva funcionalidad"
git push

# 3. Vercel automáticamente despliega ✨
# ¡No necesitas hacer nada más!
```

---

## ❌ Solución Rápida de Errores

### Error de CORS

```
❌ CORS policy: No 'Access-Control-Allow-Origin'
```

**Solución:**
```powershell
.\update_cors_for_vercel.ps1 -VercelDomain "tu-url.vercel.app"
```

---

### Variable de Entorno no Funciona

```
❌ API no encontrada / undefined
```

**Solución:**

1. Ve a Vercel → Settings → Environment Variables
2. Verifica el nombre:
   - ✅ `REACT_APP_API_URL` para React
   - ✅ `NEXT_PUBLIC_API_URL` para Next.js
   - ✅ `VITE_API_URL` para Vue/Vite
3. Verifica el valor: `http://98.92.49.243/api`
4. Ve a Deployments → ... → Redeploy

---

### Build Falla

```
❌ Error durante build
```

**Solución:**

1. Prueba localmente:
   ```bash
   npm install
   npm run build
   ```
2. Si funciona local, revisa logs en Vercel
3. Busca el error específico y corrígelo
4. Push de nuevo a GitHub

---

## 📊 Datos del Sistema

**Backend:** `http://98.92.49.243`

**Datos disponibles:**
- ✅ 37 productos
- ✅ 65 órdenes
- ✅ 35 devoluciones
- ✅ 18 usuarios

**Credenciales:**
```
Cliente:  juan_cliente / password123
Manager:  carlos_manager / manager123
Admin:    admin / admin123
```

---

## 📚 Archivos de Ayuda Creados

Si necesitas más información:

1. **`GUIA_PASO_A_PASO_VERCEL.md`** ← Guía detallada
2. **`CHECKLIST_DESPLIEGUE_FRONTEND.md`** ← Checklist completo
3. **`frontend_config_example.js`** ← Ejemplos de código
4. **`VARIABLES_ENTORNO_FRONTEND.env`** ← Variables para todos los frameworks

---

## ✅ Checklist Final

- [ ] ✅ Creé `.env.production` en mi proyecto
- [ ] ✅ Subí mi proyecto a GitHub
- [ ] ✅ Creé cuenta en Vercel con GitHub
- [ ] ✅ Importé mi repositorio en Vercel
- [ ] ✅ Agregué variable de entorno en Vercel
- [ ] ✅ Desplegué el proyecto (botón Deploy)
- [ ] ✅ Copié mi URL de Vercel
- [ ] ✅ Ejecuté script de CORS
- [ ] ✅ Probé login y no hay errores

---

## 🎯 URLs Finales

**Frontend:** `https://tu-proyecto.vercel.app`
**Backend API:** `http://98.92.49.243/api/`
**Admin:** `http://98.92.49.243/admin/`

---

**¡Felicitaciones! Tu app está en línea 🚀**
