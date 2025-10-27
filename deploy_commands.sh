#!/bin/bash

# 🚀 Script de Despliegue Automático para Django Backend en EC2
# Este script debe ejecutarse DENTRO del servidor EC2

set -e  # Detener si hay errores

echo "════════════════════════════════════════════════════════════"
echo "🚀 INICIO DEL DESPLIEGUE - Django E-commerce Backend"
echo "════════════════════════════════════════════════════════════"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
DB_ENDPOINT="django-db.cormkuccww82.us-east-1.rds.amazonaws.com"
GITHUB_REPO="https://github.com/Camila-V1/backend_2ex.git"
PROJECT_DIR="/var/www/django-backend"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📦 Paso 1: Actualizando sistema operativo"
echo "═══════════════════════════════════════════════════════════"
sudo apt update
sudo apt upgrade -y

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📦 Paso 2: Instalando dependencias del sistema"
echo "═══════════════════════════════════════════════════════════"
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    libpq-dev \
    nginx \
    postgresql-client \
    git \
    redis-server \
    curl \
    wget

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Versiones instaladas:"
echo "═══════════════════════════════════════════════════════════"
python3 --version
nginx -v
psql --version
redis-cli --version
git --version

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📂 Paso 3: Creando estructura de directorios"
echo "═══════════════════════════════════════════════════════════"
sudo mkdir -p $PROJECT_DIR
sudo chown ubuntu:ubuntu $PROJECT_DIR
cd $PROJECT_DIR

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📥 Paso 4: Clonando repositorio desde GitHub"
echo "═══════════════════════════════════════════════════════════"
if [ -d ".git" ]; then
    echo "⚠️  Repositorio ya existe. Actualizando..."
    git pull origin main
else
    echo "📥 Clonando repositorio..."
    git clone $GITHUB_REPO .
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🐍 Paso 5: Creando entorno virtual de Python"
echo "═══════════════════════════════════════════════════════════"
python3 -m venv venv
source venv/bin/activate

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📦 Paso 6: Instalando dependencias de Python"
echo "═══════════════════════════════════════════════════════════"
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn boto3 django-storages psycopg2-binary python-decouple

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🔐 Paso 7: Configurando variables de entorno"
echo "═══════════════════════════════════════════════════════════"

# Generar SECRET_KEY
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

cat > .env << EOF
# Django Configuration
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=3.88.180.221,localhost,127.0.0.1

# Database Configuration
DB_NAME=django_db
DB_USER=dbadmin
DB_PASSWORD=Django2024Secure!
DB_HOST=$DB_ENDPOINT
DB_PORT=5432

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_HERE
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY_HERE
AWS_STORAGE_BUCKET_NAME=YOUR_S3_BUCKET_NAME_HERE
AWS_S3_REGION_NAME=us-east-1
USE_S3=True

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Stripe Configuration (actualizar con tus claves reales)
STRIPE_SECRET_KEY=sk_test_tu_clave_aqui
STRIPE_WEBHOOK_SECRET=whsec_tu_webhook_aqui

# Email Configuration (opcional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EOF

echo -e "${GREEN}✅ Archivo .env creado${NC}"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🗄️  Paso 8: Configurando base de datos"
echo "═══════════════════════════════════════════════════════════"

# Esperar a que RDS esté disponible
echo "⏳ Esperando a que RDS esté disponible..."
for i in {1..30}; do
    if PGPASSWORD=Django2024Secure! psql -h $DB_ENDPOINT -U dbadmin -d postgres -c "SELECT 1" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ RDS está disponible${NC}"
        break
    fi
    echo "Intento $i/30... esperando 10 segundos"
    sleep 10
done

# Crear base de datos si no existe
PGPASSWORD=Django2024Secure! psql -h $DB_ENDPOINT -U dbadmin -d postgres << 'EOSQL'
SELECT 'CREATE DATABASE django_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'django_db')\gexec
EOSQL

echo -e "${GREEN}✅ Base de datos configurada${NC}"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🔄 Paso 9: Ejecutando migraciones de Django"
echo "═══════════════════════════════════════════════════════════"
python manage.py makemigrations
python manage.py migrate

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📁 Paso 10: Recolectando archivos estáticos"
echo "═══════════════════════════════════════════════════════════"
python manage.py collectstatic --noinput

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "👤 Paso 11: Creando superusuario (si no existe)"
echo "═══════════════════════════════════════════════════════════"
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🌱 Paso 12: Cargando datos de prueba (opcional)"
echo "═══════════════════════════════════════════════════════════"
if [ -f "seed_data.py" ]; then
    python seed_data.py
    echo -e "${GREEN}✅ Datos de prueba cargados${NC}"
else
    echo -e "${YELLOW}⚠️  No se encontró seed_data.py${NC}"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🦄 Paso 13: Configurando Gunicorn"
echo "═══════════════════════════════════════════════════════════"

sudo tee /etc/systemd/system/gunicorn.service > /dev/null << EOF
[Unit]
Description=gunicorn daemon for Django backend
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/gunicorn \\
          --access-logfile - \\
          --workers 3 \\
          --timeout 120 \\
          --bind unix:$PROJECT_DIR/gunicorn.sock \\
          ecommerce_api.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

echo -e "${GREEN}✅ Gunicorn configurado e iniciado${NC}"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🌐 Paso 14: Configurando Nginx"
echo "═══════════════════════════════════════════════════════════"

sudo tee /etc/nginx/sites-available/django-backend > /dev/null << 'EOF'
server {
    listen 80;
    server_name 3.88.180.221;
    client_max_body_size 100M;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        alias /var/www/django-backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/django-backend/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/django-backend/gunicorn.sock;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_redirect off;
        proxy_buffering off;
        proxy_read_timeout 120s;
    }
}
EOF

# Activar sitio
sudo ln -sf /etc/nginx/sites-available/django-backend /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx

echo -e "${GREEN}✅ Nginx configurado e iniciado${NC}"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🔥 Paso 15: Configurando Redis"
echo "═══════════════════════════════════════════════════════════"
sudo systemctl start redis-server
sudo systemctl enable redis-server
echo -e "${GREEN}✅ Redis iniciado${NC}"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🔍 Paso 16: Verificando estado de servicios"
echo "═══════════════════════════════════════════════════════════"

services=("nginx" "gunicorn" "redis-server")

for service in "${services[@]}"; do
    if sudo systemctl is-active --quiet $service; then
        echo -e "${GREEN}✅ $service está corriendo${NC}"
    else
        echo -e "${RED}❌ $service NO está corriendo${NC}"
        sudo systemctl status $service --no-pager -l
    fi
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🧪 Paso 17: Prueba de conectividad"
echo "═══════════════════════════════════════════════════════════"

sleep 3

echo "Probando endpoint /api/..."
curl -I http://localhost/api/ || echo -e "${YELLOW}⚠️  Endpoint no responde aún${NC}"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ DESPLIEGUE COMPLETADO EXITOSAMENTE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📊 URLs del sistema:"
echo "   🌐 API: http://3.88.180.221/api/"
echo "   🔐 Admin: http://3.88.180.221/admin/"
echo "   📈 Health: http://3.88.180.221/api/health/"
echo ""
echo "👤 Credenciales de superusuario:"
echo "   Username: admin"
echo "   Password: admin123"
echo "   ⚠️  CAMBIA ESTA CONTRASEÑA INMEDIATAMENTE"
echo ""
echo "📝 Comandos útiles:"
echo "   Ver logs de Gunicorn: sudo journalctl -u gunicorn -f"
echo "   Ver logs de Nginx: sudo tail -f /var/log/nginx/error.log"
echo "   Reiniciar Gunicorn: sudo systemctl restart gunicorn"
echo "   Reiniciar Nginx: sudo systemctl restart nginx"
echo ""
echo "════════════════════════════════════════════════════════════"
