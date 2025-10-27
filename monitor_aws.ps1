# Monitor de Estado - Infraestructura AWS
# Ejecutar desde Windows PowerShell

Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "MONITOR DE ESTADO - Infraestructura AWS" -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host ""

# Variables
$EC2_INSTANCE_ID = "i-05700893150f99361"
$RDS_INSTANCE_ID = "django-db"
$S3_BUCKET = "django-backend-static-3193"

# 1. Estado de EC2
Write-Host "---------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "EC2 Instance" -ForegroundColor Yellow
Write-Host "---------------------------------------------------------------" -ForegroundColor DarkGray

try {
    $ec2_status = aws ec2 describe-instances --instance-ids $EC2_INSTANCE_ID --query "Reservations[0].Instances[0].State.Name" --output text
    $ec2_ip = aws ec2 describe-instances --instance-ids $EC2_INSTANCE_ID --query "Reservations[0].Instances[0].PublicIpAddress" --output text
    
    Write-Host "Estado: $ec2_status" -ForegroundColor Green
    Write-Host "IP Publica: $ec2_ip" -ForegroundColor Green
} catch {
    Write-Host "Error obteniendo estado de EC2" -ForegroundColor Red
}

Write-Host ""

# 2. Estado de RDS
Write-Host "---------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "Base de Datos RDS" -ForegroundColor Yellow
Write-Host "---------------------------------------------------------------" -ForegroundColor DarkGray

try {
    $rds_status = aws rds describe-db-instances --db-instance-identifier $RDS_INSTANCE_ID --query "DBInstances[0].DBInstanceStatus" --output text
    
    Write-Host "Estado: $rds_status" -ForegroundColor Yellow
    
    if ($rds_status -eq "available") {
        $rds_endpoint = aws rds describe-db-instances --db-instance-identifier $RDS_INSTANCE_ID --query "DBInstances[0].Endpoint.Address" --output text
        
        Write-Host "Endpoint: $rds_endpoint" -ForegroundColor Green
        Write-Host "Puerto: 5432" -ForegroundColor Green
        
        # Guardar endpoint
        $rds_endpoint | Out-File -FilePath "RDS_ENDPOINT.txt" -Encoding ASCII
        Write-Host "Endpoint guardado en RDS_ENDPOINT.txt" -ForegroundColor Cyan
    } else {
        Write-Host "Esperando disponibilidad (5-10 minutos)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error obteniendo estado de RDS" -ForegroundColor Red
}

Write-Host ""

# 3. Estado de S3
Write-Host "---------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "Bucket S3" -ForegroundColor Yellow
Write-Host "---------------------------------------------------------------" -ForegroundColor DarkGray

try {
    $s3_exists = aws s3 ls "s3://$S3_BUCKET" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Estado: Disponible" -ForegroundColor Green
        Write-Host "Nombre: $S3_BUCKET" -ForegroundColor Green
    } else {
        Write-Host "Estado: Error de acceso" -ForegroundColor Red
    }
} catch {
    Write-Host "Error verificando S3" -ForegroundColor Red
}

Write-Host ""
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si RDS está listo
$rds_ready = $false
try {
    $current_rds_status = aws rds describe-db-instances --db-instance-identifier $RDS_INSTANCE_ID --query "DBInstances[0].DBInstanceStatus" --output text
    
    if ($current_rds_status -eq "available") {
        $rds_ready = $true
    }
} catch {}

Write-Host "SIGUIENTES PASOS:" -ForegroundColor Cyan
Write-Host ""

if ($rds_ready) {
    Write-Host "RDS esta disponible. Puedes proceder con el despliegue" -ForegroundColor Green
    Write-Host ""
    Write-Host "1. Conectarse al servidor EC2:" -ForegroundColor Yellow
    Write-Host "   ssh -i django-backend-key.pem ubuntu@$ec2_ip" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Copiar script de despliegue:" -ForegroundColor Yellow
    Write-Host "   scp -i django-backend-key.pem deploy_commands.sh ubuntu@${ec2_ip}:~/" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Ejecutar en el servidor:" -ForegroundColor Yellow
    Write-Host "   chmod +x deploy_commands.sh" -ForegroundColor White
    Write-Host "   ./deploy_commands.sh" -ForegroundColor White
    Write-Host ""
    
    # Mostrar endpoint de RDS
    $rds_ep = Get-Content "RDS_ENDPOINT.txt" -ErrorAction SilentlyContinue
    if ($rds_ep) {
        Write-Host "RDS Endpoint para usar en el script:" -ForegroundColor Cyan
        Write-Host "   $rds_ep" -ForegroundColor Green
    }
} else {
    Write-Host "RDS aun se esta creando. Espera a que este disponible." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Ejecuta este script nuevamente en 5 minutos:" -ForegroundColor Cyan
    Write-Host "   .\monitor_aws.ps1" -ForegroundColor White
}

Write-Host ""
Write-Host "===============================================================" -ForegroundColor Cyan
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "Monitor ejecutado: $timestamp" -ForegroundColor DarkGray
Write-Host "===============================================================" -ForegroundColor Cyan
