# 📧 Configuración de Emails para Producción

## ✅ Estado Actual

El sistema de emails está **100% implementado y funcional**.

**En desarrollo:** Los emails se imprimen en la consola  
**En producción:** Se enviarán emails reales vía SMTP

---

## 🔧 Configuración para Producción

### **Opción 1: Gmail (Más Simple)**

#### 1. Crear una contraseña de aplicación en Gmail

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Seguridad → Verificación en dos pasos (debe estar activada)
3. Seguridad → Contraseñas de aplicaciones
4. Genera una contraseña para "Correo"
5. Copia la contraseña de 16 caracteres

#### 2. Configurar variables de entorno

Crea o edita el archivo `.env`:

```bash
# Cambiar a backend SMTP real
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# Configuración de Gmail
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx  # Contraseña de aplicación

# Email del remitente
DEFAULT_FROM_EMAIL=noreply@tudominio.com
ADMIN_EMAIL=admin@tudominio.com
EMAIL_SUBJECT_PREFIX=[SmartSales365] 
```

#### 3. Probar envío

```python
python manage.py shell

from django.core.mail import send_mail

send_mail(
    subject='Test Email',
    message='Si ves esto, los emails funcionan!',
    from_email='noreply@tudominio.com',
    recipient_list=['tu-email@gmail.com'],
    fail_silently=False,
)
```

---

### **Opción 2: SendGrid (Recomendado para Producción)**

#### 1. Crear cuenta en SendGrid

1. Registrarse en: https://sendgrid.com/
2. Verificar tu email
3. Plan gratuito: 100 emails/día

#### 2. Obtener API Key

1. Settings → API Keys
2. Create API Key
3. Full Access
4. Copiar el API Key (empieza con `SG.`)

#### 3. Instalar SendGrid

```bash
pip install sendgrid
pip freeze > requirements.txt
```

#### 4. Configurar variables de entorno

```bash
# Backend para SendGrid
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# Configuración de SendGrid
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey  # Literalmente "apikey"
EMAIL_HOST_PASSWORD=SG.tu_api_key_aqui

# Email del remitente (debe estar verificado en SendGrid)
DEFAULT_FROM_EMAIL=noreply@tudominio.com
ADMIN_EMAIL=admin@tudominio.com
```

---

### **Opción 3: AWS SES (Para Alto Volumen)**

```bash
# Configuración de AWS SES
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_aws_ses_username
EMAIL_HOST_PASSWORD=tu_aws_ses_password
DEFAULT_FROM_EMAIL=noreply@tudominio.com
```

---

## 📧 Emails Implementados

| Evento | Disparador | Destinatario | Plantilla |
|--------|-----------|--------------|-----------|
| Nueva solicitud | Cliente crea devolución | Managers/Admins | `send_new_return_notification_to_managers()` |
| En evaluación | Manager envía a evaluación | Cliente | `send_return_evaluation_started_notification()` |
| Aprobada | Manager aprueba | Cliente | `send_return_approved_notification()` |
| Rechazada | Manager rechaza | Cliente | `send_return_rejected_notification()` |

---

## 🧪 Testing en Producción

### Verificar que los emails se envían:

```bash
# 1. Crear devolución de prueba
curl -X POST http://tu-servidor.com/api/deliveries/returns/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "order_id": 1,
    "product_id": 1,
    "quantity": 1,
    "reason": "DEFECTIVE",
    "description": "Test"
  }'

# 2. Revisar logs del servidor
tail -f logs/django.log

# 3. Verificar email recibido
# Debería llegar a todos los managers
```

---

## 🎨 Personalizar Plantillas de Email

### Modificar `deliveries/email_utils.py`:

```python
def send_return_approved_notification(return_obj):
    subject = f"✅ Devolución Aprobada #{return_obj.id}"
    
    # Personalizar mensaje aquí
    message = f"""
Hola {return_obj.user.first_name},

Tu devolución ha sido aprobada.
Reembolso: ${return_obj.refund_amount}

Tu mensaje personalizado aquí...
"""
    
    send_mail(...)
```

---

## ⚠️ Troubleshooting

### Error: "SMTPAuthenticationError"
**Solución:** Verifica EMAIL_HOST_USER y EMAIL_HOST_PASSWORD

### Error: "SMTPServerDisconnected"
**Solución:** Verifica que EMAIL_PORT sea 587 y EMAIL_USE_TLS=True

### Error: "Connection refused"
**Solución:** Verifica que el servidor SMTP sea accesible desde tu servidor

### Emails no llegan (Gmail)
**Solución:** 
1. Verifica que la verificación en 2 pasos esté activada
2. Usa contraseña de aplicación, no tu contraseña normal
3. Revisa la carpeta de spam

### Emails no llegan (SendGrid)
**Solución:**
1. Verifica que el dominio del remitente esté verificado
2. Revisa el Dashboard de SendGrid para ver errores
3. Asegúrate de no exceder el límite de 100/día (plan gratuito)

---

## 📊 Monitoreo

### Ver emails enviados en desarrollo:
```bash
# Los emails se imprimen en la consola donde corre el servidor
python manage.py runserver
```

### Ver emails enviados en producción:

#### Con SendGrid:
1. Dashboard → Activity
2. Filtra por fecha
3. Ve entregas, aperturas, clics

#### Con Gmail:
1. Revisar "Enviados" en Gmail
2. Limitado a 500 emails/día

---

## 🔐 Seguridad

### ✅ Buenas Prácticas:

1. **Nunca commitees credenciales:**
   ```bash
   # ❌ MAL
   EMAIL_HOST_PASSWORD=mi_password_123
   
   # ✅ BIEN
   EMAIL_HOST_PASSWORD=config('EMAIL_HOST_PASSWORD')
   ```

2. **Usa variables de entorno:**
   ```python
   # En settings.py
   EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
   ```

3. **Valida emails antes de enviar:**
   ```python
   if not return_obj.user.email:
       print("⚠️  Usuario sin email")
       return
   ```

4. **Maneja excepciones:**
   ```python
   try:
       send_mail(...)
   except Exception as e:
       print(f"❌ Error: {str(e)}")
   ```

---

## 📈 Mejoras Futuras

### 1. **Emails HTML**
```python
from django.core.mail import EmailMultiAlternatives

email = EmailMultiAlternatives(subject, text_content, from_email, [to])
email.attach_alternative(html_content, "text/html")
email.send()
```

### 2. **Templates con Django**
```python
from django.template.loader import render_to_string

html_content = render_to_string('emails/return_approved.html', {
    'return': return_obj,
    'user': return_obj.user
})
```

### 3. **Cola de emails (Celery)**
```python
# Para no bloquear requests
@celery_app.task
def send_email_async(subject, message, to):
    send_mail(subject, message, DEFAULT_FROM_EMAIL, [to])
```

### 4. **Tracking de apertura**
- Implementar con SendGrid
- Agregar pixel de tracking
- Dashboard de estadísticas

---

## ✅ Checklist de Producción

- [ ] Variables de entorno configuradas en servidor
- [ ] EMAIL_BACKEND cambiado a SMTP
- [ ] Credenciales SMTP válidas
- [ ] Dominio de remitente verificado (si aplica)
- [ ] Email de prueba enviado exitosamente
- [ ] Emails no van a spam
- [ ] Logs monitoreados
- [ ] Límites de envío verificados
- [ ] Excepciones manejadas correctamente
- [ ] DEFAULT_FROM_EMAIL con dominio real

---

## 🎯 Resumen

**Estado Actual:** ✅ FUNCIONAL (modo console)  
**Para Producción:** Cambiar 3 variables en `.env`  
**Tiempo de configuración:** 10-15 minutos  
**Costo:** $0 (SendGrid Free Tier: 100/día)

---

## 📞 Soporte

**Documentación oficial:**
- Gmail: https://support.google.com/mail/answer/185833
- SendGrid: https://docs.sendgrid.com/
- Django: https://docs.djangoproject.com/en/5.2/topics/email/

**Archivo de configuración:** `ecommerce_api/settings.py`  
**Módulo de emails:** `deliveries/email_utils.py`  
**Vistas con integración:** `deliveries/views.py`

---

**Última actualización:** 10 de Noviembre de 2025  
**Versión:** 1.0.0  
**Estado:** LISTO PARA PRODUCCIÓN ✅
