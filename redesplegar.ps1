# 🔄 Script de Redespliegue Automático
# Aplica los últimos cambios del repositorio al servidor EC2

Write-Host "🚀 REDESPLIEGUE RÁPIDO - Backend E-commerce" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Variables
$EC2_IP = "3.88.180.221"
$KEY_FILE = "django-backend-key.pem"
$PROJECT_DIR = "/var/www/django-backend"

# Verificar que existe la clave SSH
if (-not (Test-Path $KEY_FILE)) {
    Write-Host "❌ ERROR: No se encontró la clave SSH ($KEY_FILE)" -ForegroundColor Red
    Write-Host "   Asegúrate de estar en el directorio correcto" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Clave SSH encontrada" -ForegroundColor Green
Write-Host ""

# Crear archivo de comandos para ejecutar en el servidor
$COMMANDS = @"
echo '🔄 Iniciando redespliegue...'
cd $PROJECT_DIR

echo '📥 Descargando últimos cambios de GitHub...'
git pull origin main

echo '🐍 Activando entorno virtual...'
source venv/bin/activate

echo '📦 Actualizando dependencias...'
pip install -r requirements.txt

echo '🗄️ Aplicando migraciones de base de datos...'
python manage.py makemigrations
python manage.py migrate

echo '📁 Recolectando archivos estáticos...'
python manage.py collectstatic --noinput

echo '🔄 Reiniciando Gunicorn...'
sudo systemctl restart gunicorn

echo '🔄 Reiniciando Nginx...'
sudo systemctl restart nginx

echo ''
echo '✅ Redespliegue completado!'
echo ''
echo '📊 Estado de los servicios:'
sudo systemctl status gunicorn --no-pager -l
echo ''
sudo systemctl status nginx --no-pager -l
"@

# Guardar comandos en archivo temporal
$COMMANDS | Out-File -FilePath "temp_deploy_commands.sh" -Encoding UTF8 -NoNewline

Write-Host "📋 Comandos preparados para ejecutar:" -ForegroundColor Cyan
Write-Host "   1. Descargar cambios de GitHub" -ForegroundColor White
Write-Host "   2. Actualizar dependencias" -ForegroundColor White
Write-Host "   3. Aplicar migraciones" -ForegroundColor White
Write-Host "   4. Recolectar estáticos" -ForegroundColor White
Write-Host "   5. Reiniciar servicios" -ForegroundColor White
Write-Host ""

$response = Read-Host "¿Continuar con el redespliegue? (S/N)"
if ($response -ne "S" -and $response -ne "s") {
    Write-Host "❌ Redespliegue cancelado" -ForegroundColor Yellow
    Remove-Item "temp_deploy_commands.sh" -ErrorAction SilentlyContinue
    exit 0
}

Write-Host ""
Write-Host "🔌 Conectando al servidor EC2..." -ForegroundColor Cyan
Write-Host ""

# Ejecutar comandos en el servidor
Get-Content "temp_deploy_commands.sh" | ssh -i $KEY_FILE ubuntu@$EC2_IP "bash -s"

# Limpiar archivo temporal
Remove-Item "temp_deploy_commands.sh" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "🧪 Verificando endpoints..." -ForegroundColor Cyan
Write-Host ""

# Probar endpoint de productos
try {
    $response = Invoke-WebRequest -Uri "http://$EC2_IP/api/products/" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API funcionando correctamente" -ForegroundColor Green
        Write-Host "   GET /api/products/ → Status 200" -ForegroundColor White
    }
} catch {
    Write-Host "⚠️  No se pudo verificar la API" -ForegroundColor Yellow
    Write-Host "   Verifica manualmente: http://$EC2_IP/api/products/" -ForegroundColor White
}

Write-Host ""
Write-Host "🎉 REDESPLIEGUE COMPLETADO" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
Write-Host ""
Write-Host "📍 URLs disponibles:" -ForegroundColor Cyan
Write-Host "   API Root:     http://$EC2_IP/api/" -ForegroundColor White
Write-Host "   Django Admin: http://$EC2_IP/admin/" -ForegroundColor White
Write-Host "   Productos:    http://$EC2_IP/api/products/" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Credenciales de prueba:" -ForegroundColor Cyan
Write-Host "   CLIENTE:  juan_cliente / password123" -ForegroundColor White
Write-Host "   MANAGER:  carlos_manager / manager123" -ForegroundColor White
Write-Host "   ADMIN:    admin / admin123" -ForegroundColor White
Write-Host ""
Write-Host "Ver documentacion completa: REDESPLIEGUE_RAPIDO.md" -ForegroundColor Yellow
