# 🔄 Sistema Simplificado de Devoluciones

## 📋 Resumen

Sistema simple de devoluciones donde el cliente puede solicitar devoluciones desde su historial, el manager las evalúa físicamente con un tercero, y se procesa el reembolso automáticamente.

---

## 🎯 Flujo Completo

```
┌──────────────────────────────────────────────────────────────┐
│  1️⃣ CLIENTE: Solicitar Devolución desde Historial           │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
        Estado: REQUESTED (Solicitada por cliente)
        ✉️ Email al Manager: "Nueva solicitud de devolución"
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  2️⃣ MANAGER: Enviar a Evaluación Física                     │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
        Estado: IN_EVALUATION (En evaluación física)
        Manager envía producto físicamente a tercero
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  3️⃣ TERCERO: Evalúa físicamente el producto                 │
│      Manager recibe informe físico                           │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  4️⃣ MANAGER: Toma Decisión                                  │
│                                                               │
│  ┌────────────────────┐      ┌────────────────────┐         │
│  │    ✅ ACEPTAR      │  o   │    ❌ RECHAZAR     │         │
│  └─────────┬──────────┘      └─────────┬──────────┘         │
└────────────┼──────────────────────────┼─────────────────────┘
             │                            │
             ▼                            ▼
    Estado: APPROVED              Estado: REJECTED
    (Aprobada)                    (Rechazada)
             │                            │
             ▼                            ▼
┌─────────────────────────┐    ┌──────────────────────┐
│ 5️⃣ SISTEMA: Procesa    │    │ ✉️ Email al Cliente:  │
│    Reembolso AUTO       │    │ "Devolución          │
│                         │    │  Rechazada"          │
│ • Calcula monto         │    │                      │
│ • Billetera virtual     │    │ Motivo: [notas]      │
│   o método original     │    └──────────────────────┘
│ • Actualiza estado      │
│   → COMPLETED           │
│                         │
│ ✉️ Email al Cliente:    │
│ "Reembolso procesado"   │
└─────────────────────────┘
```

---

## 🔐 Roles y Permisos

| Acción | Cliente | Manager | Admin |
|--------|---------|---------|-------|
| Ver mis devoluciones | ✅ | ✅ | ✅ |
| Solicitar devolución | ✅ | ✅ | ✅ |
| Ver todas las devoluciones | ❌ | ✅ | ✅ |
| Cambiar a IN_EVALUATION | ❌ | ✅ | ✅ |
| Aprobar/Rechazar | ❌ | ✅ | ✅ |
| Ver estadísticas | ❌ | ✅ | ✅ |

---

## 📡 Endpoints API

### **1. Cliente: Solicitar Devolución**

```bash
POST /api/deliveries/returns/

Headers:
  Authorization: Bearer {token_cliente}
  Content-Type: application/json

Body:
{
  "order_id": 123,
  "product_id": 45,
  "quantity": 1,
  "reason": "DEFECTIVE",
  "description": "El producto llegó con la pantalla rota"
}

Response 201:
{
  "id": 5,
  "status": "REQUESTED",
  "order": 123,
  "product": {
    "id": 45,
    "name": "Smartphone XYZ"
  },
  "reason": "DEFECTIVE",
  "description": "El producto llegó con la pantalla rota",
  "requested_at": "2025-11-10T10:30:00Z",
  "message": "Solicitud de devolución creada. Un manager la revisará pronto."
}
```

### **2. Cliente: Ver Mis Devoluciones**

```bash
GET /api/deliveries/returns/my-returns/

Headers:
  Authorization: Bearer {token_cliente}

Response 200:
{
  "count": 2,
  "results": [
    {
      "id": 5,
      "order": 123,
      "product": {
        "id": 45,
        "name": "Smartphone XYZ",
        "price": "999.99"
      },
      "status": "REQUESTED",
      "status_display": "Solicitada por cliente",
      "reason": "DEFECTIVE",
      "requested_at": "2025-11-10T10:30:00Z"
    },
    {
      "id": 3,
      "order": 98,
      "product": {
        "id": 12,
        "name": "Laptop ABC"
      },
      "status": "COMPLETED",
      "status_display": "Completada - Reembolso realizado",
      "refund_amount": "1499.99",
      "completed_at": "2025-11-05T15:00:00Z"
    }
  ]
}
```

### **3. Manager: Ver Todas las Solicitudes**

```bash
GET /api/deliveries/returns/

Headers:
  Authorization: Bearer {token_manager}

Query Params:
  ?status=REQUESTED          # Filtrar por estado
  ?order=123                 # Filtrar por orden
  ?product=45                # Filtrar por producto

Response 200:
{
  "count": 15,
  "results": [
    {
      "id": 5,
      "customer": {
        "id": 12,
        "username": "cliente123",
        "email": "cliente@example.com"
      },
      "order": 123,
      "product": {
        "id": 45,
        "name": "Smartphone XYZ"
      },
      "status": "REQUESTED",
      "reason": "DEFECTIVE",
      "description": "El producto llegó con la pantalla rota",
      "requested_at": "2025-11-10T10:30:00Z"
    }
  ]
}
```

### **4. Manager: Enviar a Evaluación**

```bash
POST /api/deliveries/returns/5/send-to-evaluation/

Headers:
  Authorization: Bearer {token_manager}
  Content-Type: application/json

Body:
{
  "notes": "Producto enviado a técnico externo para evaluación"
}

Response 200:
{
  "id": 5,
  "status": "IN_EVALUATION",
  "status_display": "En evaluación física",
  "manager_notes": "Producto enviado a técnico externo para evaluación",
  "updated_at": "2025-11-10T11:00:00Z",
  "message": "Devolución enviada a evaluación física"
}
```

### **5. Manager: Aprobar Devolución**

```bash
POST /api/deliveries/returns/5/approve/

Headers:
  Authorization: Bearer {token_manager}
  Content-Type: application/json

Body:
{
  "evaluation_notes": "Producto efectivamente defectuoso. Pantalla rota confirmada.",
  "refund_amount": 999.99,
  "refund_method": "WALLET"
}

Response 200:
{
  "id": 5,
  "status": "APPROVED",
  "status_display": "Aprobada - Procesando reembolso",
  "evaluation_notes": "Producto efectivamente defectuoso. Pantalla rota confirmada.",
  "refund_amount": "999.99",
  "refund_method": "WALLET",
  "evaluated_at": "2025-11-10T14:00:00Z",
  "message": "✅ Devolución aprobada. Procesando reembolso automáticamente..."
}

# Automáticamente después:
# 1. Se procesa el reembolso
# 2. Estado cambia a COMPLETED
# 3. Se envía email al cliente
```

### **6. Manager: Rechazar Devolución**

```bash
POST /api/deliveries/returns/5/reject/

Headers:
  Authorization: Bearer {token_manager}
  Content-Type: application/json

Body:
{
  "evaluation_notes": "Producto en perfecto estado. No se encontraron defectos.",
  "manager_notes": "El daño parece ser causado por mal uso del cliente."
}

Response 200:
{
  "id": 5,
  "status": "REJECTED",
  "status_display": "Rechazada",
  "evaluation_notes": "Producto en perfecto estado. No se encontraron defectos.",
  "manager_notes": "El daño parece ser causado por mal uso del cliente.",
  "evaluated_at": "2025-11-10T14:00:00Z",
  "message": "❌ Devolución rechazada. Se ha notificado al cliente."
}

# Automáticamente se envía email al cliente con el motivo
```

---

## 📧 Emails Automáticos

### **Email 1: Nueva Solicitud (al Manager)**

```
Asunto: 🔔 Nueva Solicitud de Devolución #5

Hola Manager,

Un cliente ha solicitado una devolución:

Cliente: cliente123 (cliente@example.com)
Orden: #123
Producto: Smartphone XYZ
Motivo: Producto defectuoso
Descripción: El producto llegó con la pantalla rota

Por favor, revisa la solicitud en:
http://tuapp.com/admin/returns/5

Saludos,
Sistema SmartSales365
```

### **Email 2: Devolución Aprobada (al Cliente)**

```
Asunto: ✅ Tu Devolución #5 ha sido Aprobada

Hola cliente123,

¡Buenas noticias! Tu solicitud de devolución ha sido aprobada.

Detalles:
• Orden: #123
• Producto: Smartphone XYZ
• Monto a reembolsar: $999.99
• Método: Billetera virtual

El reembolso se procesará en las próximas 24-48 horas.

Podrás ver el saldo en tu billetera virtual en:
http://tuapp.com/mi-cuenta/billetera

Gracias por tu compra,
SmartSales365
```

### **Email 3: Devolución Rechazada (al Cliente)**

```
Asunto: ❌ Tu Solicitud de Devolución #5

Hola cliente123,

Lamentamos informarte que tu solicitud de devolución ha sido rechazada.

Detalles:
• Orden: #123
• Producto: Smartphone XYZ

Motivo del rechazo:
Después de la evaluación física realizada por nuestro equipo técnico, 
se determinó que el producto está en perfecto estado y el daño parece 
ser causado por mal uso.

Si tienes dudas, contáctanos en: soporte@smartsales365.com

Saludos,
SmartSales365
```

---

## 💰 Sistema de Reembolso

### **Métodos de Reembolso:**

#### **1. Billetera Virtual (WALLET)** - Más Simple
```python
# En el futuro puedes implementar:
user.wallet_balance += refund_amount
user.save()

# O usar modelo Wallet:
Wallet.objects.create(
    user=user,
    transaction_type='REFUND',
    amount=refund_amount,
    description=f'Reembolso por devolución #{return_id}'
)
```

#### **2. Método Original (ORIGINAL)**
```python
# Si pagó con Stripe, reembolsar a Stripe
# Si pagó en efectivo, marcar para reembolso manual
```

#### **3. Transferencia Bancaria (BANK)**
```python
# Registrar datos bancarios del cliente
# Procesar transferencia (manual o con API bancaria)
```

**Para simplificar, recomiendo empezar con WALLET.**

---

## 🗃️ Modelo de Datos

```python
class Return(models.Model):
    # Información básica
    order = ForeignKey(Order)
    product = ForeignKey(Product)
    user = ForeignKey(User)  # Cliente que solicita
    quantity = PositiveIntegerField()
    reason = CharField(choices=ReturnReason.choices)
    description = TextField()
    
    # Estado
    status = CharField(
        choices=[
            'REQUESTED',      # Solicitada por cliente
            'IN_EVALUATION',  # En evaluación física  
            'APPROVED',       # Aprobada
            'REJECTED',       # Rechazada
            'COMPLETED'       # Completada
        ]
    )
    
    # Evaluación
    evaluation_notes = TextField()   # Notas del tercero
    manager_notes = TextField()       # Notas del manager
    
    # Reembolso
    refund_amount = DecimalField()
    refund_method = CharField(
        choices=[
            'WALLET',    # Billetera virtual
            'ORIGINAL',  # Método original
            'BANK'       # Transferencia
        ]
    )
    
    # Timestamps
    requested_at = DateTimeField()
    evaluated_at = DateTimeField()
    processed_at = DateTimeField()
    completed_at = DateTimeField()
```

---

## 🧪 Probar el Sistema

### **Opción 1: Desde el Frontend**

```javascript
// 1. Cliente ve su historial
GET /api/orders/
// Muestra órdenes con botón "Devolver Producto"

// 2. Cliente hace clic en "Devolver"
POST /api/deliveries/returns/
{
  "order_id": 123,
  "product_id": 45,
  "reason": "DEFECTIVE",
  "description": "..."
}

// 3. Manager ve solicitudes pendientes
GET /api/deliveries/returns/?status=REQUESTED

// 4. Manager envía a evaluación
POST /api/deliveries/returns/5/send-to-evaluation/

// 5. Manager aprueba o rechaza
POST /api/deliveries/returns/5/approve/
// o
POST /api/deliveries/returns/5/reject/
```

### **Opción 2: Script Python**

```python
# test_returns_simple.py
from shop_orders.models import Order
from deliveries.models import Return
from django.contrib.auth import get_user_model

User = get_user_model()

# 1. Cliente solicita devolución
cliente = User.objects.get(username='cliente_test')
orden = Order.objects.filter(user=cliente, status='DELIVERED').first()
producto = orden.items.first().product

devolucion = Return.objects.create(
    order=orden,
    product=producto,
    user=cliente,
    quantity=1,
    reason='DEFECTIVE',
    description='Producto defectuoso',
    status='REQUESTED'
)

print(f"✅ Devolución #{devolucion.id} creada")

# 2. Manager envía a evaluación
devolucion.status = 'IN_EVALUATION'
devolucion.manager_notes = 'Enviado a técnico'
devolucion.save()

# 3. Manager aprueba
devolucion.status = 'APPROVED'
devolucion.evaluation_notes = 'Producto efectivamente defectuoso'
devolucion.refund_amount = producto.price
devolucion.save()

# 4. Sistema procesa reembolso
devolucion.status = 'COMPLETED'
devolucion.save()

print(f"✅ Devolución completada. Reembolso: ${devolucion.refund_amount}")
```

---

## ✅ Ventajas del Sistema Simplificado

1. **✅ Sin complejidad de delivery**
   - No hay rutas, zonas, repartidores
   - Solo estados simples

2. **✅ Evaluación física real**
   - Manager envía a tercero
   - Informe físico valida la devolución

3. **✅ Automatización del reembolso**
   - Si APPROVED → reembolso automático
   - Sin pasos manuales adicionales

4. **✅ Notificaciones por email**
   - Cliente siempre informado
   - Manager notificado de nuevas solicitudes

5. **✅ Historial completo**
   - Cliente ve todas sus devoluciones
   - Estados claros y entendibles

6. **✅ Escalable**
   - Funciona con 1 o 1000 devoluciones/día
   - Sin procesos manuales complejos

---

## 🎯 Resumen

| Aspecto | Implementación |
|---------|----------------|
| **Complejidad** | ⭐⭐ Simple |
| **Estados** | 5 estados claros |
| **Roles** | Cliente + Manager |
| **Automatización** | Alta (reembolso automático) |
| **Emails** | Automáticos |
| **Delivery físico** | ❌ Eliminado |
| **Evaluación** | ✅ Por tercero físico |

---

**Estado**: ✅ LISTO PARA IMPLEMENTAR  
**Complejidad**: SIMPLE  
**Prioridad**: ALTA
