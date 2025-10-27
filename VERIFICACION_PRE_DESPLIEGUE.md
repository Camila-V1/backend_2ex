# ✅ VERIFICACIÓN PRE-DESPLIEGUE

## 📋 Checklist de Verificación

Ejecuta estos comandos en PowerShell para verificar que todo está listo:

```powershell
cd "C:\Users\asus\Documents\SISTEMAS DE INFORMACION 2\segundo examen SI2\backend_2ex"
```

### 1. ✅ Verificar que AWS CLI está configurado
```powershell
aws sts get-caller-identity
```
**Resultado esperado**: Debe mostrar tu usuario `isael2ex` y Account `487692780331`

### 2. ✅ Verificar que EC2 está corriendo
```powershell
aws ec2 describe-instances --instance-ids i-05700893150f99361 --query "Reservations[0].Instances[0].State.Name" --output text
```
**Resultado esperado**: `running`

### 3. ✅ Verificar IP pública de EC2
```powershell
aws ec2 describe-instances --instance-ids i-05700893150f99361 --query "Reservations[0].Instances[0].PublicIpAddress" --output text
```
**Resultado esperado**: `3.88.180.221`

### 4. ✅ Verificar que RDS está disponible
```powershell
aws rds describe-db-instances --db-instance-identifier django-db --query "DBInstances[0].DBInstanceStatus" --output text
```
**Resultado esperado**: `available`

### 5. ✅ Verificar endpoint de RDS
```powershell
aws rds describe-db-instances --db-instance-identifier django-db --query "DBInstances[0].Endpoint.Address" --output text
```
**Resultado esperado**: `django-db.cormkuccww82.us-east-1.rds.amazonaws.com`

### 6. ✅ Verificar que el archivo de clave SSH existe
```powershell
Test-Path django-backend-key.pem
```
**Resultado esperado**: `True`

### 7. ✅ Verificar que el script de despliegue existe
```powershell
Test-Path deploy_commands.sh
```
**Resultado esperado**: `True`

### 8. ✅ Verificar conectividad al servidor (ping)
```powershell
Test-NetConnection -ComputerName 3.88.180.221 -Port 22
```
**Resultado esperado**: `TcpTestSucceeded : True`

---

## 🚀 Script Automático de Verificación

Ejecuta este script para verificar todo de una vez:

```powershell
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "VERIFICACION PRE-DESPLIEGUE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$checks = @()

# 1. AWS CLI configurado
Write-Host "[1/8] Verificando AWS CLI..." -NoNewline
try {
    $identity = aws sts get-caller-identity 2>$null | ConvertFrom-Json
    if ($identity.UserId) {
        Write-Host " OK" -ForegroundColor Green
        $checks += $true
    } else {
        Write-Host " FALLO" -ForegroundColor Red
        $checks += $false
    }
} catch {
    Write-Host " FALLO" -ForegroundColor Red
    $checks += $false
}

# 2. EC2 corriendo
Write-Host "[2/8] Verificando EC2..." -NoNewline
try {
    $ec2_status = aws ec2 describe-instances --instance-ids i-05700893150f99361 --query "Reservations[0].Instances[0].State.Name" --output text
    if ($ec2_status -eq "running") {
        Write-Host " OK (running)" -ForegroundColor Green
        $checks += $true
    } else {
        Write-Host " ADVERTENCIA (estado: $ec2_status)" -ForegroundColor Yellow
        $checks += $false
    }
} catch {
    Write-Host " FALLO" -ForegroundColor Red
    $checks += $false
}

# 3. IP pública
Write-Host "[3/8] Verificando IP publica..." -NoNewline
try {
    $ec2_ip = aws ec2 describe-instances --instance-ids i-05700893150f99361 --query "Reservations[0].Instances[0].PublicIpAddress" --output text
    if ($ec2_ip -eq "3.88.180.221") {
        Write-Host " OK ($ec2_ip)" -ForegroundColor Green
        $checks += $true
    } else {
        Write-Host " ADVERTENCIA (IP: $ec2_ip)" -ForegroundColor Yellow
        $checks += $false
    }
} catch {
    Write-Host " FALLO" -ForegroundColor Red
    $checks += $false
}

# 4. RDS disponible
Write-Host "[4/8] Verificando RDS..." -NoNewline
try {
    $rds_status = aws rds describe-db-instances --db-instance-identifier django-db --query "DBInstances[0].DBInstanceStatus" --output text
    if ($rds_status -eq "available") {
        Write-Host " OK (available)" -ForegroundColor Green
        $checks += $true
    } else {
        Write-Host " ADVERTENCIA (estado: $rds_status)" -ForegroundColor Yellow
        $checks += $false
    }
} catch {
    Write-Host " FALLO" -ForegroundColor Red
    $checks += $false
}

# 5. Endpoint de RDS
Write-Host "[5/8] Verificando endpoint RDS..." -NoNewline
try {
    $rds_endpoint = aws rds describe-db-instances --db-instance-identifier django-db --query "DBInstances[0].Endpoint.Address" --output text
    if ($rds_endpoint) {
        Write-Host " OK" -ForegroundColor Green
        $checks += $true
    } else {
        Write-Host " FALLO" -ForegroundColor Red
        $checks += $false
    }
} catch {
    Write-Host " FALLO" -ForegroundColor Red
    $checks += $false
}

# 6. Archivo de clave SSH
Write-Host "[6/8] Verificando clave SSH..." -NoNewline
if (Test-Path django-backend-key.pem) {
    Write-Host " OK (django-backend-key.pem existe)" -ForegroundColor Green
    $checks += $true
} else {
    Write-Host " FALLO (archivo no encontrado)" -ForegroundColor Red
    $checks += $false
}

# 7. Script de despliegue
Write-Host "[7/8] Verificando script de despliegue..." -NoNewline
if (Test-Path deploy_commands.sh) {
    Write-Host " OK (deploy_commands.sh existe)" -ForegroundColor Green
    $checks += $true
} else {
    Write-Host " FALLO (archivo no encontrado)" -ForegroundColor Red
    $checks += $false
}

# 8. Conectividad SSH
Write-Host "[8/8] Verificando conectividad SSH..." -NoNewline
try {
    $connection = Test-NetConnection -ComputerName 3.88.180.221 -Port 22 -WarningAction SilentlyContinue
    if ($connection.TcpTestSucceeded) {
        Write-Host " OK (puerto 22 abierto)" -ForegroundColor Green
        $checks += $true
    } else {
        Write-Host " FALLO (puerto 22 no accesible)" -ForegroundColor Red
        $checks += $false
    }
} catch {
    Write-Host " FALLO" -ForegroundColor Red
    $checks += $false
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan

$passed = ($checks | Where-Object { $_ -eq $true }).Count
$total = $checks.Count

if ($passed -eq $total) {
    Write-Host "RESULTADO: $passed/$total VERIFICACIONES EXITOSAS" -ForegroundColor Green
    Write-Host ""
    Write-Host "Todo esta listo para el despliegue!" -ForegroundColor Green
    Write-Host ""
    Write-Host "SIGUIENTE PASO:" -ForegroundColor Cyan
    Write-Host "1. Abrir Git Bash o PowerShell con OpenSSH" -ForegroundColor White
    Write-Host "2. Ejecutar: ssh -i django-backend-key.pem ubuntu@3.88.180.221" -ForegroundColor Yellow
    Write-Host "3. Dentro del servidor, ejecutar: ./deploy_commands.sh" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "O ejecuta el monitor completo:" -ForegroundColor Cyan
    Write-Host "   .\monitor_aws.ps1" -ForegroundColor Yellow
} else {
    Write-Host "RESULTADO: $passed/$total VERIFICACIONES EXITOSAS" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Algunas verificaciones fallaron." -ForegroundColor Yellow
    Write-Host "Revisa los errores arriba antes de continuar." -ForegroundColor Yellow
}

Write-Host "============================================" -ForegroundColor Cyan
```

---

## 📊 Resultado Esperado

Si todo está correcto, deberías ver:

```
============================================
VERIFICACION PRE-DESPLIEGUE
============================================

[1/8] Verificando AWS CLI... OK
[2/8] Verificando EC2... OK (running)
[3/8] Verificando IP publica... OK (3.88.180.221)
[4/8] Verificando RDS... OK (available)
[5/8] Verificando endpoint RDS... OK
[6/8] Verificando clave SSH... OK (django-backend-key.pem existe)
[7/8] Verificando script de despliegue... OK (deploy_commands.sh existe)
[8/8] Verificando conectividad SSH... OK (puerto 22 abierto)

============================================
RESULTADO: 8/8 VERIFICACIONES EXITOSAS

Todo esta listo para el despliegue!

SIGUIENTE PASO:
1. Abrir Git Bash o PowerShell con OpenSSH
2. Ejecutar: ssh -i django-backend-key.pem ubuntu@3.88.180.221
3. Dentro del servidor, ejecutar: ./deploy_commands.sh

O ejecuta el monitor completo:
   .\monitor_aws.ps1
============================================
```

---

## ⚠️ Si Alguna Verificación Falla

### EC2 no está "running"
```powershell
# Iniciar la instancia
aws ec2 start-instances --instance-ids i-05700893150f99361

# Esperar 1 minuto y verificar nuevamente
Start-Sleep -Seconds 60
aws ec2 describe-instances --instance-ids i-05700893150f99361 --query "Reservations[0].Instances[0].State.Name"
```

### RDS no está "available"
```powershell
# Simplemente esperar, RDS tarda 5-10 minutos en estar disponible
# Ejecutar el monitor cada 2 minutos:
.\monitor_aws.ps1
```

### Puerto 22 no accesible
```powershell
# Verificar Security Group
aws ec2 describe-security-groups --group-ids sg-0cc0c93c58aedcd87

# Agregar regla SSH si no existe
aws ec2 authorize-security-group-ingress --group-id sg-0cc0c93c58aedcd87 --protocol tcp --port 22 --cidr 0.0.0.0/0
```

---

## 🎯 Después de Verificar

Si todas las verificaciones pasan, procede con:

1. **Leer**: `INSTRUCCIONES_CONEXION_SSH.md` para conectarte al servidor
2. **Ejecutar**: El script de despliegue en el servidor
3. **Verificar**: Que la aplicación funciona en http://3.88.180.221/api/

---

**¡Todo está listo para desplegar!** 🚀
