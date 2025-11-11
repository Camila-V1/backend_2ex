# 🚀 Guía Completa de Despliegue - E-commerce API

Esta es la guía maestra para desplegar tu aplicación Django E-commerce con sistema de devoluciones en producción.

---

## 📋 Índice de Documentación

### 📚 **Documentos Disponibles**

| Documento | Descripción | Cuándo Usarlo |
|-----------|-------------|---------------|
| **[COMANDOS_EXACTOS_DESPLIEGUE.md](./COMANDOS_EXACTOS_DESPLIEGUE.md)** | ✅ **EMPIEZA AQUÍ** - Comandos copy-paste listos para usar | Si ya tienes infraestructura AWS lista |
| **[DESPLIEGUE_AWS.md](./DESPLIEGUE_AWS.md)** | Guía paso a paso completa para AWS | Si es tu primera vez con AWS |
| **[RESUMEN_DESPLIEGUE_AWS.md](./RESUMEN_DESPLIEGUE_AWS.md)** | Resumen ejecutivo del proceso | Para tener una visión general |
| **[VERIFICACION_PRE_DESPLIEGUE.md](./VERIFICACION_PRE_DESPLIEGUE.md)** | Checklist antes de desplegar | Antes de empezar el despliegue |
| **[CONFIGURACION_SERVIDOR.md](./CONFIGURACION_SERVIDOR.md)** | Configuración del servidor EC2 | Para configurar el servidor manualmente |
| **[RDS_ENDPOINT.txt](./RDS_ENDPOINT.txt)** | Endpoint de la base de datos | Referencia rápida |
| **[CREDENCIALES_ACCESO.txt](./CREDENCIALES_ACCESO.txt)** | Credenciales de acceso | ⚠️ PRIVADO - No subir a Git |

---

## 🎯 Rutas de Despliegue

### 🟢 **RUTA RÁPIDA** (Infraestructura Ya Configurada)

Si ya tienes:
- ✅ Cuenta AWS con EC2, RDS y S3 configurados
- ✅ Clave SSH (.pem)
- ✅ Base de datos PostgreSQL en RDS
- ✅ Security Groups configurados

**👉 Sigue: [COMANDOS_EXACTOS_DESPLIEGUE.md](./COMANDOS_EXACTOS_DESPLIEGUE.md)**

**Tiempo estimado:** 15-20 minutos

---

### 🟡 **RUTA COMPLETA** (Desde Cero)

Si es tu primera vez o necesitas crear todo:
- 🆕 Cuenta AWS nueva o sin infraestructura
- 🆕 No tienes EC2, RDS ni S3 configurados
- 🆕 Primera vez desplegando en la nube

**👉 Sigue: [DESPLIEGUE_AWS.md](./DESPLIEGUE_AWS.md)**

**Tiempo estimado:** 1-2 horas

---

### 🔴 **RUTA MANUAL** (Configuración Avanzada)

Si necesitas personalizar la configuración:
- ⚙️ Configuración específica de servidor
- ⚙️ Optimización de recursos
- ⚙️ Configuración manual de servicios

**👉 Sigue: [CONFIGURACION_SERVIDOR.md](./CONFIGURACION_SERVIDOR.md)**

**Tiempo estimado:** 2-3 horas

---

## 📊 Comparativa de Opciones de Despliegue

| Opción | Complejidad | Costo Mensual | Escalabilidad | Recomendado Para |
|--------|-------------|---------------|---------------|------------------|
| **AWS EC2 + RDS** | Media | $24/mes* | Alta | Producción seria |
| **Heroku** | Baja | $25-50/mes | Media | Prototipos rápidos |
| **DigitalOcean** | Media | $12-24/mes | Media | Startups pequeñas |
| **Railway** | Baja | $5-20/mes | Baja | Desarrollo/Testing |
| **Local + ngrok** | Muy Baja | Gratis | Muy Baja | Solo demos |

*Después del primer año. Primer año con Free Tier: ~$0.12/mes

---

## 🏗️ Arquitectura de la Aplicación

```
Internet
    ↓
[Nginx] ← Puerto 80 (HTTP)
    ↓
[Gunicorn] ← WSGI Server (3 workers)
    ↓
[Django App] ← Lógica de negocio
    ↓
    ├─→ [PostgreSQL RDS] ← Base de datos
    ├─→ [Redis] ← Cache & Celery
    ├─→ [S3 Bucket] ← Archivos estáticos
    └─→ [SMTP Gmail] ← Emails
```

---

## ✅ Pre-requisitos Técnicos

### 🖥️ **En tu Computadora (Windows)**

- [ ] **Git** instalado
  - Descargar: https://git-scm.com/download/win
- [ ] **Python 3.10+** instalado
  - Verificar: `python --version`
- [ ] **Repositorio clonado** localmente
  - `git clone https://github.com/Camila-V1/backend_2ex.git`
- [ ] **PowerShell** o **Git Bash**

### ☁️ **En AWS**

- [ ] **Cuenta AWS** activa
  - Crear en: https://aws.amazon.com/
- [ ] **Tarjeta de crédito** registrada
  - Para verificación (cargos mínimos con Free Tier)
- [ ] **Usuario IAM** con permisos
  - EC2FullAccess, RDSFullAccess, S3FullAccess
- [ ] **AWS CLI** instalado y configurado
  - Verificar: `aws --version`

### 🔐 **Credenciales Necesarias**

- [ ] **AWS Access Keys** (Access Key ID + Secret)
- [ ] **SSH Key Pair** (.pem file)
- [ ] **RDS Credentials** (username, password)
- [ ] **Gmail App Password** (para emails)
- [ ] **Stripe Keys** (opcional, para pagos)

---

## 🎓 Pasos de Despliegue (Resumen)

### **Fase 1: Preparación** (15 min)
1. ✅ Verificar cuenta AWS y credenciales
2. ✅ Clonar repositorio en local
3. ✅ Instalar AWS CLI
4. ✅ Configurar usuario IAM
5. ✅ Generar SSH key pair

### **Fase 2: Infraestructura** (30 min)
6. ✅ Crear instancia EC2 (t3.micro)
7. ✅ Crear base de datos RDS (PostgreSQL)
8. ✅ Crear bucket S3
9. ✅ Configurar Security Groups
10. ✅ Asignar Elastic IP (opcional)

### **Fase 3: Configuración Servidor** (20 min)
11. ✅ Conectarse por SSH
12. ✅ Instalar dependencias (Python, Nginx, PostgreSQL client)
13. ✅ Clonar repositorio en servidor
14. ✅ Crear entorno virtual
15. ✅ Configurar variables de entorno (.env)

### **Fase 4: Base de Datos** (10 min)
16. ✅ Crear base de datos en RDS
17. ✅ Ejecutar migraciones
18. ✅ Crear superusuario
19. ✅ Poblar datos de prueba (opcional)

### **Fase 5: Servicios Web** (15 min)
20. ✅ Configurar Gunicorn
21. ✅ Configurar Nginx
22. ✅ Configurar Redis
23. ✅ Recolectar archivos estáticos

### **Fase 6: Verificación** (10 min)
24. ✅ Probar API: `http://TU_IP/api/`
25. ✅ Probar Admin: `http://TU_IP/admin/`
26. ✅ Verificar logs: `journalctl -u gunicorn`
27. ✅ Probar endpoints principales

---

## 📦 Componentes del Sistema

### **Backend (Django)**
- ✅ API REST con Django REST Framework
- ✅ Autenticación JWT (Simple JWT)
- ✅ Sistema de usuarios con roles (CLIENTE, MANAGER, ADMIN)
- ✅ Gestión de productos y categorías
- ✅ Sistema de órdenes y carrito
- ✅ **Sistema de devoluciones** (módulo principal)
- ✅ Billetera virtual
- ✅ Sistema de garantías
- ✅ Auditoría de acciones
- ✅ Reportes en PDF
- ✅ Notificaciones por email

### **Base de Datos (PostgreSQL)**
- ✅ RDS db.t3.micro
- ✅ 20GB almacenamiento
- ✅ Backups automáticos
- ✅ Multi-AZ para alta disponibilidad (opcional)

### **Almacenamiento (S3)**
- ✅ Archivos estáticos (CSS, JS)
- ✅ Archivos de medios (imágenes)
- ✅ Reportes generados (PDFs)
- ✅ Acceso público configurado

### **Cache & Tareas (Redis)**
- ✅ Cache de sesiones
- ✅ Celery para tareas asíncronas
- ✅ Rate limiting

### **Servidor Web**
- ✅ Nginx como proxy inverso
- ✅ Gunicorn como WSGI server
- ✅ Systemd para gestión de servicios

---

## 🔒 Seguridad Implementada

### **A Nivel de Aplicación**
- ✅ Autenticación JWT con tokens
- ✅ Permisos por rol (RBAC)
- ✅ Validación de entrada de datos
- ✅ Protección CSRF
- ✅ Rate limiting en endpoints
- ✅ Logs de auditoría

### **A Nivel de Infraestructura**
- ✅ Security Groups configurados
  - Puerto 80 (HTTP) abierto
  - Puerto 22 (SSH) restringido a tu IP
  - Puerto 5432 (PostgreSQL) solo desde EC2
- ✅ RDS en subnet privada
- ✅ Credenciales en variables de entorno
- ✅ SSL/TLS para conexión a RDS
- ✅ IAM roles con permisos mínimos

### **Recomendaciones Adicionales**
- 🔐 Cambiar contraseña del admin después del despliegue
- 🔐 Configurar HTTPS con Let's Encrypt (Certbot)
- 🔐 Habilitar WAF (Web Application Firewall)
- 🔐 Configurar CloudWatch para monitoreo
- 🔐 Habilitar MFA en cuenta AWS

---

## 💰 Costos Estimados

### **Primer Año (con AWS Free Tier)**

| Servicio | Costo Mensual | Costo Anual |
|----------|---------------|-------------|
| EC2 t3.micro | $0 | $0 |
| RDS db.t3.micro | $0 | $0 |
| S3 (5GB) | $0.12 | $1.44 |
| Data Transfer | $0.50 | $6.00 |
| **TOTAL** | **$0.62** | **$7.44** |

### **Después del Primer Año**

| Servicio | Costo Mensual | Costo Anual |
|----------|---------------|-------------|
| EC2 t3.micro | $8.50 | $102 |
| RDS db.t3.micro | $15.00 | $180 |
| S3 (5GB) | $0.12 | $1.44 |
| Data Transfer | $0.50 | $6.00 |
| **TOTAL** | **$24.12** | **$289.44** |

### **Optimización de Costos**
- 💡 Usar Reserved Instances (ahorro del 30-50%)
- 💡 Apagar instancias en horarios no productivos
- 💡 Usar S3 Intelligent-Tiering
- 💡 Configurar alarmas de billing

**Monitorear costos:** https://console.aws.amazon.com/billing/

---

## 🧪 Poblado de Datos de Prueba

### **Ejecutar Poblador Completo**

Una vez desplegado, puedes poblar la base de datos con datos realistas:

```bash
# Conectarse al servidor
ssh -i django-backend-key.pem ubuntu@TU_IP

# Activar entorno virtual
cd /var/www/django-backend
source venv/bin/activate

# Ejecutar poblador
python seed_complete_database.py

# Responder "SI" para limpiar BD y poblar
```

**Datos generados:**
- ✅ 10 categorías de productos
- ✅ 37 productos con precios ($499 - $34,999)
- ✅ 18 usuarios (10 clientes, 6 managers, 2 admins)
- ✅ 65 órdenes en diferentes estados
- ✅ 35 devoluciones en todos los estados
- ✅ 7 billeteras con saldo
- ✅ 34 transacciones

**Credenciales de prueba:**
- Cliente: `juan_cliente / password123`
- Manager: `carlos_manager / manager123`
- Admin: `admin / admin123`

Ver: [CREDENCIALES_SISTEMA.md](./CREDENCIALES_SISTEMA.md)

---

## 📊 Endpoints Disponibles

### **Autenticación**
- `POST /api/users/login/` - Login
- `POST /api/users/refresh/` - Refresh token
- `GET /api/users/me/` - Perfil del usuario

### **Productos**
- `GET /api/products/` - Listar productos
- `GET /api/products/{id}/` - Detalle de producto
- `GET /api/categories/` - Listar categorías

### **Órdenes**
- `POST /api/orders/` - Crear orden
- `GET /api/orders/my_orders/` - Mis órdenes
- `GET /api/orders/{id}/` - Detalle de orden

### **Devoluciones** ⭐ (Módulo Principal)
- `POST /api/returns/` - Solicitar devolución
- `GET /api/returns/` - Listar devoluciones
- `GET /api/returns/my_returns/` - Mis devoluciones
- `POST /api/returns/{id}/approve/` - Aprobar (MANAGER)
- `POST /api/returns/{id}/reject/` - Rechazar (MANAGER)
- `POST /api/returns/{id}/request_physical_evaluation/` - Evaluar (MANAGER)
- `POST /api/returns/{id}/cancel/` - Cancelar (CLIENTE)

### **Billetera Virtual**
- `GET /api/wallet/balance/` - Ver saldo
- `GET /api/wallet/transactions/` - Historial
- `GET /api/wallet/statistics/` - Estadísticas
- `POST /api/wallet/withdraw/` - Retirar fondos

### **Auditoría**
- `GET /api/audit/logs/` - Logs del sistema

### **Admin Panel**
- `GET /admin/` - Panel de administración Django

Ver esquema completo: [API_SCHEMA.md](./API_SCHEMA.md)

---

## 🔧 Comandos Útiles Post-Despliegue

### **Ver logs en tiempo real**
```bash
sudo journalctl -u gunicorn -f
sudo tail -f /var/log/nginx/error.log
```

### **Reiniciar servicios**
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
sudo systemctl restart redis-server
```

### **Actualizar código desde GitHub**
```bash
cd /var/www/django-backend
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

### **Hacer backup de la base de datos**
```bash
PGPASSWORD=TU_PASSWORD pg_dump -h TU_RDS_ENDPOINT -U dbadmin django_db > backup_$(date +%Y%m%d).sql
```

### **Restaurar backup**
```bash
PGPASSWORD=TU_PASSWORD psql -h TU_RDS_ENDPOINT -U dbadmin django_db < backup_20241110.sql
```

### **Ver estado de servicios**
```bash
sudo systemctl status nginx
sudo systemctl status gunicorn
sudo systemctl status redis-server
```

---

## 🐛 Solución de Problemas Comunes

### **Error 502 Bad Gateway**
```bash
# Verificar Gunicorn
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -n 50

# Verificar socket
ls -la /var/www/django-backend/gunicorn.sock

# Reiniciar
sudo systemctl restart gunicorn nginx
```

### **Error de conexión a RDS**
```bash
# Verificar connectivity
nc -zv TU_RDS_ENDPOINT 5432

# Verificar Security Group
# Debe permitir tráfico desde EC2 en puerto 5432

# Probar conexión manual
PGPASSWORD=TU_PASSWORD psql -h TU_RDS_ENDPOINT -U dbadmin -d postgres -c "SELECT 1;"
```

### **Archivos estáticos no cargan**
```bash
# Verificar S3
python manage.py collectstatic --noinput

# Ver configuración
cat .env | grep S3

# Verificar permisos de bucket S3
# Debe tener política pública de lectura
```

### **Emails no se envían**
```bash
# Verificar configuración SMTP
cat .env | grep EMAIL

# Probar en shell
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])
```

---

## 📚 Documentación Adicional

### **Sistema de Devoluciones**
- [README_DELIVERIES.md](./README_DELIVERIES.md) - Documentación del módulo
- [FLUJO_DEVOLUCIONES_SIMPLE.md](./FLUJO_DEVOLUCIONES_SIMPLE.md) - Flujo simplificado
- [SISTEMA_DEVOLUCIONES.md](./SISTEMA_DEVOLUCIONES.md) - Documentación técnica

### **Frontend**
- [frontend_docs/](./frontend_docs/) - Documentación completa para el frontend
  - [00_INDICE.md](./frontend_docs/00_INDICE.md) - Índice general
  - [01_AUTENTICACION.md](./frontend_docs/01_AUTENTICACION.md) - Sistema de autenticación
  - [03_DEVOLUCIONES.md](./frontend_docs/03_DEVOLUCIONES.md) - Integración de devoluciones
  - [04_BILLETERA_VIRTUAL.md](./frontend_docs/04_BILLETERA_VIRTUAL.md) - Billetera virtual

### **Funcionalidades por Rol**
- [FUNCIONALIDADES_POR_ROL.md](./FUNCIONALIDADES_POR_ROL.md) - Permisos y capacidades por rol
- [CREDENCIALES_SISTEMA.md](./CREDENCIALES_SISTEMA.md) - Credenciales de prueba

### **API**
- [API_SCHEMA.md](./API_SCHEMA.md) - Esquema completo de la API
- [API_SCHEMA.yaml](./API_SCHEMA.yaml) - OpenAPI 3.0 spec
- [API_SCHEMA.json](./API_SCHEMA.json) - JSON schema

---

## ✅ Checklist de Despliegue

### **Antes de Empezar**
- [ ] Revisar [VERIFICACION_PRE_DESPLIEGUE.md](./VERIFICACION_PRE_DESPLIEGUE.md)
- [ ] Tener cuenta AWS activa
- [ ] Instalar AWS CLI y configurar credenciales
- [ ] Tener repositorio actualizado en GitHub

### **Durante el Despliegue**
- [ ] Crear infraestructura AWS (EC2, RDS, S3)
- [ ] Configurar Security Groups
- [ ] Conectarse por SSH al servidor
- [ ] Clonar repositorio y configurar entorno
- [ ] Ejecutar migraciones de base de datos
- [ ] Configurar Gunicorn y Nginx
- [ ] Recolectar archivos estáticos

### **Después del Despliegue**
- [ ] Probar API: `http://TU_IP/api/`
- [ ] Probar Admin: `http://TU_IP/admin/`
- [ ] Cambiar contraseña del admin
- [ ] Poblar datos de prueba (opcional)
- [ ] Configurar monitoreo de costos
- [ ] Documentar credenciales en lugar seguro
- [ ] Configurar HTTPS (Certbot)
- [ ] Configurar backups automáticos

---

## 🎯 Próximos Pasos

### **Mejoras de Producción**
1. ⚡ Configurar **HTTPS** con Let's Encrypt
   - Tutorial: https://certbot.eff.org/
2. 📊 Configurar **CloudWatch** para logs y métricas
3. 🔔 Configurar **alarmas** de billing y performance
4. 🔐 Habilitar **MFA** en cuenta AWS
5. 🔄 Configurar **backups automáticos** de RDS
6. 🚀 Configurar **CD/CI** con GitHub Actions

### **Optimizaciones**
1. ⚡ Implementar cache con Redis
2. ⚡ Configurar CDN (CloudFront) para estáticos
3. ⚡ Optimizar consultas de base de datos
4. ⚡ Implementar compression en Nginx
5. ⚡ Configurar Auto Scaling (opcional)

### **Monitoreo**
1. 📊 Configurar Sentry para errores
2. 📊 Implementar New Relic o DataDog
3. 📊 Configurar uptime monitoring
4. 📊 Analítica de uso de API

---

## 📞 Soporte y Recursos

### **Documentación Oficial**
- AWS: https://docs.aws.amazon.com/
- Django: https://docs.djangoproject.com/
- DRF: https://www.django-rest-framework.org/
- Nginx: https://nginx.org/en/docs/
- PostgreSQL: https://www.postgresql.org/docs/

### **Comunidad**
- Stack Overflow: https://stackoverflow.com/questions/tagged/django
- Reddit: r/django, r/aws
- Discord: Django Discord Server

### **Contacto del Proyecto**
- **Repositorio:** https://github.com/Camila-V1/backend_2ex
- **Issues:** https://github.com/Camila-V1/backend_2ex/issues

---

## 🎉 ¡Felicidades!

Si llegaste hasta aquí y completaste el despliegue, ¡felicidades! 🎊

Ahora tienes una aplicación E-commerce completa corriendo en AWS con:
- ✅ API REST profesional
- ✅ Sistema de devoluciones completo
- ✅ Billetera virtual
- ✅ Base de datos en la nube
- ✅ Almacenamiento de archivos
- ✅ Sistema de autenticación
- ✅ Panel de administración

**¡A seguir construyendo! 🚀**

---

**Última actualización:** 10 de noviembre de 2025  
**Versión del sistema:** 1.0  
**Autor:** Sistema E-commerce con Devoluciones
