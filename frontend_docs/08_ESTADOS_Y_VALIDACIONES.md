# ✅ 08. ESTADOS Y VALIDACIONES

## 📝 Descripción

Esta sección documenta todas las **reglas de negocio**, **validaciones** y **restricciones** del sistema de devoluciones.

---

## 🔒 VALIDACIONES PREVIAS A SOLICITAR DEVOLUCIÓN

### 1. Usuario debe estar autenticado

```javascript
// ❌ Sin token
fetch('http://localhost:8000/api/deliveries/returns/', {
  method: 'POST',
  body: JSON.stringify({...})
});
// Response: 401 Unauthorized

// ✅ Con token
fetch('http://localhost:8000/api/deliveries/returns/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({...})
});
```

---

### 2. El usuario debe tener el rol CLIENTE

```javascript
// ❌ Manager o Admin intentando solicitar devolución
// Response: 403 Forbidden

// ✅ Cliente puede solicitar
if (user.role === 'CLIENTE') {
  // Permitir solicitar devolución
}
```

---

### 3. La orden debe pertenecer al cliente

```javascript
// Validación automática en el backend
// El cliente solo puede solicitar devolución de SUS propias órdenes

// ❌ Intentar devolver orden de otro cliente
POST /api/deliveries/returns/
{
  "order": 999,  // Orden que no es del cliente
  "product": 1,
  "reason": "...",
  "refund_method": "WALLET"
}
// Response: 400 Bad Request - "No tienes permiso para devolver esta orden"

// ✅ Devolver orden propia
POST /api/deliveries/returns/
{
  "order": 62,  // Orden del cliente
  ...
}
```

---

### 4. La orden debe estar en estado DELIVERED

```javascript
const canRequestReturn = (order) => {
  if (order.status !== 'DELIVERED') {
    return {
      allowed: false,
      reason: 'La orden debe estar entregada para solicitar devolución'
    };
  }
  return { allowed: true };
};

// Estados de orden:
// - PENDING: ❌ No se puede devolver
// - IN_TRANSIT: ❌ No se puede devolver
// - DELIVERED: ✅ Se puede devolver
// - CANCELLED: ❌ No se puede devolver
// - RETURNED: ❌ Ya fue devuelta
```

**Ejemplo en Frontend:**

```jsx
const MyOrders = () => {
  const [orders, setOrders] = useState([]);

  return (
    <div>
      {orders.map(order => (
        <div key={order.id}>
          <p>Estado: {order.status_display}</p>
          
          {order.status === 'DELIVERED' ? (
            <button onClick={() => requestReturn(order)}>
              ↩️ Solicitar Devolución
            </button>
          ) : (
            <span className="disabled">
              ⚠️ Debe estar entregada para devolver
            </span>
          )}
        </div>
      ))}
    </div>
  );
};
```

---

### 5. Plazo de 30 días desde la entrega

```javascript
const canRequestReturn = (order) => {
  const deliveryDate = new Date(order.updated_at);
  const now = new Date();
  const daysSinceDelivery = Math.floor((now - deliveryDate) / (1000 * 60 * 60 * 24));

  if (daysSinceDelivery > 30) {
    return {
      allowed: false,
      reason: `Han pasado ${daysSinceDelivery} días desde la entrega. Plazo máximo: 30 días`
    };
  }

  return {
    allowed: true,
    daysRemaining: 30 - daysSinceDelivery
  };
};

// Ejemplo de uso:
const validation = canRequestReturn(order);

if (!validation.allowed) {
  alert(validation.reason);
} else {
  console.log(`Tienes ${validation.daysRemaining} días restantes para devolver`);
}
```

**Componente Visual:**

```jsx
const ReturnDeadlineIndicator = ({ order }) => {
  const deliveryDate = new Date(order.updated_at);
  const now = new Date();
  const daysSince = Math.floor((now - deliveryDate) / (1000 * 60 * 60 * 24));
  const daysRemaining = 30 - daysSince;

  if (daysSince > 30) {
    return (
      <div className="deadline-expired">
        ❌ Plazo expirado hace {daysSince - 30} días
      </div>
    );
  }

  const urgency = daysRemaining <= 5 ? 'urgent' : 
                  daysRemaining <= 10 ? 'warning' : 'normal';

  return (
    <div className={`deadline-indicator ${urgency}`}>
      ⏰ {daysRemaining} días restantes para devolver
    </div>
  );
};
```

---

### 6. No debe existir una devolución previa para el mismo producto

```javascript
// Validación automática en el backend

// ❌ Intentar crear segunda devolución del mismo producto
POST /api/deliveries/returns/
{
  "order": 62,
  "product": 1,  // Ya existe devolución para este producto
  ...
}
// Response: 400 Bad Request - "Ya existe una devolución para este producto"

// ✅ Primera devolución
POST /api/deliveries/returns/
{
  "order": 62,
  "product": 1,  // No existe devolución previa
  ...
}
```

**Frontend - Verificar antes de mostrar botón:**

```javascript
const checkExistingReturn = async (orderId, productId) => {
  const response = await fetch(
    `http://localhost:8000/api/deliveries/returns/`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );

  const data = await response.json();
  
  return data.results.some(ret => 
    ret.order_details.id === orderId && 
    ret.product_details.id === productId
  );
};

// Uso:
const hasExistingReturn = await checkExistingReturn(62, 1);

if (hasExistingReturn) {
  alert('Ya solicitaste devolución para este producto');
} else {
  // Mostrar formulario de devolución
}
```

---

### 7. El producto debe existir en la orden

```javascript
// Validación automática en el backend

// ❌ Producto que no está en la orden
POST /api/deliveries/returns/
{
  "order": 62,
  "product": 999,  // Este producto no está en la orden 62
  ...
}
// Response: 400 Bad Request - "El producto no pertenece a esta orden"

// ✅ Producto válido
const orderItems = order.items;
const validProductIds = orderItems.map(item => item.product.id);

// Solo permitir devolver productos que están en la orden
```

---

## 📋 VALIDACIONES AL CREAR DEVOLUCIÓN

### Campos Requeridos:

```javascript
// ✅ Datos mínimos requeridos
{
  "order": 62,              // Required, debe ser número
  "product": 1,             // Required, debe ser número
  "reason": "Defectuoso",   // Required, mínimo 10 caracteres
  "refund_method": "WALLET" // Required, "WALLET" o "ORIGINAL_PAYMENT"
}

// ❌ Falta campo requerido
{
  "order": 62,
  "product": 1
  // Faltan reason y refund_method
}
// Response: 400 Bad Request
// {
//   "reason": ["Este campo es requerido"],
//   "refund_method": ["Este campo es requerido"]
// }
```

### Validación de `reason`:

```javascript
// Longitud mínima: 10 caracteres
// Longitud máxima: 500 caracteres

// ❌ Razón muy corta
{
  "reason": "Malo"  // Solo 4 caracteres
}
// Response: 400 Bad Request - "La razón debe tener al menos 10 caracteres"

// ❌ Razón muy larga
{
  "reason": "A".repeat(501)  // 501 caracteres
}
// Response: 400 Bad Request - "La razón no puede exceder 500 caracteres"

// ✅ Razón válida
{
  "reason": "El producto llegó con defectos de fábrica"
}
```

**Componente de validación:**

```jsx
const ReasonInput = ({ value, onChange, error }) => {
  const [charCount, setCharCount] = useState(value.length);
  const minLength = 10;
  const maxLength = 500;

  const handleChange = (e) => {
    const newValue = e.target.value;
    setCharCount(newValue.length);
    onChange(newValue);
  };

  return (
    <div className="reason-input">
      <label>Razón de la devolución:</label>
      <textarea
        value={value}
        onChange={handleChange}
        maxLength={maxLength}
        placeholder="Explica por qué deseas devolver este producto (mínimo 10 caracteres)"
        rows="4"
      />
      
      <div className="char-counter">
        <span className={charCount < minLength ? 'error' : 'success'}>
          {charCount} / {maxLength} caracteres
        </span>
        {charCount < minLength && (
          <span className="min-warning">
            (Mínimo {minLength - charCount} caracteres más)
          </span>
        )}
      </div>
      
      {error && <span className="error-message">{error}</span>}
    </div>
  );
};
```

---

### Validación de `refund_method`:

```javascript
// Opciones válidas: "WALLET" o "ORIGINAL_PAYMENT"

// ❌ Método inválido
{
  "refund_method": "PAYPAL"
}
// Response: 400 Bad Request - "Método de reembolso inválido"

// ✅ Métodos válidos
{
  "refund_method": "WALLET"  // Recomendado
}

{
  "refund_method": "ORIGINAL_PAYMENT"
}
```

**Selector de método:**

```jsx
const RefundMethodSelector = ({ value, onChange }) => {
  return (
    <div className="refund-method-selector">
      <h3>Método de reembolso:</h3>
      
      <label className={value === 'WALLET' ? 'selected' : ''}>
        <input
          type="radio"
          value="WALLET"
          checked={value === 'WALLET'}
          onChange={(e) => onChange(e.target.value)}
        />
        <div className="method-info">
          <h4>💰 Billetera Virtual</h4>
          <p>Reembolso inmediato</p>
          <span className="badge-recommended">Recomendado</span>
        </div>
      </label>

      <label className={value === 'ORIGINAL_PAYMENT' ? 'selected' : ''}>
        <input
          type="radio"
          value="ORIGINAL_PAYMENT"
          checked={value === 'ORIGINAL_PAYMENT'}
          onChange={(e) => onChange(e.target.value)}
        />
        <div className="method-info">
          <h4>💳 Método de Pago Original</h4>
          <p>Reembolso en 5-10 días hábiles</p>
        </div>
      </label>
    </div>
  );
};
```

---

## 🔄 TRANSICIONES DE ESTADO

### Flujo Válido de Estados:

```
REQUESTED → IN_EVALUATION → APPROVED
                          → REJECTED

Estados finales: APPROVED, REJECTED
```

### Validaciones por Estado:

| Estado Actual | Acciones Permitidas | Roles Autorizados |
|--------------|---------------------|-------------------|
| `REQUESTED` | → `IN_EVALUATION`<br>→ `REJECTED` | MANAGER, ADMIN |
| `IN_EVALUATION` | → `APPROVED`<br>→ `REJECTED` | MANAGER, ADMIN |
| `APPROVED` | **Ninguna** (estado final) | - |
| `REJECTED` | **Ninguna** (estado final) | - |

**Validación en Backend:**

```python
# deliveries/views.py

def send_to_evaluation(self, request, pk=None):
    ret = self.get_object()
    
    # ✅ Solo desde REQUESTED
    if ret.status != 'REQUESTED':
        return Response(
            {"error": "Solo puedes enviar a evaluación devoluciones en estado REQUESTED"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    ret.status = 'IN_EVALUATION'
    ret.save()
    return Response({"message": "Enviado a evaluación"})

def approve(self, request, pk=None):
    ret = self.get_object()
    
    # ✅ Solo desde IN_EVALUATION
    if ret.status != 'IN_EVALUATION':
        return Response(
            {"error": "Solo puedes aprobar devoluciones en evaluación"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Procesar reembolso...
    ret.status = 'APPROVED'
    ret.save()
    return Response({"message": "Aprobado"})
```

**Validación en Frontend:**

```jsx
const ReturnActions = ({ returnData }) => {
  const canSendToEvaluation = returnData.status === 'REQUESTED';
  const canApproveOrReject = returnData.status === 'IN_EVALUATION';
  const isFinal = ['APPROVED', 'REJECTED'].includes(returnData.status);

  return (
    <div className="return-actions">
      {canSendToEvaluation && (
        <button onClick={sendToEvaluation}>
          📦 Enviar a Evaluación
        </button>
      )}

      {canApproveOrReject && (
        <>
          <button onClick={approve} className="btn-approve">
            ✅ Aprobar
          </button>
          <button onClick={reject} className="btn-reject">
            ❌ Rechazar
          </button>
        </>
      )}

      {isFinal && (
        <div className="final-status">
          {returnData.status === 'APPROVED' ? '✅ Aprobado' : '❌ Rechazado'}
          <span className="no-actions">No hay más acciones disponibles</span>
        </div>
      )}
    </div>
  );
};
```

---

## 💰 VALIDACIONES DE REEMBOLSO

### 1. Monto de Reembolso

```javascript
// El monto del reembolso es SIEMPRE el precio del producto al momento de la compra

// ✅ Reembolso correcto
const refundAmount = orderItem.price;  // Precio original

// ❌ No usar precio actual del producto
const wrongAmount = product.current_price;  // Puede haber cambiado
```

### 2. Creación de Billetera

```javascript
// Si refund_method = "WALLET":

// 1. Verificar si el cliente ya tiene billetera
const walletResponse = await fetch(
  'http://localhost:8000/api/users/wallets/my_balance/',
  { headers: { 'Authorization': `Bearer ${token}` } }
);

if (walletResponse.status === 404) {
  // Se creará automáticamente al aprobar
  console.log('Se creará billetera al aprobar');
} else {
  const wallet = await walletResponse.json();
  console.log('Balance actual:', wallet.balance);
}

// 2. Al aprobar, el backend:
//    - Crea billetera si no existe
//    - Actualiza balance
//    - Crea transacción de tipo REFUND
```

### 3. Reembolso a Método Original

```javascript
// Si refund_method = "ORIGINAL_PAYMENT":

// Backend procesa con Stripe:
stripe.refunds.create({
  payment_intent: order.payment_intent_id,
  amount: refund_amount * 100  // Stripe usa centavos
})

// Tiempo de procesamiento:
// - Tarjeta de crédito: 5-10 días hábiles
// - Cuenta bancaria: 5-10 días hábiles
```

---

## 🚫 RESTRICCIONES DE PERMISOS

### Cliente (CLIENTE):

```javascript
// ✅ Puede hacer:
- Ver MIS productos
- Ver MIS órdenes
- Solicitar devolución de MIS órdenes
- Ver MIS devoluciones
- Ver MI billetera
- Ver MIS transacciones

// ❌ NO puede hacer:
- Ver devoluciones de otros clientes
- Ver todas las órdenes
- Aprobar/rechazar devoluciones
- Enviar a evaluación
- Ver billeteras de otros
```

### Manager (MANAGER):

```javascript
// ✅ Puede hacer:
- Ver TODAS las devoluciones
- Enviar a evaluación
- Aprobar devoluciones
- Rechazar devoluciones
- Ver detalles de cualquier orden relacionada

// ❌ NO puede hacer:
- Solicitar devoluciones (es manager, no cliente)
- Modificar productos
- Ver billeteras de clientes
```

### Admin (ADMIN):

```javascript
// ✅ Puede hacer:
- TODO lo que puede Manager
- Acceder al panel de Django Admin
- Crear/editar/eliminar usuarios
- Ver todas las billeteras
- Crear transacciones manualmente
```

---

## ⚠️ MANEJO DE ERRORES

### Errores Comunes y Sus Códigos:

```javascript
// 400 Bad Request
{
  "error": "La orden debe estar en estado DELIVERED",
  "code": "INVALID_ORDER_STATUS"
}

// 401 Unauthorized
{
  "detail": "Las credenciales de autenticación no se proveyeron."
}

// 403 Forbidden
{
  "detail": "No tienes permiso para realizar esta acción."
}

// 404 Not Found
{
  "detail": "No encontrado."
}

// 500 Internal Server Error
{
  "error": "Error interno del servidor"
}
```

**Manejador de errores:**

```javascript
const handleReturnError = (error) => {
  const errorMessages = {
    400: 'Datos inválidos. Revisa el formulario.',
    401: 'Sesión expirada. Por favor inicia sesión nuevamente.',
    403: 'No tienes permiso para realizar esta acción.',
    404: 'Recurso no encontrado.',
    500: 'Error del servidor. Intenta de nuevo más tarde.'
  };

  const message = errorMessages[error.status] || 'Error desconocido';
  alert(message);
};

// Uso:
try {
  const response = await createReturn(data);
  if (!response.ok) {
    throw { status: response.status };
  }
} catch (error) {
  handleReturnError(error);
}
```

---

## 📊 RESUMEN DE VALIDACIONES

| Validación | Dónde se Valida | Error si Falla |
|-----------|----------------|---------------|
| Usuario autenticado | Backend + Frontend | 401 Unauthorized |
| Rol = CLIENTE | Backend | 403 Forbidden |
| Orden pertenece al cliente | Backend | 400 Bad Request |
| Estado = DELIVERED | Backend + Frontend | 400 Bad Request |
| Plazo ≤ 30 días | Backend + Frontend | 400 Bad Request |
| No existe devolución previa | Backend | 400 Bad Request |
| Producto en la orden | Backend | 400 Bad Request |
| reason ≥ 10 caracteres | Backend + Frontend | 400 Bad Request |
| refund_method válido | Backend + Frontend | 400 Bad Request |
| Estado permite transición | Backend | 400 Bad Request |

---

**Siguiente:** Ver `09_ERRORES_COMUNES.md` para troubleshooting
