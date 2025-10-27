# 🚀 Guía Completa de Despliegue en AWS

## 📋 Requisitos Previos
- ✅ Cuenta AWS activa
- ✅ Tarjeta de crédito registrada en AWS
- ✅ Acceso a la consola AWS

---

## 🔧 PASO 1: Instalar AWS CLI en Windows

### 1.1 Descargar e instalar AWS CLI

```powershell
# Opción A: Usando Windows Installer (Recomendado)
# Descarga desde: https://awscli.amazonaws.com/AWSCLIV2.msi
# Ejecuta el instalador y sigue las instrucciones

# Opción B: Usando winget (si tienes Windows 11)
winget install Amazon.AWSCLI

# Opción C: Usando Chocolatey (si lo tienes instalado)
choco install awscli
```

### 1.2 Verificar instalación

```powershell
aws --version
# Debe mostrar: aws-cli/2.x.x Python/3.x.x Windows/10...
```

---

## 🔑 PASO 2: Crear Usuario IAM y Configurar Credenciales

### 2.1 Crear usuario IAM desde la consola AWS

**IMPORTANTE: Este paso DEBE hacerse desde la consola web de AWS primero**

1. **Inicia sesión en AWS Console:** https://console.aws.amazon.com/
2. **Ir a IAM:** Busca "IAM" en el buscador superior
3. **Crear usuario:**
   - Click en "Users" (Usuarios)
   - Click en "Add users" (Agregar usuarios)
   - Nombre de usuario: `django-deploy-user`
   - Tipo de acceso: ✅ **Access key - Programmatic access**
   - Click "Next"

4. **Asignar permisos:**
   - Selecciona: "Attach policies directly" (Adjuntar políticas directamente)
   - Marca estas políticas:
     - ✅ `AmazonEC2FullAccess`
     - ✅ `AmazonRDSFullAccess`
     - ✅ `AmazonS3FullAccess`
     - ✅ `AmazonVPCFullAccess`
     - ✅ `IAMReadOnlyAccess`
   - Click "Next"

5. **Revisar y crear:**
   - Click "Create user"

6. **⚠️ IMPORTANTE - Guardar credenciales:**
   ```
   Access key ID: AKIA...
   Secret access key: wJal...
   ```
   **¡COPIA ESTAS CREDENCIALES AHORA! No podrás verlas de nuevo.**

### 2.2 Configurar AWS CLI con tus credenciales

```powershell
# En PowerShell, ejecuta:
aws configure

# Te pedirá:
AWS Access Key ID [None]: AKIA... (pega tu Access Key)
AWS Secret Access Key [None]: wJal... (pega tu Secret Key)
Default region name [None]: us-east-1
Default output format [None]: json
```

### 2.3 Verificar configuración

```powershell
# Verificar que las credenciales funcionan
aws sts get-caller-identity

# Debe mostrar:
# {
#     "UserId": "AIDA...",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/django-deploy-user"
# }
```

---

## 🔐 PASO 3: Crear Par de Claves SSH (Key Pair)

```powershell
# Crear directorio para claves
mkdir C:\Users\asus\.aws\keys
cd C:\Users\asus\.aws\keys

# Crear key pair
aws ec2 create-key-pair `
  --key-name django-backend-key `
  --query 'KeyMaterial' `
  --output text `
  --region us-east-1 > django-backend-key.pem

# Verificar que se creó
dir django-backend-key.pem
```

**Resultado esperado:**
```
django-backend-key.pem (archivo con tu clave privada)
```

---

## 🌐 PASO 4: Crear Security Group (Firewall)

```powershell
# Crear Security Group
aws ec2 create-security-group `
  --group-name django-backend-sg `
  --description "Security group for Django backend" `
  --region us-east-1

# Guardar el Security Group ID que te devuelve
# Ejemplo: sg-0123456789abcdef0
```

### 4.1 Configurar reglas de firewall

```powershell
# Obtener tu IP pública (para SSH seguro)
$MY_IP = (Invoke-WebRequest -Uri "https://api.ipify.org").Content
Write-Host "Tu IP pública es: $MY_IP"

# Obtener el Security Group ID
$SG_ID = aws ec2 describe-security-groups `
  --filters "Name=group-name,Values=django-backend-sg" `
  --query "SecurityGroups[0].GroupId" `
  --output text `
  --region us-east-1

Write-Host "Security Group ID: $SG_ID"

# Regla 1: SSH desde tu IP (puerto 22)
aws ec2 authorize-security-group-ingress `
  --group-id $SG_ID `
  --protocol tcp `
  --port 22 `
  --cidr "$MY_IP/32" `
  --region us-east-1

# Regla 2: HTTP público (puerto 80)
aws ec2 authorize-security-group-ingress `
  --group-id $SG_ID `
  --protocol tcp `
  --port 80 `
  --cidr 0.0.0.0/0 `
  --region us-east-1

# Regla 3: HTTPS público (puerto 443)
aws ec2 authorize-security-group-ingress `
  --group-id $SG_ID `
  --protocol tcp `
  --port 443 `
  --cidr 0.0.0.0/0 `
  --region us-east-1

# Regla 4: Django dev server (puerto 8000) - Temporal
aws ec2 authorize-security-group-ingress `
  --group-id $SG_ID `
  --protocol tcp `
  --port 8000 `
  --cidr 0.0.0.0/0 `
  --region us-east-1

Write-Host "✅ Security Group configurado"
```

---

## 💻 PASO 5: Lanzar Instancia EC2

```powershell
# Obtener la AMI ID de Ubuntu 22.04 más reciente
$AMI_ID = aws ec2 describe-images `
  --owners 099720109477 `
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" `
            "Name=state,Values=available" `
  --query "Images | sort_by(@, &CreationDate) | [-1].ImageId" `
  --output text `
  --region us-east-1

Write-Host "AMI ID: $AMI_ID"

# Crear script de inicialización
$USER_DATA = @"
#!/bin/bash
apt-get update
apt-get install -y python3-pip python3-venv nginx postgresql-client git
"@

# Guardar en archivo temporal
$USER_DATA | Out-File -FilePath user-data.txt -Encoding ASCII

# Lanzar instancia EC2
aws ec2 run-instances `
  --image-id $AMI_ID `
  --instance-type t2.micro `
  --key-name django-backend-key `
  --security-group-ids $SG_ID `
  --user-data file://user-data.txt `
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=django-backend-server}]" `
  --region us-east-1

Write-Host "✅ Instancia EC2 lanzándose..."
Write-Host "⏳ Espera 2-3 minutos para que esté lista"
```

### 5.1 Obtener IP pública de la instancia

```powershell
# Esperar 2 minutos
Start-Sleep -Seconds 120

# Obtener la IP pública
$EC2_IP = aws ec2 describe-instances `
  --filters "Name=tag:Name,Values=django-backend-server" `
            "Name=instance-state-name,Values=running" `
  --query "Reservations[0].Instances[0].PublicIpAddress" `
  --output text `
  --region us-east-1

Write-Host "🌐 IP Pública del servidor: $EC2_IP"
```

---

## 🗄️ PASO 6: Crear Base de Datos RDS (PostgreSQL)

```powershell
# Crear DB Subnet Group (requiere VPC por defecto)
$VPC_ID = aws ec2 describe-vpcs `
  --filters "Name=is-default,Values=true" `
  --query "Vpcs[0].VpcId" `
  --output text `
  --region us-east-1

# Obtener subnets
$SUBNET_IDS = aws ec2 describe-subnets `
  --filters "Name=vpc-id,Values=$VPC_ID" `
  --query "Subnets[*].SubnetId" `
  --output text `
  --region us-east-1

Write-Host "Subnets: $SUBNET_IDS"

# Crear DB Subnet Group
aws rds create-db-subnet-group `
  --db-subnet-group-name django-db-subnet `
  --db-subnet-group-description "Subnet group for Django DB" `
  --subnet-ids $SUBNET_IDS.Split() `
  --region us-east-1

# Crear Security Group para RDS
aws ec2 create-security-group `
  --group-name django-rds-sg `
  --description "Security group for RDS PostgreSQL" `
  --vpc-id $VPC_ID `
  --region us-east-1

$RDS_SG_ID = aws ec2 describe-security-groups `
  --filters "Name=group-name,Values=django-rds-sg" `
  --query "SecurityGroups[0].GroupId" `
  --output text `
  --region us-east-1

# Permitir conexión desde EC2
aws ec2 authorize-security-group-ingress `
  --group-id $RDS_SG_ID `
  --protocol tcp `
  --port 5432 `
  --source-group $SG_ID `
  --region us-east-1

# Crear instancia RDS PostgreSQL
aws rds create-db-instance `
  --db-instance-identifier django-backend-db `
  --db-instance-class db.t3.micro `
  --engine postgres `
  --engine-version 15.3 `
  --master-username dbadmin `
  --master-user-password "ChangeMeNow123!" `
  --allocated-storage 20 `
  --db-subnet-group-name django-db-subnet `
  --vpc-security-group-ids $RDS_SG_ID `
  --publicly-accessible false `
  --backup-retention-period 7 `
  --region us-east-1

Write-Host "✅ Base de datos RDS creándose..."
Write-Host "⏳ Esto toma 5-10 minutos"
```

### 6.1 Esperar a que RDS esté disponible

```powershell
# Esperar hasta que esté disponible (esto puede tardar)
Write-Host "⏳ Esperando a que RDS esté disponible..."

do {
    $DB_STATUS = aws rds describe-db-instances `
      --db-instance-identifier django-backend-db `
      --query "DBInstances[0].DBInstanceStatus" `
      --output text `
      --region us-east-1
    
    Write-Host "Estado actual: $DB_STATUS"
    
    if ($DB_STATUS -ne "available") {
        Start-Sleep -Seconds 30
    }
} while ($DB_STATUS -ne "available")

Write-Host "✅ Base de datos disponible!"

# Obtener endpoint de la base de datos
$DB_ENDPOINT = aws rds describe-db-instances `
  --db-instance-identifier django-backend-db `
  --query "DBInstances[0].Endpoint.Address" `
  --output text `
  --region us-east-1

Write-Host "🗄️ DB Endpoint: $DB_ENDPOINT"
```

---

## 📦 PASO 7: Crear Bucket S3 para Archivos Estáticos

```powershell
# Generar nombre único para el bucket
$BUCKET_NAME = "django-backend-$(Get-Random -Minimum 1000 -Maximum 9999)"

# Crear bucket S3
aws s3api create-bucket `
  --bucket $BUCKET_NAME `
  --region us-east-1

# Configurar acceso público para archivos estáticos
aws s3api put-public-access-block `
  --bucket $BUCKET_NAME `
  --public-access-block-configuration `
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# Configurar política de bucket
$BUCKET_POLICY = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BUCKET_NAME/static/*"
    }
  ]
}
"@

$BUCKET_POLICY | Out-File -FilePath bucket-policy.json -Encoding ASCII

aws s3api put-bucket-policy `
  --bucket $BUCKET_NAME `
  --policy file://bucket-policy.json

Write-Host "✅ Bucket S3 creado: $BUCKET_NAME"
```

---

## 📝 PASO 8: Guardar Variables de Entorno

```powershell
# Crear archivo con todas las credenciales
$ENV_FILE = @"
# AWS Deployment Configuration
# Generated on $(Get-Date)

# EC2
EC2_PUBLIC_IP=$EC2_IP

# RDS Database
DB_HOST=$DB_ENDPOINT
DB_PORT=5432
DB_NAME=postgres
DB_USER=dbadmin
DB_PASSWORD=ChangeMeNow123!

# S3
S3_BUCKET_NAME=$BUCKET_NAME

# Security Group
SECURITY_GROUP_ID=$SG_ID
RDS_SECURITY_GROUP_ID=$RDS_SG_ID

# Key Pair
KEY_PAIR_NAME=django-backend-key
KEY_FILE=C:\Users\asus\.aws\keys\django-backend-key.pem

# Region
AWS_REGION=us-east-1
"@

$ENV_FILE | Out-File -FilePath aws-deployment-config.txt -Encoding UTF8

Write-Host "✅ Configuración guardada en: aws-deployment-config.txt"
```

---

## 🔌 PASO 9: Conectar al Servidor EC2

### 9.1 Configurar permisos de la clave SSH

```powershell
# Windows requiere configurar permisos manualmente
# Click derecho en django-backend-key.pem → Propiedades → Seguridad
# - Deshabilitar herencia
# - Eliminar todos los permisos excepto el tuyo
# O usar icacls:

icacls C:\Users\asus\.aws\keys\django-backend-key.pem /inheritance:r
icacls C:\Users\asus\.aws\keys\django-backend-key.pem /grant:r "$($env:USERNAME):(R)"
```

### 9.2 Conectar por SSH

```powershell
# Conectar al servidor
ssh -i C:\Users\asus\.aws\keys\django-backend-key.pem ubuntu@$EC2_IP
```

---

## 🚀 PASO 10: Configurar el Servidor (ejecutar en EC2)

Una vez conectado por SSH, ejecuta:

```bash
# Actualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar dependencias
sudo apt-get install -y \
    python3.10 \
    python3-pip \
    python3-venv \
    nginx \
    postgresql-client \
    git \
    supervisor

# Crear usuario para la aplicación
sudo useradd -m -s /bin/bash django
sudo su - django

# Clonar repositorio
cd /home/django
git clone https://github.com/Camila-V1/backend_2ex.git app
cd app

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary boto3 django-storages

# Configurar variables de entorno
cat > .env << EOF
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
DATABASE_URL=postgresql://dbadmin:ChangeMeNow123!@$DB_ENDPOINT:5432/postgres
ALLOWED_HOSTS=$EC2_IP,localhost

# Stripe
STRIPE_PUBLISHABLE_KEY=your_key_here
STRIPE_SECRET_KEY=your_key_here
STRIPE_WEBHOOK_SECRET=your_webhook_secret

# AWS S3
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_STORAGE_BUCKET_NAME=$BUCKET_NAME
AWS_S3_REGION_NAME=us-east-1

# Frontend
FRONTEND_URL=http://$EC2_IP:3000
EOF

# Migrar base de datos
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# Salir del usuario django
exit
```

---

## 🔧 PASO 11: Configurar Gunicorn

```bash
# Crear archivo de configuración de Gunicorn
sudo nano /etc/supervisor/conf.d/django-backend.conf
```

Contenido:
```ini
[program:django-backend]
command=/home/django/app/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 ecommerce_api.wsgi:application
directory=/home/django/app
user=django
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/django-backend.log
```

```bash
# Recargar supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start django-backend
sudo supervisorctl status
```

---

## 🌐 PASO 12: Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/django-backend
```

Contenido:
```nginx
server {
    listen 80;
    server_name $EC2_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/django/app/staticfiles/;
    }

    location /media/ {
        alias /home/django/app/media/;
    }
}
```

```bash
# Activar sitio
sudo ln -s /etc/nginx/sites-available/django-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## ✅ PASO 13: Verificar Despliegue

```powershell
# Desde tu PC local, verifica que funciona:
curl http://$EC2_IP/api/
```

---

## 📊 Resumen de Costos Mensuales (Estimado)

- EC2 t2.micro: ~$8.50/mes
- RDS db.t3.micro: ~$15/mes
- S3: ~$0.50/mes (dependiendo del uso)
- **Total aproximado: $24/mes**

⚠️ **Capa gratuita de AWS:** Si es tu primera vez, tienes 12 meses gratis en muchos servicios.

---

## 🔒 Medidas de Seguridad Importantes

1. ✅ Cambiar contraseña de RDS después del despliegue
2. ✅ Configurar SSL/HTTPS con Let's Encrypt
3. ✅ Habilitar backups automáticos
4. ✅ Configurar CloudWatch para monitoreo
5. ✅ Restringir acceso SSH solo a tu IP

---

¿Empezamos con el PASO 1? 🚀
