#!/bin/bash
set -e

echo "=========================================="
echo "   DESPLIEGUE AUTOMATICO DJANGO BACKEND"
echo "=========================================="
echo ""

# Actualizar sistema
echo "[1/12] Actualizando sistema..."
sudo apt update && sudo DEBIAN_FRONTEND=noninteractive apt upgrade -y

# Instalar dependencias
echo "[2/12] Instalando dependencias..."
sudo apt install -y python3-pip python3-venv nginx postgresql-client git redis-server

# Crear directorio del proyecto
echo "[3/12] Creando directorio del proyecto..."
sudo mkdir -p /var/www/django-backend
sudo chown ubuntu:ubuntu /var/www/django-backend
cd /var/www/django-backend

# Clonar repositorio
echo "[4/12] Clonando repositorio desde GitHub..."
git clone https://github.com/Camila-V1/backend_2ex.git .

# Crear entorno virtual
echo "[5/12] Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar paquetes Python
echo "[6/12] Instalando paquetes Python..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn boto3 django-storages psycopg2-binary python-decouple

# Generar SECRET_KEY
echo "[7/12] Configurando variables de entorno..."
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# Crear archivo .env
cat > .env << 'ENVEOF'
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=98.92.49.243,localhost
DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=Django2024Secure!
DB_HOST=django-db.cormkuccww82.us-east-1.rds.amazonaws.com
DB_PORT=5432
USE_S3=False
REDIS_HOST=localhost
REDIS_PORT=6379
ENVEOF

# Verificar conexión a RDS
echo "[8/12] Verificando conexión a base de datos..."
PGPASSWORD=Django2024Secure! psql -h django-db.cormkuccww82.us-east-1.rds.amazonaws.com -U postgres -d postgres -c "\l" || echo "Advertencia: No se pudo conectar a RDS"

# Ejecutar migraciones
echo "[9/12] Aplicando migraciones..."
python manage.py migrate

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Crear superusuario admin
echo "[10/12] Creando usuario administrador..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123', role='ADMIN')" | python manage.py shell

# Configurar Gunicorn
echo "[11/12] Configurando Gunicorn..."
sudo tee /etc/systemd/system/gunicorn.service > /dev/null << 'SERVICEEOF'
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

# Configurar Nginx
echo "[12/12] Configurando Nginx..."
sudo tee /etc/nginx/sites-available/django-backend > /dev/null << 'NGINXEOF'
server {
    listen 80;
    server_name 98.92.49.243;
    
    client_max_body_size 10M;
    
    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ { 
        alias /var/www/django-backend/staticfiles/; 
    }
    
    location /media/ { 
        alias /var/www/django-backend/media/; 
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/django-backend/gunicorn.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
NGINXEOF

sudo ln -sf /etc/nginx/sites-available/django-backend /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Iniciar Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

echo ""
echo "=========================================="
echo "   DESPLIEGUE COMPLETADO EXITOSAMENTE"
echo "=========================================="
echo ""
echo "URLs disponibles:"
echo "  API Root:     http://98.92.49.243/api/"
echo "  Django Admin: http://98.92.49.243/admin/"
echo "  Productos:    http://98.92.49.243/api/products/"
echo ""
echo "Credenciales:"
echo "  Admin: admin / admin123"
echo ""
echo "Para poblar la base de datos con datos de prueba:"
echo "  cd /var/www/django-backend"
echo "  source venv/bin/activate"
echo "  python seed_complete_database.py"
echo ""
