# 📧 05. SISTEMA DE EMAILS

## 📝 Descripción General

El sistema envía notificaciones por email a los **managers** cuando:
- ✅ Un cliente solicita una devolución
- ✅ La devolución pasa a evaluación
- ✅ La devolución es aprobada
- ✅ La devolución es rechazada

El cliente **NO** recibe emails directamente (futuro enhancement).

---

## 👥 Managers que Reciben Notificaciones

**Total:** 6 managers configurados

**Lista de Managers:**
1. **Carlos Manager** - carlos_manager@example.com
2. **Ana Manager** - ana_manager@example.com  
3. **Luis Manager** - luis_manager@example.com
4. **Sofia Manager** - sofia_manager@example.com
5. **Miguel Manager** - miguel_manager@example.com
6. **Laura Manager** - laura_manager@example.com

---

## 📮 Tipos de Notificaciones

### 1. Notificación de Nueva Devolución

**Trigger:** Cliente solicita devolución (POST `/api/deliveries/returns/`)

**Subject:** 
```
🔔 Nueva solicitud de devolución - Tablet iPad Air
```

**Cuerpo:**
```
¡Hola Ana Manager!

Se ha recibido una nueva solicitud de devolución que requiere tu atención.

DETALLES DE LA DEVOLUCIÓN:
--------------------------
ID de Devolución: #17
Estado: Solicitada
Cliente: Juan Cliente
Email Cliente: juan.cliente@example.com

PRODUCTO:
---------
Nombre: Tablet iPad Air
Precio: $5,999.99
Cantidad: 1

ORDEN:
------
ID Orden: #62
Total Orden: $5,999.99
Fecha Orden: 10 de noviembre de 2025

RAZÓN DE DEVOLUCIÓN:
-------------------
Producto defectuoso

MÉTODO DE REEMBOLSO:
-------------------
Billetera virtual

ACCIONES:
---------
Por favor, revisa esta solicitud en el panel de administración.

Fecha de solicitud: 10 de noviembre de 2025 22:22

---
Sistema de Devoluciones E-commerce
```

---

### 2. Notificación de Evaluación

**Trigger:** Manager envía a evaluación (POST `/{id}/send_to_evaluation/`)

**Subject:**
```
📦 Devolución #17 en evaluación
```

**Cuerpo:**
```
Hola Ana Manager,

La devolución #17 ha sido enviada a evaluación.

DETALLES:
Cliente: Juan Cliente
Producto: Tablet iPad Air
Estado: En evaluación

Se notificará cuando se complete el proceso de evaluación.

Gracias,
Sistema de Devoluciones
```

---

### 3. Notificación de Aprobación

**Trigger:** Manager aprueba (POST `/{id}/approve/`)

**Subject:**
```
✅ Devolución #17 aprobada
```

**Cuerpo:**
```
Hola Ana Manager,

La devolución #17 ha sido aprobada exitosamente.

DETALLES DEL REEMBOLSO:
Monto: $5,999.99
Método: Billetera virtual
Cliente: Juan Cliente
Producto: Tablet iPad Air

El reembolso ha sido procesado.

Gracias,
Sistema de Devoluciones
```

---

### 4. Notificación de Rechazo

**Trigger:** Manager rechaza (POST `/{id}/reject/`)

**Subject:**
```
❌ Devolución #17 rechazada
```

**Cuerpo:**
```
Hola Ana Manager,

La devolución #17 ha sido rechazada.

DETALLES:
Cliente: Juan Cliente
Producto: Tablet iPad Air
Razón de rechazo: No cumple con los criterios de devolución

No se procesó ningún reembolso.

Gracias,
Sistema de Devoluciones
```

---

## 🔧 Configuración Backend

### Configuración en settings.py:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'your-email@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'your-app-password')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

### Variables de Entorno (.env):

```env
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password-de-google
```

---

## 📂 Archivo Responsable

**Archivo:** `deliveries/email_utils.py`

**Funciones principales:**

```python
def send_manager_notification(return_instance):
    """
    Envía notificación a TODOS los managers cuando se crea una devolución
    """
    managers = User.objects.filter(role='MANAGER')
    
    for manager in managers:
        send_mail(
            subject=f'🔔 Nueva solicitud de devolución - {return_instance.product.name}',
            message=generate_email_body(return_instance, manager),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[manager.email],
            fail_silently=False
        )
```

---

## 🎨 Componente Frontend (Administración)

### Panel de Notificaciones Email

```jsx
const EmailNotificationPanel = ({ returnData }) => {
  const [emailsSent, setEmailsSent] = useState(false);
  const [managers, setManagers] = useState([]);

  useEffect(() => {
    // Cargar lista de managers
    loadManagers();
  }, []);

  const loadManagers = async () => {
    const response = await fetch('http://localhost:8000/api/users/?role=MANAGER', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    const data = await response.json();
    setManagers(data.results);
  };

  return (
    <div className="email-notification-panel">
      <h3>📧 Notificaciones por Email</h3>
      
      <div className="notification-status">
        {emailsSent ? (
          <div className="success">
            ✅ Se enviaron notificaciones a {managers.length} managers
          </div>
        ) : (
          <div className="info">
            ℹ️ Los emails se enviarán automáticamente cuando se cree la devolución
          </div>
        )}
      </div>

      <div className="manager-list">
        <h4>Managers que recibirán notificación:</h4>
        <ul>
          {managers.map(manager => (
            <li key={manager.id}>
              <span className="manager-name">{manager.first_name} {manager.last_name}</span>
              <span className="manager-email">{manager.email}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
```

---

## 📊 Vista de Estado de Emails

```jsx
const EmailStatusBadge = ({ returnId }) => {
  const [emailLog, setEmailLog] = useState(null);

  useEffect(() => {
    // En producción, podrías tener un endpoint de log de emails
    // Por ahora, asumimos que se enviaron correctamente
    setEmailLog({
      sent: true,
      recipients: 6,
      timestamp: new Date().toISOString()
    });
  }, [returnId]);

  if (!emailLog) return null;

  return (
    <div className="email-status-badge">
      {emailLog.sent ? (
        <>
          <span className="icon">✉️</span>
          <span className="text">
            {emailLog.recipients} managers notificados
          </span>
          <small>{new Date(emailLog.timestamp).toLocaleString()}</small>
        </>
      ) : (
        <span className="error">❌ Error al enviar emails</span>
      )}
    </div>
  );
};
```

---

## 🧪 Probar Sistema de Emails

### 1. Desde Frontend (simulación):

```javascript
const testEmailNotification = async (returnId) => {
  console.log('📧 Sistema de emails:');
  console.log('- Se enviarán 6 emails a los managers');
  console.log('- Destinatarios:');
  console.log('  • carlos_manager@example.com');
  console.log('  • ana_manager@example.com');
  console.log('  • luis_manager@example.com');
  console.log('  • sofia_manager@example.com');
  console.log('  • miguel_manager@example.com');
  console.log('  • laura_manager@example.com');
  
  // En producción, esto se hace automáticamente en el backend
  // No necesitas llamar un endpoint específico
};
```

### 2. Ver en Backend (logs):

Cuando se crea una devolución, verás en la consola del servidor:

```
📧 Enviando notificación a carlos_manager@example.com
✅ Email enviado correctamente
📧 Enviando notificación a ana_manager@example.com
✅ Email enviado correctamente
...
```

---

## ⚙️ Configuración de Gmail

### Paso 1: Habilitar App Password

1. Ve a tu cuenta de Google
2. Seguridad → Verificación en 2 pasos (debes habilitarla)
3. Contraseñas de aplicaciones
4. Genera una contraseña para "Django Backend"

### Paso 2: Configurar .env

```env
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx  # App password de 16 dígitos
```

### Paso 3: Reiniciar servidor

```bash
python manage.py runserver
```

---

## 📋 Checklist de Emails

Al crear una devolución, verifica:

- [ ] ✅ 6 emails enviados (uno por manager)
- [ ] ✅ Subject correcto con nombre del producto
- [ ] ✅ Cuerpo del email con todos los detalles
- [ ] ✅ Email del cliente visible en el mensaje
- [ ] ✅ ID de devolución incluido
- [ ] ✅ Estado actual de la devolución
- [ ] ✅ Método de reembolso mencionado

---

## 🚀 Mejoras Futuras

### Notificaciones al Cliente:

```python
def send_customer_notification(return_instance):
    """
    Enviar email al cliente cuando su devolución cambia de estado
    """
    customer = return_instance.user
    
    status_messages = {
        'APPROVED': 'Tu devolución ha sido aprobada ✅',
        'REJECTED': 'Tu devolución ha sido rechazada ❌',
        'IN_EVALUATION': 'Tu devolución está en evaluación 📦'
    }
    
    send_mail(
        subject=status_messages.get(return_instance.status),
        message=f'Hola {customer.first_name}, ...',
        recipient_list=[customer.email]
    )
```

### Templates HTML:

```python
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_html_notification(return_instance):
    html_content = render_to_string('emails/return_notification.html', {
        'return': return_instance,
        'manager': manager
    })
    
    msg = EmailMultiAlternatives(
        subject='Nueva devolución',
        body='Versión texto plano',
        to=[manager.email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
```

---

## ⚠️ Troubleshooting

### Problema: No se envían emails

**Solución:**
1. Verificar configuración en `.env`
2. Verificar que Gmail tiene App Password habilitado
3. Ver logs del servidor para errores
4. Verificar que EMAIL_HOST_PASSWORD es correcto

### Problema: Emails van a spam

**Solución:**
1. Configurar SPF/DKIM en tu dominio
2. Usar un servicio profesional (SendGrid, Mailgun)
3. Agregar dominio verificado

### Problema: Error "SMTPAuthenticationError"

**Solución:**
```python
# Verificar credenciales
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Body', 'from@example.com', ['to@example.com'])
```

---

**Siguiente:** Ver `06_EJEMPLOS_COMPLETOS.md` para integraciones completas
