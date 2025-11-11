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

echo "🗑️ LIMPIANDO base de datos (flush)..."
# Limpiar TODA la base de datos en cada deploy para tener datos consistentes
python manage.py flush --no-input

echo "🌱 Repoblando base de datos con datos iniciales..."
# Ejecutar seed_data.py siempre después de limpiar
python seed_data.py

echo "✅ Deploy completado exitosamente!"
echo "📊 Base de datos limpia y repoblada con datos frescos"
