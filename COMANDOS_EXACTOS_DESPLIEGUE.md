# 🎯 COMANDOS EXACTOS PARA DESPLEGAR

## ✅ TODO ESTÁ LISTO - Ejecuta estos comandos

### 📍 Tu infraestructura AWS está 100% operativa:
- ✅ EC2: Running (IP: 3.88.180.221)
- ✅ RDS: Available (django-db.cormkuccww82.us-east-1.rds.amazonaws.com)
- ✅ S3: Available (django-backend-static-3193)
- ✅ SSH: Puerto 22 abierto y accesible

---

## 🚀 OPCIÓN 1: Usando Git Bash (MÁS FÁCIL)

### 1️⃣ Abrir Git Bash
- Descargar de: https://git-scm.com/download/win (si no lo tienes)
- Click derecho en Escritorio → "Git Bash Here"

### 2️⃣ Copiar y pegar estos comandos (UNO POR UNO):

```bash
# Navegar al directorio del proyecto
cd "/c/Users/asus/Documents/SISTEMAS DE INFORMACION 2/segundo examen SI2/backend_2ex"

# Configurar permisos de la clave SSH
chmod 400 django-backend-key.pem

# Conectarse al servidor EC2
ssh -i django-backend-key.pem ubuntu@3.88.180.221
```

**Cuando pregunte "Are you sure you want to continue connecting":**
- Escribir: `yes`
- Presionar Enter

### 3️⃣ Una vez dentro del servidor, ejecutar:

```bash
# Crear el script de despliegue
cat > deploy_commands.sh << 'EOF'
#!/bin/bash
set -e
echo "Iniciando despliegue..."
sudo apt update
sudo apt install -y python3-pip python3-venv nginx postgresql-client git redis-server
sudo mkdir -p /var/www/django-backend
sudo chown ubuntu:ubuntu /var/www/django-backend
cd /var/www/django-backend
git clone https://github.com/Camila-V1/backend_2ex.git .
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn boto3 django-storages psycopg2-binary python-decouple
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
cat > .env << ENVEOF
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=3.88.180.221,localhost
DB_NAME=django_db
DB_USER=dbadmin
DB_PASSWORD=Django2024Secure!
DB_HOST=django-db.cormkuccww82.us-east-1.rds.amazonaws.com
DB_PORT=5432
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_HERE
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY_HERE
AWS_STORAGE_BUCKET_NAME=YOUR_S3_BUCKET_NAME_HERE
AWS_S3_REGION_NAME=us-east-1
USE_S3=True
REDIS_HOST=localhost
REDIS_PORT=6379
STRIPE_SECRET_KEY=sk_test_placeholder
STRIPE_WEBHOOK_SECRET=whsec_placeholder
ENVEOF
PGPASSWORD=Django2024Secure! psql -h django-db.cormkuccww82.us-east-1.rds.amazonaws.com -U dbadmin -d postgres -c "SELECT 'CREATE DATABASE django_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'django_db')" | psql -h django-db.cormkuccww82.us-east-1.rds.amazonaws.com -U dbadmin -d postgres
python manage.py migrate
python manage.py collectstatic --noinput
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell
sudo tee /etc/systemd/system/gunicorn.service > /dev/null << SERVICEEOF
[Unit]
Description=gunicorn daemon
After=network.target
[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/django-backend
ExecStart=/var/www/django-backend/venv/bin/gunicorn --workers 3 --bind unix:/var/www/django-backend/gunicorn.sock ecommerce_api.wsgi:application
[Install]
WantedBy=multi-user.target
SERVICEEOF
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo tee /etc/nginx/sites-available/django-backend > /dev/null << NGINXEOF
server {
    listen 80;
    server_name 3.88.180.221;
    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ { alias /var/www/django-backend/staticfiles/; }
    location /media/ { alias /var/www/django-backend/media/; }
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/django-backend/gunicorn.sock;
    }
}
NGINXEOF
sudo ln -sf /etc/nginx/sites-available/django-backend /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
sudo systemctl start redis-server
sudo systemctl enable redis-server
echo "¡Despliegue completado!"
echo "API: http://3.88.180.221/api/"
echo "Admin: http://3.88.180.221/admin/"
echo "Usuario: admin | Password: admin123"
EOF

# Dar permisos de ejecución
chmod +x deploy_commands.sh

# ¡EJECUTAR EL DESPLIEGUE!
./deploy_commands.sh
```

**Tiempo estimado**: 10-15 minutos

### 4️⃣ Cuando termine, verificar:

```bash
# Ver estado de servicios
sudo systemctl status nginx
sudo systemctl status gunicorn

# Probar la API
curl http://localhost/api/

# Ver logs (si hay problemas)
sudo journalctl -u gunicorn -n 50
```

### 5️⃣ Salir del servidor:

```bash
exit
```

---

## 🚀 OPCIÓN 2: Usando PowerShell (con OpenSSH)

### 1️⃣ Abrir PowerShell como Administrador

### 2️⃣ Instalar OpenSSH (si no lo tienes):
```powershell
Add-WindowsCapability -Online -Name OpenSSH.Client
```

### 3️⃣ Navegar al directorio:
```powershell
cd "C:\Users\asus\Documents\SISTEMAS DE INFORMACION 2\segundo examen SI2\backend_2ex"
```

### 4️⃣ Configurar permisos de la clave:
```powershell
icacls django-backend-key.pem /inheritance:r
icacls django-backend-key.pem /grant:r "$($env:USERNAME):(R)"
```

### 5️⃣ Conectarse:
```powershell
ssh -i django-backend-key.pem ubuntu@3.88.180.221
```

### 6️⃣ Dentro del servidor, ejecutar los mismos comandos de la Opción 1 (paso 3)

---

## 🌐 PROBAR LA APLICACIÓN

### Una vez completado el despliegue:

1. **Abrir navegador** en tu computadora Windows
2. **Ir a**: http://3.88.180.221/api/
3. **Admin**: http://3.88.180.221/admin/
   - Usuario: `admin`
   - Password: `admin123`

### Endpoints disponibles:
- API Root: http://3.88.180.221/api/
- Admin Panel: http://3.88.180.221/admin/
- Productos: http://3.88.180.221/api/products/
- Usuarios: http://3.88.180.221/api/users/
- Órdenes: http://3.88.180.221/api/orders/
- Auditoría: http://3.88.180.221/api/audit/logs/
- Reportes: http://3.88.180.221/api/reports/

---

## 🛠️ COMANDOS ÚTILES DESPUÉS DEL DESPLIEGUE

### Ver logs en tiempo real:
```bash
sudo journalctl -u gunicorn -f
```

### Reiniciar servicios:
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Actualizar código desde GitHub:
```bash
cd /var/www/django-backend
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

### Cambiar contraseña del admin:
```bash
cd /var/www/django-backend
source venv/bin/activate
python manage.py changepassword admin
```

---

## ⚠️ SOLUCIÓN DE PROBLEMAS

### Si el script falla en algún paso:

1. **Ver el error específico** - El script mostrará dónde falló
2. **Ver logs de Gunicorn**:
   ```bash
   sudo journalctl -u gunicorn -n 100 --no-pager
   ```
3. **Ver logs de Nginx**:
   ```bash
   sudo tail -n 100 /var/log/nginx/error.log
   ```
4. **Verificar que RDS es accesible**:
   ```bash
   nc -zv django-db.cormkuccww82.us-east-1.rds.amazonaws.com 5432
   ```
5. **Probar conexión a la base de datos**:
   ```bash
   PGPASSWORD=Django2024Secure! psql -h django-db.cormkuccww82.us-east-1.rds.amazonaws.com -U dbadmin -d postgres -c "SELECT version();"
   ```

### Si Nginx devuelve 502 Bad Gateway:

```bash
# Verificar estado de Gunicorn
sudo systemctl status gunicorn

# Si está fallando, ver por qué
sudo journalctl -u gunicorn -n 50

# Verificar que el socket existe
ls -la /var/www/django-backend/gunicorn.sock

# Reiniciar ambos servicios
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

## 📊 VERIFICACIÓN FINAL

### En tu navegador, deberías ver:

**http://3.88.180.221/api/**
```json
{
  "message": "E-commerce API is running",
  "endpoints": {
    "products": "/api/products/",
    "users": "/api/users/",
    "orders": "/api/orders/",
    ...
  }
}
```

**http://3.88.180.221/admin/**
- Pantalla de login de Django Admin
- Login: admin / admin123

---

## 💰 COSTOS

### Primer año (Free Tier):
- EC2 t3.micro: **$0** (750 horas/mes gratis)
- RDS db.t3.micro: **$0** (750 horas/mes gratis)
- S3: **~$0.12/mes** (almacenamiento)
- **Total: ~$0.12/mes**

### Después del primer año:
- EC2: ~$8.50/mes
- RDS: ~$15/mes
- S3: ~$0.12/mes
- **Total: ~$24/mes**

### Monitorear costos:
https://console.aws.amazon.com/billing/

---

## ✅ CHECKLIST

- [ ] Abrir Git Bash o PowerShell
- [ ] Conectarse: `ssh -i django-backend-key.pem ubuntu@3.88.180.221`
- [ ] Crear y ejecutar `deploy_commands.sh`
- [ ] Esperar 10-15 minutos
- [ ] Probar: http://3.88.180.221/api/
- [ ] Login admin: http://3.88.180.221/admin/
- [ ] Cambiar contraseña del admin
- [ ] ¡Disfrutar tu aplicación en la nube! 🎉

---

**¡Todo listo para desplegar en 3... 2... 1...!** 🚀
