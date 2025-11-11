# ✅ DESPLIEGUE AWS COMPLETADO - RESUMEN FINAL

## 🎉 Infraestructura Creada Exitosamente

### ✅ Recursos AWS Activos

| Recurso | Estado | Detalles |
|---------|--------|----------|
| **EC2 Instance** | ✅ Running | IP: `3.88.180.221`, Tipo: `t3.micro` |
| **RDS PostgreSQL** | ✅ Available | Endpoint: `django-db.cormkuccww82.us-east-1.rds.amazonaws.com` |
| **S3 Bucket** | ✅ Available | Nombre: `django-backend-static-3193` |
| **Security Group** | ✅ Configured | Puertos: 22, 80, 443, 8000 |
| **SSH Key Pair** | ✅ Created | Archivo: `django-backend-key.pem` |

---

## ✅ RESUMEN DEL NUEVO DESPLIEGUE - ACTUALIZADO

## 🆕 NUEVO SERVIDOR DESPLEGADO (11 Nov 2025)

### 🖥️ Instancia EC2 Nueva
- **Instance ID**: i-0f5db5c1b5eae1b80
- **IP Pública**: **98.92.49.243** ⭐ (USAR ESTA)
- **IP Antigua**: ~~3.88.180.221~~ (Terminada)
- **Estado**: Despliegue en progreso
- **Key Name**: django-backend-key ✅ (Funcional)

---

# 📋 RESUMEN DEL DESPLIEGUE EN AWS

### Opción 1: Usar Cliente SSH (Git Bash o PowerShell con OpenSSH)

#### 1️⃣ Conectarse al servidor EC2
```bash
ssh -i django-backend-key.pem ubuntu@3.88.180.221
```

**Nota**: Si aparece un error de permisos en Windows, ejecuta:
```powershell
# En PowerShell
icacls django-backend-key.pem /inheritance:r
icacls django-backend-key.pem /grant:r "$($env:USERNAME):(R)"
```

#### 2️⃣ Dentro del servidor, descargar el script de despliegue
```bash
# Descargar el script desde tu repositorio
wget https://raw.githubusercontent.com/Camila-V1/backend_2ex/main/deploy_commands.sh

# O copiarlo manualmente (desde otra terminal local):
# scp -i django-backend-key.pem deploy_commands.sh ubuntu@3.88.180.221:~/
```

#### 3️⃣ Ejecutar el script de despliegue
```bash
chmod +x deploy_commands.sh
./deploy_commands.sh
```

El script automáticamente:
- ✅ Instalará todas las dependencias (Python, Nginx, PostgreSQL client, Redis)
- ✅ Clonará tu repositorio desde GitHub
- ✅ Creará el entorno virtual de Python
- ✅ Instalará los paquetes de Python
- ✅ Configurará las variables de entorno
- ✅ Creará la base de datos en RDS
- ✅ Ejecutará las migraciones
- ✅ Creará el superusuario (admin/admin123)
- ✅ Configurará Gunicorn
- ✅ Configurará Nginx
- ✅ Iniciará todos los servicios

**Tiempo estimado**: 10-15 minutos

---

### Opción 2: Usar PuTTY (Si no tienes Git Bash)

#### 1️⃣ Convertir la clave .pem a .ppk
1. Descargar **PuTTYgen** desde: https://www.putty.org/
2. Abrir PuTTYgen
3. Click en "Load" y seleccionar `django-backend-key.pem`
4. Click en "Save private key" y guardar como `django-backend-key.ppk`

#### 2️⃣ Conectarse con PuTTY
1. Abrir **PuTTY**
2. En "Host Name": `ubuntu@3.88.180.221`
3. En el menú izquierdo: Connection → SSH → Auth → Credentials
4. En "Private key file": Buscar `django-backend-key.ppk`
5. Click "Open"

#### 3️⃣ Copiar el script de despliegue
Usar **WinSCP** o **FileZilla** para copiar `deploy_commands.sh` al servidor.

O simplemente ejecutar comandos manualmente (ver CONFIGURACION_SERVIDOR.md)

---

## 🌐 URLs de la Aplicación

Una vez completado el despliegue:

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **API Backend** | http://3.88.180.221/api/ | - |
| **Admin Django** | http://3.88.180.221/admin/ | admin / admin123 |
| **API Docs** | http://3.88.180.221/api/schema/ | - |
| **Health Check** | http://3.88.180.221/api/health/ | - |

---

## 🔐 Credenciales Importantes

### AWS Console
- **URL**: https://487692780331.signin.aws.amazon.com/console
- **Usuario**: isael2ex
- **Contraseña**: isaelOrtiz2

### AWS CLI (Ya configurado)
- **Access Key ID**: YOUR_AWS_ACCESS_KEY_HERE
- **Secret Access Key**: YOUR_AWS_SECRET_KEY_HERE
- **Región**: us-east-1

### RDS PostgreSQL
- **Endpoint**: django-db.cormkuccww82.us-east-1.rds.amazonaws.com
- **Puerto**: 5432
- **Usuario**: dbadmin
- **Contraseña**: Django2024Secure!
- **Base de datos**: django_db

### Django Admin (Después del despliegue)
- **Usuario**: admin
- **Contraseña**: admin123
- **⚠️ IMPORTANTE**: Cambiar esta contraseña inmediatamente después del primer login

### EC2 SSH Access
- **IP**: 3.88.180.221
- **Usuario**: ubuntu
- **Key**: django-backend-key.pem

---

## 📊 Verificación del Despliegue

### Después de ejecutar el script, verificar:

#### 1️⃣ Estado de los servicios
```bash
sudo systemctl status nginx
sudo systemctl status gunicorn
sudo systemctl status redis-server
```

#### 2️⃣ Logs de la aplicación
```bash
# Logs de Gunicorn
sudo journalctl -u gunicorn -n 50 --no-pager

# Logs de Nginx
sudo tail -n 50 /var/log/nginx/error.log
```

#### 3️⃣ Probar la API desde el servidor
```bash
curl http://localhost/api/
curl http://localhost/admin/
```

#### 4️⃣ Probar desde tu computadora local
```bash
# En PowerShell local
Invoke-WebRequest http://3.88.180.221/api/
```

O abrir en el navegador: http://3.88.180.221/api/

---

## 🛠️ Comandos Útiles

### Ver logs en tiempo real
```bash
# Gunicorn
sudo journalctl -u gunicorn -f

# Nginx
sudo tail -f /var/log/nginx/error.log
```

### Reiniciar servicios
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Actualizar código desde GitHub
```bash
cd /var/www/django-backend
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

### Acceder a la base de datos RDS
```bash
PGPASSWORD=Django2024Secure! psql -h django-db.cormkuccww82.us-east-1.rds.amazonaws.com -U dbadmin -d django_db
```

---

## 💰 Costos Estimados

| Recurso | Costo con Free Tier (Primer año) | Costo después |
|---------|-----------------------------------|---------------|
| EC2 t3.micro | $0 (750 horas/mes gratis) | ~$8.50/mes |
| RDS db.t3.micro | $0 (750 horas/mes gratis) | ~$15/mes |
| S3 | $0.12/mes (5GB almacenamiento) | $0.12/mes |
| Transferencia | $0 (1GB salida gratis/mes) | Variable |
| **TOTAL** | **~$0.12/mes** | **~$24/mes** |

### Monitorear costos
1. AWS Console → Billing Dashboard
2. URL: https://console.aws.amazon.com/billing/
3. Revisar: "Cost Explorer" y "Free Tier Usage"

---

## ⚠️ Seguridad Post-Despliegue

### Tareas inmediatas después del primer despliegue:

#### 1️⃣ Cambiar contraseñas
```bash
# En el servidor EC2, conectado vía SSH
cd /var/www/django-backend
source venv/bin/activate
python manage.py changepassword admin
```

#### 2️⃣ Configurar HTTPS con Let's Encrypt (Opcional pero recomendado)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

#### 3️⃣ Restringir acceso SSH (Opcional)
```bash
# Editar Security Group en AWS Console
# Cambiar SSH (22) de 0.0.0.0/0 a tu IP específica
```

#### 4️⃣ Habilitar MFA en AWS Console
1. IAM → Users → isael2ex
2. Security credentials → Assign MFA device

---

## 🔄 Estado Actual del Sistema

### ✅ Completado en esta sesión:
1. ✅ Usuario IAM creado con permisos de administrador
2. ✅ AWS CLI configurado
3. ✅ Key Pair SSH generado
4. ✅ Security Group configurado (puertos 22, 80, 443, 8000)
5. ✅ Instancia EC2 lanzada (t3.micro, Ubuntu 22.04)
6. ✅ Base de datos RDS PostgreSQL creada y disponible
7. ✅ Bucket S3 creado
8. ✅ Script de despliegue automatizado preparado

### ⏳ Pendiente (próximo paso):
1. Conectarse por SSH al servidor EC2
2. Ejecutar el script de despliegue
3. Verificar que la aplicación funciona
4. Probar los endpoints desde el navegador

---

## 📞 Troubleshooting

### Problema: No puedo conectarme por SSH
**Solución**:
1. Verificar que el Security Group permite el puerto 22
2. Verificar que la instancia EC2 está en estado "running"
3. En Windows, usar Git Bash o convertir .pem a .ppk para PuTTY

### Problema: El script de despliegue falla
**Solución**:
1. Ver logs: `cat /tmp/deploy.log`
2. Verificar conexión a RDS: `nc -zv django-db.cormkuccww82.us-east-1.rds.amazonaws.com 5432`
3. Verificar que GitHub es accesible: `git ls-remote https://github.com/Camila-V1/backend_2ex.git`

### Problema: Nginx devuelve 502 Bad Gateway
**Solución**:
1. Verificar que Gunicorn está corriendo: `sudo systemctl status gunicorn`
2. Ver logs de Gunicorn: `sudo journalctl -u gunicorn -n 50`
3. Reiniciar servicios: `sudo systemctl restart gunicorn nginx`

---

## 📁 Archivos Generados

| Archivo | Descripción |
|---------|-------------|
| `django-backend-key.pem` | Clave privada SSH (⚠️ NO compartir) |
| `RDS_ENDPOINT.txt` | Endpoint de RDS para referencia |
| `deploy_commands.sh` | Script de despliegue automatizado |
| `monitor_aws.ps1` | Script de monitoreo de infraestructura |
| `CONFIGURACION_SERVIDOR.md` | Guía detallada paso a paso |
| `DESPLIEGUE_AWS.md` | Guía completa de despliegue |

---

## 🎓 Recursos Adicionales

- **AWS Free Tier**: https://aws.amazon.com/free/
- **Django Deployment Checklist**: https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
- **Gunicorn Documentation**: https://docs.gunicorn.org/
- **Nginx Documentation**: https://nginx.org/en/docs/

---

## ✅ Checklist de Despliegue

- [x] Crear usuario IAM con permisos
- [x] Configurar AWS CLI
- [x] Crear Key Pair SSH
- [x] Crear Security Group
- [x] Lanzar instancia EC2
- [x] Crear base de datos RDS
- [x] Crear bucket S3
- [x] Preparar script de despliegue
- [ ] Conectarse al servidor EC2
- [ ] Ejecutar script de despliegue
- [ ] Verificar funcionamiento
- [ ] Cambiar contraseñas
- [ ] Configurar dominio (opcional)
- [ ] Configurar HTTPS (opcional)

---

**Fecha**: 26 de octubre de 2025  
**Infraestructura**: AWS (us-east-1)  
**Estado**: ✅ Infraestructura lista, pendiente despliegue de aplicación
