# 📦 Flujo de Estados de Órdenes

## 🎯 Estados Disponibles

Tu sistema tiene **4 estados** para las órdenes:

```python
class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pendiente'      # 🟡 Esperando pago
    PAID = 'PAID', 'Pagado'               # 🟢 Pago confirmado
    SHIPPED = 'SHIPPED', 'Enviado'        # 🚚 En camino
    CANCELLED = 'CANCELLED', 'Cancelado'  # ❌ Cancelada
```

**Nota:** No tienes estado `DELIVERED` (Entregado) en el modelo, solo en algunos comentarios.

---

## 🔄 Flujo Completo de Estados

### **Diagrama de Flujo:**

```
┌─────────────────────────────────────────────────────────────┐
│  1️⃣ CLIENTE CREA ORDEN                                      │
│     POST /api/orders/                                        │
│     Estado inicial: PENDING 🟡                               │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  2️⃣ CLIENTE INICIA PAGO                                     │
│     POST /api/orders/{id}/checkout/                          │
│     - Crea sesión de Stripe Checkout                         │
│     - Redirige a Stripe para pagar                           │
│     Estado: PENDING 🟡 (aún no pagado)                       │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  3️⃣ STRIPE PROCESA PAGO                                     │
│     Cliente completa pago en Stripe                          │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  4️⃣ WEBHOOK DE STRIPE (AUTOMÁTICO) ⚡                       │
│     POST /api/orders/webhook/stripe/                         │
│     Stripe envía evento: checkout.session.completed          │
│                                                              │
│     ✅ Backend cambia estado: PENDING → PAID                 │
│     ✅ Reduce stock de productos                             │
│                                                              │
│     Estado: PAID 🟢                                          │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  5️⃣ ADMIN CAMBIA A ENVIADO (MANUAL) 👨‍💼                     │
│     POST /api/admin/orders/{id}/update_status/               │
│     Body: {"status": "shipped"}                              │
│                                                              │
│     ✅ Admin cambia estado: PAID → SHIPPED                   │
│                                                              │
│     Estado: SHIPPED 🚚                                       │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  6️⃣ ORDEN COMPLETADA                                        │
│     Cliente recibe el producto                               │
│     (Opcional: Podría haber estado DELIVERED)                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 ¿QUIÉN CAMBIA LOS ESTADOS?

### **1️⃣ PENDING → Estado Inicial (Automático)**

**Quién:** Sistema (al crear la orden)  
**Cuándo:** Cuando el cliente crea una orden  
**Cómo:** Valor por defecto en el modelo

```python
# shop_orders/models.py
status = models.CharField(
    max_length=20, 
    choices=OrderStatus.choices, 
    default=OrderStatus.PENDING  # ← Automático
)
```

**Endpoint:**
```bash
POST /api/orders/
Body: {
  "items": [
    {"product_id": 1, "quantity": 2}
  ]
}

# Respuesta:
{
  "id": 123,
  "status": "PENDING",  # ← Automático
  "total_price": 1999.98
}
```

---

### **2️⃣ PENDING → PAID (Webhook de Stripe - Automático) ⚡**

**Quién:** Stripe (a través de webhook)  
**Cuándo:** Cuando el cliente completa el pago en Stripe  
**Cómo:** Webhook automático de Stripe

**Código del webhook:**
```python
# shop_orders/views.py - StripeWebhookView

def post(self, request, *args, **kwargs):
    # Stripe envía el evento
    event = stripe.Webhook.construct_event(payload, sig_header, secret)
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session.get('metadata', {}).get('order_id')
        
        order = Order.objects.get(id=order_id)
        
        # ✅ Cambio automático de estado
        if order.status == Order.OrderStatus.PENDING:
            # Reducir stock
            for item in order.items.all():
                product = item.product
                product.stock -= item.quantity
                product.save()
            
            # Cambiar estado a PAID
            order.status = Order.OrderStatus.PAID  # ← Automático
            order.save()
```

**Flujo:**
```
Cliente paga en Stripe
    ↓
Stripe confirma pago
    ↓
Stripe envía webhook a: POST /api/orders/webhook/stripe/
    ↓
Backend recibe evento checkout.session.completed
    ↓
Backend cambia orden de PENDING a PAID ✅
    ↓
Backend reduce stock de productos ✅
```

**Configuración requerida:**
En Stripe Dashboard → Webhooks, debes agregar:
```
URL: https://tudominio.com/api/orders/webhook/stripe/
Eventos: checkout.session.completed
```

---

### **3️⃣ PAID → SHIPPED (Admin Manual) 👨‍💼**

**Quién:** Administrador (manualmente)  
**Cuándo:** Cuando el admin despacha el paquete  
**Cómo:** Endpoint de admin para actualizar estado

**Endpoint:**
```bash
POST /api/admin/orders/123/update_status/
Authorization: Bearer {admin_token}
Body: {
  "status": "shipped"
}
```

**Código:**
```python
# shop_orders/views.py - AdminOrderViewSet

@action(detail=True, methods=['post'])
def update_status(self, request, pk=None):
    """
    Endpoint para que ADMIN cambie el estado manualmente
    """
    order = self.get_object()
    new_status = request.data.get('status')
    
    valid_statuses = ['pending', 'paid', 'shipped', 'delivered', 'cancelled']
    
    if new_status not in valid_statuses:
        return Response({'error': 'Estado inválido'})
    
    # ✅ Admin cambia estado manualmente
    order.status = new_status
    order.save()
    
    return Response(serializer.data)
```

**Permisos:** Solo `IsAdminUser`

---

### **4️⃣ * → CANCELLED (Admin o Sistema)**

**Quién:** Admin o Sistema  
**Cuándo:** 
- Admin cancela manualmente
- Sistema cancela si no hay stock (en webhook)

**Casos:**

**Caso A: Admin cancela manualmente**
```bash
POST /api/admin/orders/123/update_status/
Body: {"status": "cancelled"}
```

**Caso B: Sistema cancela por falta de stock**
```python
# En el webhook de Stripe
if product.stock < item.quantity:
    order.status = Order.OrderStatus.CANCELLED  # ← Automático
    order.save()
    # TODO: Reembolsar en Stripe
```

---

## 📋 Tabla Resumen

| Transición | Quién | Cómo | Automático |
|------------|-------|------|------------|
| **NULL → PENDING** | Sistema | Al crear orden | ✅ Sí |
| **PENDING → PAID** | Stripe Webhook | checkout.session.completed | ✅ Sí |
| **PAID → SHIPPED** | Admin | POST /admin/orders/{id}/update_status/ | ❌ Manual |
| **PAID → CANCELLED** | Admin | POST /admin/orders/{id}/update_status/ | ❌ Manual |
| **PENDING → CANCELLED** | Sistema/Admin | Stock insuficiente o manual | ⚠️ Mixto |

---

## 🚀 Implementación en Frontend

### **Para Admin: Cambiar estado de orden**

```javascript
const updateOrderStatus = async (orderId, newStatus) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(
    `http://localhost:8000/api/admin/orders/${orderId}/update_status/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status: newStatus })
    }
  );
  
  if (response.ok) {
    const data = await response.json();
    console.log('✅ Estado actualizado:', data.status);
  }
};

// Uso:
updateOrderStatus(123, 'shipped');  // Marcar como enviado
updateOrderStatus(456, 'cancelled'); // Cancelar orden
```

### **Vista de Admin - Tabla de Órdenes**

```javascript
const AdminOrders = () => {
  const [orders, setOrders] = useState([]);
  
  const handleStatusChange = async (orderId, newStatus) => {
    await updateOrderStatus(orderId, newStatus);
    // Recargar lista de órdenes
    fetchOrders();
  };
  
  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Cliente</th>
          <th>Total</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {orders.map(order => (
          <tr key={order.id}>
            <td>{order.id}</td>
            <td>{order.user.username}</td>
            <td>${order.total_price}</td>
            <td>
              <span className={`badge ${order.status}`}>
                {order.status}
              </span>
            </td>
            <td>
              {order.status === 'PAID' && (
                <button onClick={() => handleStatusChange(order.id, 'shipped')}>
                  📦 Marcar como Enviado
                </button>
              )}
              
              {order.status !== 'CANCELLED' && (
                <button onClick={() => handleStatusChange(order.id, 'cancelled')}>
                  ❌ Cancelar
                </button>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};
```

---

## ⚠️ Estados NO Implementados Actualmente

Tu sistema **NO tiene** estos estados (pero están mencionados en comentarios):

- ❌ `DELIVERED` (Entregado) - No está en `OrderStatus.choices`

Si quieres agregar más estados, modifica el modelo:

```python
# shop_orders/models.py

class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pendiente'
    PAID = 'PAID', 'Pagado'
    SHIPPED = 'SHIPPED', 'Enviado'
    DELIVERED = 'DELIVERED', 'Entregado'  # ← Agregar
    CANCELLED = 'CANCELLED', 'Cancelado'
```

Luego crea migración:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🔍 Verificar Estado de una Orden

**Como cliente:**
```bash
GET /api/orders/
Authorization: Bearer {user_token}

# Respuesta:
[
  {
    "id": 123,
    "status": "PAID",  # ← Estado actual
    "created_at": "2025-10-26T10:30:00Z",
    "total_price": "1999.98"
  }
]
```

**Como admin:**
```bash
GET /api/admin/orders/
Authorization: Bearer {admin_token}

# Ver todas las órdenes con sus estados
```

---

## 🎨 Badges de Estado para UI

```css
.badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 12px;
}

.badge.PENDING {
  background: #FFF3CD;
  color: #856404;
}

.badge.PAID {
  background: #D4EDDA;
  color: #155724;
}

.badge.SHIPPED {
  background: #D1ECF1;
  color: #0C5460;
}

.badge.CANCELLED {
  background: #F8D7DA;
  color: #721C24;
}
```

---

## 🧪 Testing del Flujo

```bash
# 1. Crear orden (estado: PENDING)
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"items": [{"product_id": 1, "quantity": 2}]}'

# 2. Iniciar checkout (sigue PENDING hasta pagar)
curl -X POST http://localhost:8000/api/orders/123/checkout/ \
  -H "Authorization: Bearer $USER_TOKEN"

# 3. Simular webhook de Stripe (PENDING → PAID)
# (En producción, Stripe lo hace automático)

# 4. Admin cambia a SHIPPED
curl -X POST http://localhost:8000/api/admin/orders/123/update_status/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "shipped"}'
```

---

## 📝 Resumen

**Cambios automáticos:**
- ✅ `NULL → PENDING` - Al crear orden
- ✅ `PENDING → PAID` - Webhook de Stripe cuando pagan

**Cambios manuales (solo Admin):**
- 👨‍💼 `PAID → SHIPPED` - Admin despacha paquete
- 👨‍💼 `* → CANCELLED` - Admin cancela orden

**El cliente NUNCA cambia estados directamente**, solo puede:
- Crear órdenes (que inician en PENDING)
- Pagar (Stripe cambia a PAID vía webhook)
- Ver sus órdenes

**Todo el control de estados post-pago es del ADMIN.**
