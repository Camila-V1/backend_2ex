# ============================================================================
# Script PowerShell para Actualizar CORS en el Backend para Vercel
# ============================================================================
# Ejecutar este script después de desplegar tu frontend en Vercel
# Uso: .\update_cors_for_vercel.ps1 -VercelDomain "tu-app.vercel.app"

param(
    [Parameter(Mandatory=$true)]
    [string]$VercelDomain
)

$ErrorActionPreference = "Stop"

# Configuración
$ServerIP = "98.92.49.243"
$SSHKey = "django-backend-key.pem"
$SSHUser = "ubuntu"

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  Actualización de CORS para Frontend en Vercel" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📝 Configuración:" -ForegroundColor Green
Write-Host "  • Dominio Vercel: https://$VercelDomain"
Write-Host "  • Servidor Backend: $ServerIP"
Write-Host ""

# Verificar que existe la clave SSH
if (-not (Test-Path $SSHKey)) {
    Write-Host "❌ Error: No se encuentra el archivo $SSHKey" -ForegroundColor Red
    Write-Host "Asegúrate de estar en la carpeta correcta que contiene la clave SSH" -ForegroundColor Yellow
    exit 1
}

Write-Host "🔄 Conectando al servidor..." -ForegroundColor Yellow
Write-Host ""

# Actualizar ALLOWED_HOSTS
Write-Host "1. Actualizando ALLOWED_HOSTS..." -ForegroundColor Cyan
$updateAllowedHostsCmd = @"
cd /var/www/django-backend && \
sudo cp .env .env.backup.`$(date +%Y%m%d_%H%M%S) && \
sudo sed -i 's/^ALLOWED_HOSTS=.*/ALLOWED_HOSTS=$ServerIP,localhost,127.0.0.1,$VercelDomain/' .env
"@

ssh -i $SSHKey "$SSHUser@$ServerIP" $updateAllowedHostsCmd
Write-Host "   ✓ ALLOWED_HOSTS actualizado" -ForegroundColor Green

# Actualizar CORS_ALLOWED_ORIGINS
Write-Host "2. Actualizando CORS_ALLOWED_ORIGINS..." -ForegroundColor Cyan
$updateCorsCmd = @"
cd /var/www/django-backend && \
if grep -q '^CORS_ALLOWED_ORIGINS=' .env; then \
    sudo sed -i 's|^CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=https://$VercelDomain,http://localhost:3000,http://localhost:5173|' .env; \
else \
    echo 'CORS_ALLOWED_ORIGINS=https://$VercelDomain,http://localhost:3000,http://localhost:5173' | sudo tee -a .env; \
fi
"@

ssh -i $SSHKey "$SSHUser@$ServerIP" $updateCorsCmd
Write-Host "   ✓ CORS_ALLOWED_ORIGINS actualizado" -ForegroundColor Green

# Desactivar CORS_ALLOW_ALL_ORIGINS
Write-Host "3. Configurando CORS_ALLOW_ALL_ORIGINS..." -ForegroundColor Cyan
$updateCorsAllCmd = @"
cd /var/www/django-backend && \
if grep -q '^CORS_ALLOW_ALL_ORIGINS=' .env; then \
    sudo sed -i 's/^CORS_ALLOW_ALL_ORIGINS=.*/CORS_ALLOW_ALL_ORIGINS=False/' .env; \
fi
"@

ssh -i $SSHKey "$SSHUser@$ServerIP" $updateCorsAllCmd
Write-Host "   ✓ CORS_ALLOW_ALL_ORIGINS configurado" -ForegroundColor Green

Write-Host ""
Write-Host "🔄 Reiniciando servicios..." -ForegroundColor Yellow

# Reiniciar Gunicorn
ssh -i $SSHKey "$SSHUser@$ServerIP" "sudo systemctl restart gunicorn"
Write-Host "   ✓ Gunicorn reiniciado" -ForegroundColor Green

# Reiniciar Nginx
ssh -i $SSHKey "$SSHUser@$ServerIP" "sudo systemctl restart nginx"
Write-Host "   ✓ Nginx reiniciado" -ForegroundColor Green

Write-Host ""
Write-Host "🔍 Verificando estado de los servicios..." -ForegroundColor Yellow

# Verificar Gunicorn
$gunicornStatus = ssh -i $SSHKey "$SSHUser@$ServerIP" "systemctl is-active gunicorn"
if ($gunicornStatus -eq "active") {
    Write-Host "   ✓ Gunicorn: Activo" -ForegroundColor Green
} else {
    Write-Host "   ✗ Gunicorn: Inactivo" -ForegroundColor Red
}

# Verificar Nginx
$nginxStatus = ssh -i $SSHKey "$SSHUser@$ServerIP" "systemctl is-active nginx"
if ($nginxStatus -eq "active") {
    Write-Host "   ✓ Nginx: Activo" -ForegroundColor Green
} else {
    Write-Host "   ✗ Nginx: Inactivo" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "✅ CONFIGURACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Resumen de cambios:" -ForegroundColor Yellow
Write-Host "  • ALLOWED_HOSTS actualizado con: $VercelDomain"
Write-Host "  • CORS_ALLOWED_ORIGINS configurado para: https://$VercelDomain"
Write-Host "  • Servicios reiniciados correctamente"
Write-Host ""
Write-Host "🧪 Prueba tu aplicación:" -ForegroundColor Yellow
Write-Host "  • Frontend: https://$VercelDomain"
Write-Host "  • Backend API: http://$ServerIP/api/"
Write-Host "  • Admin Panel: http://$ServerIP/admin/"
Write-Host ""
Write-Host "🔑 Credenciales de prueba:" -ForegroundColor Yellow
Write-Host "  • Cliente: juan_cliente / password123"
Write-Host "  • Manager: carlos_manager / manager123"
Write-Host "  • Admin: admin / admin123"
Write-Host ""
Write-Host "✨ ¡Listo! Tu frontend en Vercel ahora puede conectarse al backend." -ForegroundColor Green
Write-Host ""

# Mostrar contenido actual del .env (sin contraseñas)
Write-Host "📄 Configuración actual (sin credenciales sensibles):" -ForegroundColor Yellow
$showConfigCmd = @"
cd /var/www/django-backend && \
grep -E '^(ALLOWED_HOSTS|CORS_ALLOWED_ORIGINS|CORS_ALLOW_ALL_ORIGINS)=' .env
"@

ssh -i $SSHKey "$SSHUser@$ServerIP" $showConfigCmd | ForEach-Object {
    Write-Host "   $_" -ForegroundColor Gray
}
Write-Host ""
