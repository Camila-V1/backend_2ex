#!/usr/bin/env bash
# Script de despliegue para Render
# Este script se ejecuta automáticamente cada vez que hay un nuevo deploy

set -o errexit  # Salir si hay error

echo "🔧 Instalando dependencias..."
pip install -r requirements.txt

echo "📦 Colectando archivos estáticos..."
python manage.py collectstatic --no-input

echo "🗄️ Ejecutando migraciones de base de datos..."
python manage.py migrate --no-input

echo "🌱 Poblando base de datos con datos iniciales..."
# Verificar si ya hay datos (para no duplicar)
python manage.py shell << EOF
from users.models import CustomUser
from products.models import Product

# Solo poblar si la base está vacía
if not CustomUser.objects.exists():
    print("Base de datos vacía, ejecutando seed_data.py...")
    import subprocess
    subprocess.run(['python', 'seed_data.py'])
else:
    print("Base de datos ya tiene datos, saltando seed_data.py")
EOF

echo "✅ Deploy completado exitosamente!"
