# test_api_quick.ps1
# Script de PowerShell para ejecutar tests rápidamente

Write-Host "🚀 Ejecutando pruebas de API..." -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptPath\tests_api"

python run_all_tests.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Todas las pruebas completadas exitosamente!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️ Algunas pruebas fallaron. Revisa el output arriba." -ForegroundColor Yellow
}
