# Script para iniciar Redis en Windows
# Asume que Redis está instalado via WSL o Docker

Write-Host "Iniciando Redis para SmartSales365..." -ForegroundColor Cyan

# Opción 1: Docker (recomendado)
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "Iniciando Redis con Docker..." -ForegroundColor Yellow
    docker run -d --name smartsales-redis -p 6379:6379 redis:latest
    Write-Host "✓ Redis corriendo en puerto 6379" -ForegroundColor Green
    exit 0
}

# Opción 2: WSL
if (Get-Command wsl -ErrorAction SilentlyContinue) {
    Write-Host "Iniciando Redis con WSL..." -ForegroundColor Yellow
    wsl redis-server --daemonize yes
    Write-Host "✓ Redis corriendo en puerto 6379" -ForegroundColor Green
    exit 0
}

# Si ninguno está disponible
Write-Host "❌ Redis no encontrado. Instala Redis via:" -ForegroundColor Red
Write-Host "  - Docker: docker run -d -p 6379:6379 redis:latest" -ForegroundColor Yellow
Write-Host "  - WSL: sudo apt install redis-server && redis-server" -ForegroundColor Yellow
Write-Host "  - Memurai (Windows nativo): https://www.memurai.com/" -ForegroundColor Yellow
Write-Host "`nSi no tienes Redis, el cache no funcionará pero la API seguirá funcionando." -ForegroundColor Cyan
