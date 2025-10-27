# 🔌 CONECTARSE AL SERVIDOR EC2 DESDE WINDOWS

## 📋 Información del Servidor

- **IP Pública**: `3.88.180.221`
- **Usuario**: `ubuntu`
- **Clave SSH**: `django-backend-key.pem` (en este directorio)

---

## Método 1: Git Bash (Recomendado - Más Fácil)

### 1️⃣ Descargar Git para Windows
Si no lo tienes instalado:
- Descargar de: https://git-scm.com/download/win
- Instalar con opciones por defecto

### 2️⃣ Abrir Git Bash
1. Click derecho en el Escritorio o carpeta del proyecto
2. Seleccionar **"Git Bash Here"**

### 3️⃣ Navegar a este directorio
```bash
cd "/c/Users/asus/Documents/SISTEMAS DE INFORMACION 2/segundo examen SI2/backend_2ex"
```

### 4️⃣ Configurar permisos de la clave
```bash
chmod 400 django-backend-key.pem
```

### 5️⃣ Conectarse al servidor
```bash
ssh -i django-backend-key.pem ubuntu@3.88.180.221
```

Si aparece un mensaje sobre autenticidad del host, escribir `yes` y presionar Enter.

### 6️⃣ ¡Ya estás dentro del servidor! Ahora ejecuta:
```bash
# Descargar el script de despliegue desde tu repositorio
wget https://raw.githubusercontent.com/Camila-V1/backend_2ex/main/deploy_commands.sh

# O crear el archivo manualmente
nano deploy_commands.sh
# (Copiar y pegar el contenido de deploy_commands.sh)

# Dar permisos de ejecución
chmod +x deploy_commands.sh

# Ejecutar el despliegue
./deploy_commands.sh
```

---

## Método 2: PowerShell con OpenSSH

### 1️⃣ Verificar si OpenSSH está instalado
```powershell
Get-Command ssh
```

Si aparece un error, instalar OpenSSH:
1. Configuración → Aplicaciones → Características opcionales
2. Agregar una característica → OpenSSH Client

### 2️⃣ Configurar permisos de la clave
```powershell
# Quitar herencia de permisos
icacls django-backend-key.pem /inheritance:r

# Dar permisos solo a tu usuario
icacls django-backend-key.pem /grant:r "$($env:USERNAME):(R)"
```

### 3️⃣ Conectarse al servidor
```powershell
ssh -i django-backend-key.pem ubuntu@3.88.180.221
```

### 4️⃣ Ejecutar el despliegue (igual que en Git Bash)
```bash
wget https://raw.githubusercontent.com/Camila-V1/backend_2ex/main/deploy_commands.sh
chmod +x deploy_commands.sh
./deploy_commands.sh
```

---

## Método 3: PuTTY (Si los anteriores no funcionan)

### 1️⃣ Descargar PuTTY
- Descargar de: https://www.putty.org/
- Descargar **PuTTY** y **PuTTYgen**

### 2️⃣ Convertir la clave .pem a .ppk
1. Abrir **PuTTYgen**
2. Click en "Load"
3. Cambiar filtro de archivos a "All Files (*.*)"
4. Seleccionar `django-backend-key.pem`
5. Click en "Save private key"
6. Guardar como `django-backend-key.ppk`

### 3️⃣ Conectarse con PuTTY
1. Abrir **PuTTY**
2. En "Host Name": `ubuntu@3.88.180.221`
3. En el menú izquierdo: `Connection → SSH → Auth → Credentials`
4. En "Private key file": Click "Browse" y seleccionar `django-backend-key.ppk`
5. (Opcional) Volver a "Session", poner un nombre en "Saved Sessions" y click "Save"
6. Click "Open"

### 4️⃣ Ejecutar el despliegue
Una vez conectado, ejecutar los mismos comandos:
```bash
wget https://raw.githubusercontent.com/Camila-V1/backend_2ex/main/deploy_commands.sh
chmod +x deploy_commands.sh
./deploy_commands.sh
```

---

## 🚨 Solución de Problemas

### Error: "Connection timed out"
**Causa**: El Security Group no permite SSH desde tu IP
**Solución**:
1. Ir a AWS Console → EC2 → Security Groups
2. Seleccionar `django-backend-sg`
3. Editar Inbound Rules
4. Verificar que el puerto 22 está abierto para `0.0.0.0/0`

### Error: "Permission denied (publickey)"
**Causa**: Permisos incorrectos de la clave
**Solución Git Bash**:
```bash
chmod 400 django-backend-key.pem
```

**Solución PowerShell**:
```powershell
icacls django-backend-key.pem /inheritance:r
icacls django-backend-key.pem /grant:r "$($env:USERNAME):(R)"
```

### Error: "Host key verification failed"
**Causa**: Primera vez conectándose al servidor
**Solución**:
Escribir `yes` cuando pregunte:
```
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
```

### Error: "No route to host"
**Causa**: La instancia EC2 no está en estado "running"
**Solución**:
```powershell
# Verificar estado de EC2
aws ec2 describe-instances --instance-ids i-05700893150f99361 --query "Reservations[0].Instances[0].State.Name"

# Si está "stopped", iniciarla
aws ec2 start-instances --instance-ids i-05700893150f99361
```

---

## 📋 Comandos Útiles una vez Conectado

### Ver estado de servicios
```bash
sudo systemctl status nginx
sudo systemctl status gunicorn
sudo systemctl status redis-server
```

### Ver logs
```bash
# Logs de Gunicorn (aplicación Django)
sudo journalctl -u gunicorn -f

# Logs de Nginx
sudo tail -f /var/log/nginx/error.log
```

### Reiniciar servicios
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Actualizar código desde GitHub
```bash
cd /var/www/django-backend
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

### Salir del servidor
```bash
exit
```

---

## 📦 Copiar Archivos al Servidor

### Desde Git Bash o PowerShell:
```bash
# Copiar archivo al servidor
scp -i django-backend-key.pem archivo.txt ubuntu@3.88.180.221:~/

# Copiar directorio completo
scp -r -i django-backend-key.pem carpeta/ ubuntu@3.88.180.221:~/

# Descargar archivo del servidor
scp -i django-backend-key.pem ubuntu@3.88.180.221:~/archivo.txt .
```

### Con PuTTY (usando WinSCP):
1. Descargar **WinSCP**: https://winscp.net/
2. Protocol: SFTP
3. Host: 3.88.180.221
4. User: ubuntu
5. Advanced → SSH → Authentication → Private key: Seleccionar `django-backend-key.ppk`
6. Login y arrastrar archivos

---

## ✅ Checklist de Conexión

- [ ] Descargar Git Bash o verificar que OpenSSH está instalado
- [ ] Navegar al directorio del proyecto
- [ ] Configurar permisos de `django-backend-key.pem`
- [ ] Conectarse con: `ssh -i django-backend-key.pem ubuntu@3.88.180.221`
- [ ] Una vez dentro, descargar `deploy_commands.sh`
- [ ] Ejecutar: `./deploy_commands.sh`
- [ ] Esperar 10-15 minutos a que complete el despliegue
- [ ] Probar en el navegador: http://3.88.180.221/api/

---

## 🎯 Próximos Pasos Después de Conectarse

1. ✅ **Ejecutar el script de despliegue**: `./deploy_commands.sh`
2. ✅ **Esperar a que termine** (10-15 minutos)
3. ✅ **Verificar servicios**: `sudo systemctl status nginx gunicorn`
4. ✅ **Probar la API**: Abrir http://3.88.180.221/api/ en el navegador
5. ✅ **Login al admin**: http://3.88.180.221/admin/ (admin/admin123)
6. ⚠️ **Cambiar contraseña**: `python manage.py changepassword admin`

---

**¡Buena suerte con el despliegue!** 🚀
