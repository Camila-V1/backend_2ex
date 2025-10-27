# 🚀 Configuración del Servidor AWS

## ✅ Recursos Creados

### 1. **Instancia EC2**
- **ID**: `i-05700893150f99361`
- **Tipo**: `t3.micro` (Free Tier elegible)
- **IP Pública**: `3.88.180.221`
- **Sistema Operativo**: Ubuntu 22.04 LTS
- **Key Pair**: `django-backend-key.pem` (en el directorio local)

### 2. **Security Group**
- **ID**: `sg-0cc0c93c58aedcd87`
- **Nombre**: `django-backend-sg`
- **Puertos Abiertos**:
  - 22 (SSH)
  - 80 (HTTP)
  - 443 (HTTPS)
  - 8000 (Django development)

### 3. **Base de Datos RDS PostgreSQL**
- **Identificador**: `django-db`
- **Clase**: `db.t3.micro`
- **Engine**: PostgreSQL 16.3
- **Usuario**: `dbadmin`
- **Contraseña**: `Django2024Secure!`
- **Almacenamiento**: 20 GB
- **Estado**: 🟡 Creándose (toma 5-10 minutos)

### 4. **Bucket S3**
- **Nombre**: `django-backend-static-3193`
- **Región**: `us-east-1`
- **Propósito**: Archivos estáticos y media

---

## 📋 Siguientes Pasos

### Paso 1: Esperar a que RDS esté disponible
```powershell
# Monitorear el estado de RDS
aws rds describe-db-instances --db-instance-identifier django-db --query "DBInstances[0].DBInstanceStatus" --output text

# Cuando diga "available", obtener el endpoint
aws rds describe-db-instances --db-instance-identifier django-db --query "DBInstances[0].Endpoint.Address" --output text
```

### Paso 2: Conectarse al servidor EC2
```powershell
# Usar SSH (necesitarás un cliente SSH para Windows como PuTTY o Git Bash)
ssh -i django-backend-key.pem ubuntu@3.88.180.221
```

**Nota**: Si usas PuTTY, necesitarás convertir `django-backend-key.pem` a formato `.ppk` con PuTTYgen.

### Paso 3: Instalar dependencias en el servidor
Una vez conectado al servidor:
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y dependencias
sudo apt install -y python3-pip python3-venv nginx postgresql-client git redis-server

# Verificar instalaciones
python3 --version
nginx -v
psql --version
redis-cli --version
```

### Paso 4: Clonar repositorio
```bash
# Crear directorio para el proyecto
sudo mkdir -p /var/www/django-backend
sudo chown ubuntu:ubuntu /var/www/django-backend
cd /var/www/django-backend

# Clonar tu repositorio (reemplaza con tu URL)
git clone https://github.com/Camila-V1/backend_2ex.git .

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install gunicorn boto3 django-storages psycopg2-binary
```

### Paso 5: Configurar variables de entorno
```bash
# Crear archivo .env
nano .env
```

Contenido del archivo `.env`:
```ini
# Database Configuration
DB_NAME=django_db
DB_USER=dbadmin
DB_PASSWORD=Django2024Secure!
DB_HOST=<RDS_ENDPOINT_AQUI>
DB_PORT=5432

# Django Settings
SECRET_KEY=<GENERA_UNA_CLAVE_SEGURA>
DEBUG=False
ALLOWED_HOSTS=3.88.180.221,<TU_DOMINIO_SI_LO_TIENES>

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_HERE
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY_HERE
AWS_STORAGE_BUCKET_NAME=YOUR_S3_BUCKET_NAME_HERE
AWS_S3_REGION_NAME=us-east-1

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Stripe Configuration
STRIPE_SECRET_KEY=<TU_STRIPE_KEY>
STRIPE_WEBHOOK_SECRET=<TU_WEBHOOK_SECRET>
```

### Paso 6: Crear base de datos en RDS
```bash
# Conectarse a RDS PostgreSQL
PGPASSWORD=Django2024Secure! psql -h <RDS_ENDPOINT> -U dbadmin -d postgres

# Dentro de psql:
CREATE DATABASE django_db;
\q
```

### Paso 7: Ejecutar migraciones
```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### Paso 8: Configurar Gunicorn
```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/gunicorn.service
```

Contenido:
```ini
[Unit]
Description=gunicorn daemon for Django backend
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/django-backend
ExecStart=/var/www/django-backend/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/var/www/django-backend/gunicorn.sock \
          ecommerce_api.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Iniciar y habilitar Gunicorn
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

### Paso 9: Configurar Nginx
```bash
sudo nano /etc/nginx/sites-available/django-backend
```

Contenido:
```nginx
server {
    listen 80;
    server_name 3.88.180.221;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/django-backend/staticfiles/;
    }
    
    location /media/ {
        alias /var/www/django-backend/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/django-backend/gunicorn.sock;
    }
}
```

```bash
# Activar configuración
sudo ln -s /etc/nginx/sites-available/django-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Paso 10: Verificar funcionamiento
```bash
# Ver logs de Gunicorn
sudo journalctl -u gunicorn -f

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

---

## 🔐 Credenciales Importantes

### AWS IAM User
- **Username**: `YOUR_IAM_USERNAME`
- **Access Key ID**: `YOUR_AWS_ACCESS_KEY_HERE`
- **Secret Access Key**: `YOUR_AWS_SECRET_KEY_HERE`
- **Console URL**: `YOUR_AWS_CONSOLE_URL`

### RDS PostgreSQL
- **Master Username**: `dbadmin`
- **Master Password**: `Django2024Secure!`
- **Database Name**: `django_db`
- **Puerto**: `5432`

### EC2 Access
- **IP**: `3.88.180.221`
- **Key File**: `django-backend-key.pem`
- **User**: `ubuntu`

---

## 💰 Costos Estimados

| Recurso | Tipo | Costo Mensual Estimado |
|---------|------|------------------------|
| EC2 t3.micro | 750 horas/mes (Free Tier) | $0 primer año, luego ~$8.50/mes |
| RDS db.t3.micro | 750 horas/mes (Free Tier) | $0 primer año, luego ~$15/mes |
| S3 | 5 GB almacenamiento | ~$0.12/mes |
| Transferencia de datos | 1 GB salida gratis | Variable |
| **TOTAL** | | **~$0-1** primer año, **~$24/mes** después |

---

## 🛠️ Comandos Útiles

### Reiniciar servicios
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
sudo systemctl restart redis-server
```

### Ver logs
```bash
# Django logs
sudo journalctl -u gunicorn -n 50 --no-pager

# Nginx logs
sudo tail -n 50 /var/log/nginx/error.log
```

### Actualizar código
```bash
cd /var/www/django-backend
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

---

## 📊 URLs del Sistema

- **API Backend**: http://3.88.180.221/api/
- **Admin Django**: http://3.88.180.221/admin/
- **Health Check**: http://3.88.180.221/api/health/

---

## ⚠️ Importante

1. **Cambia las contraseñas** después del primer despliegue
2. **Configura un dominio** para tener HTTPS con Let's Encrypt
3. **Habilita backups** automáticos de RDS (ya configurados 7 días)
4. **Monitorea costos** en AWS Console > Billing
5. **Guarda el archivo .pem** en un lugar seguro (no lo pierdas)

---

## 🔄 Estado Actual

✅ **Completado:**
- IAM User creado
- AWS CLI configurado
- EC2 lanzado y funcionando
- Security Group configurado
- S3 bucket creado
- RDS creándose (en progreso)

⏳ **Pendiente:**
- Esperar RDS (5-10 minutos)
- Conectarse por SSH
- Instalar dependencias
- Configurar aplicación
- Configurar Nginx + Gunicorn

---

**Fecha de creación**: 26 de octubre de 2025
