# 🔄 REDESPLIEGUE RÁPIDO - Aplicar Cambios Recientes

## 📌 Información del Servidor
- **IP EC2**: 3.88.180.221
- **RDS**: django-db.cormkuccww82.us-east-1.rds.amazonaws.com
- **S3**: django-backend-static-3193

---

## 🚀 PASOS PARA REDESPLEGAR

### 1️⃣ Conectarse al servidor EC2

**Desde PowerShell:**
```powershell
cd "c:\Users\asus\Documents\SISTEMAS DE INFORMACION 2\segundo examen SI2\backend_2ex"

# Si usas Git Bash (chmod 400 django-backend-key.pem)
# Para PowerShell, la clave ya funciona directamente

ssh -i django-backend-key.pem ubuntu@3.88.180.221
```

**Si pregunta "Are you sure..."**: Escribe `yes` y presiona Enter

---

### 2️⃣ Una vez dentro del servidor, ejecuta estos comandos:

```bash
# Ir al directorio del proyecto
cd /var/www/django-backend

# Descargar los últimos cambios de GitHub
git pull origin main

# Activar entorno virtual
source venv/bin/activate

# Instalar/actualizar dependencias
pip install -r requirements.txt

# Aplicar migraciones (si hay nuevas)
python manage.py makemigrations
python manage.py migrate

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Reiniciar Gunicorn (servidor de aplicación)
sudo systemctl restart gunicorn

# Reiniciar Nginx (servidor web)
sudo systemctl restart nginx

# Verificar que todo está funcionando
sudo systemctl status gunicorn
sudo systemctl status nginx
```

---

### 3️⃣ Verificar que el despliegue fue exitoso

**Comprobar logs de Gunicorn:**
```bash
sudo journalctl -u gunicorn -n 50 --no-pager
```

**Comprobar logs de Nginx:**
```bash
sudo tail -f /var/log/nginx/error.log
```

**Probar endpoint:**
```bash
curl http://localhost:8000/api/products/
```

---

### 4️⃣ (OPCIONAL) Poblar base de datos con datos de prueba

Si quieres agregar los 65 pedidos + 35 devoluciones:

```bash
# Dentro del servidor EC2, con entorno virtual activado
python seed_complete_database.py
```

Esto creará:
- 📦 18 usuarios (10 clientes, 6 managers, 2 admins)
- 🛍️ 37 productos en 5 categorías
- 📋 65 órdenes en diferentes estados
- 🔄 35 devoluciones con todos los estados posibles
- 💰 7 billeteras con saldo

---

## 🧪 VERIFICACIÓN POST-DESPLIEGUE

### Desde tu PC local (PowerShell):

```powershell
# Probar productos
curl http://3.88.180.221/api/products/

# Probar login
curl -X POST http://3.88.180.221/api/users/login/ `
  -H "Content-Type: application/json" `
  -d '{"username": "juan_cliente", "password": "password123"}'

# Probar categorías
curl http://3.88.180.221/api/categories/
```

### Desde el navegador:

1. **API Root**: http://3.88.180.221/api/
2. **Django Admin**: http://3.88.180.221/admin/
   - Usuario: `admin`
   - Contraseña: `admin123`

---

## ⚠️ SI ALGO FALLA

### Problema: Gunicorn no arranca
```bash
# Ver logs completos
sudo journalctl -u gunicorn -n 100 --no-pager

# Reintentar
sudo systemctl restart gunicorn
```

### Problema: Error 502 Bad Gateway
```bash
# Verificar que Gunicorn está corriendo
sudo systemctl status gunicorn

# Si no está corriendo, revisar configuración
sudo nano /etc/systemd/system/gunicorn.service

# Recargar configuración
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
```

### Problema: No se conecta a la base de datos
```bash
# Verificar variables de entorno
cat /var/www/django-backend/.env

# Probar conexión a RDS
psql -h django-db.cormkuccww82.us-east-1.rds.amazonaws.com -U postgres -d ecommerce_db
```

### Problema: Cambios no se reflejan
```bash
# Limpiar caché de Python
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Reiniciar todo
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

## 📊 MONITOREO EN TIEMPO REAL

```bash
# Ver logs de Gunicorn en vivo
sudo journalctl -u gunicorn -f

# Ver logs de Nginx en vivo
sudo tail -f /var/log/nginx/access.log

# Ver uso de recursos
htop  # (si está instalado)
# o
top
```

---

## 🎯 RESUMEN RÁPIDO (Solo comandos)

**SSH al servidor:**
```bash
ssh -i django-backend-key.pem ubuntu@3.88.180.221
```

**Actualizar y reiniciar:**
```bash
cd /var/www/django-backend && \
git pull origin main && \
source venv/bin/activate && \
pip install -r requirements.txt && \
python manage.py migrate && \
python manage.py collectstatic --noinput && \
sudo systemctl restart gunicorn && \
sudo systemctl restart nginx && \
echo "✅ Redespliegue completado"
```

**Verificar:**
```bash
sudo systemctl status gunicorn nginx
```

---

## 📚 Cambios que se aplicarán

Los siguientes archivos/cambios se actualizarán desde tu repositorio GitHub:

1. ✅ `seed_complete_database.py` - Seeder mejorado con 65 órdenes + 35 devoluciones
2. ✅ `CREDENCIALES_SISTEMA.md` - Documentación de credenciales
3. ✅ `FUNCIONALIDADES_POR_ROL.md` - Documentación de funcionalidades
4. ✅ `GUIA_DESPLIEGUE_COMPLETA.md` - Guía maestra de despliegue
5. ✅ Cualquier otro cambio en el código fuente

**Nota**: La base de datos NO se eliminará. Solo se aplicarán nuevas migraciones si las hay.

---

## 🔐 Credenciales de Prueba

Una vez desplegado, puedes usar estas credenciales:

### CLIENTE
- Usuario: `juan_cliente`
- Contraseña: `password123`

### MANAGER
- Usuario: `carlos_manager`
- Contraseña: `manager123`

### ADMIN
- Usuario: `admin`
- Contraseña: `admin123`

---

**Última actualización**: 10 de noviembre de 2025  
**Tiempo estimado**: 5-10 minutos  
**Documentación completa**: `GUIA_DESPLIEGUE_COMPLETA.md`
