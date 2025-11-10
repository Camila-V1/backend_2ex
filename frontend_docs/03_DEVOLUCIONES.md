# 🔄 03. SISTEMA DE DEVOLUCIONES (PRINCIPAL)

## 📝 Descripción General

Este es el **módulo principal** del sistema. Permite a los clientes solicitar devoluciones de productos entregados y a los managers gestionarlas.

---

## 🎯 Flujo Completo de Devolución

```
┌─────────────────┐
│ 1. CLIENTE      │
│ Solicita        │  POST /deliveries/returns/
│ Devolución      │  ➜ Estado: REQUESTED
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. MANAGER      │
│ Envía a         │  POST /deliveries/returns/{id}/send_to_evaluation/
│ Evaluación      │  ➜ Estado: IN_EVALUATION
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. MANAGER      │
│ Aprueba o       │  POST /deliveries/returns/{id}/approve/
│ Rechaza         │  ➜ Estado: COMPLETED / REJECTED
└────────┬────────┘
         │
         ▼ (Si aprueba)
┌─────────────────┐
│ 4. SISTEMA      │
│ Procesa         │  - Crea billetera automáticamente
│ Reembolso       │  - Agrega saldo
└─────────────────┘  - Envía email
```

---

## 📌 ENDPOINTS PARA CLIENTE

### 1. Solicitar Devolución

**POST** `/api/deliveries/returns/`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "order_id": 264,
  "product_id": 153,
  "quantity": 1,
  "reason": "DEFECTIVE",
  "description": "El producto no cumple con las especificaciones anunciadas. La pantalla tiene píxeles muertos.",
  "refund_method": "WALLET"
}
```

**Campos:**
- `order_id` **(requerido)** - ID de la orden (debe estar DELIVERED)
- `product_id` **(requerido)** - ID del producto a devolver (debe estar en la orden)
- `quantity` **(requerido)** - Cantidad a devolver (máximo la cantidad comprada)
- `reason` **(requerido)** - Razón de devolución (ver tabla abajo)
- `description` **(requerido)** - Descripción detallada del problema
- `refund_method` **(requerido)** - Método de reembolso: `"WALLET"` o `"ORIGINAL"`

**Razones de Devolución (reason):**
| Valor | Significado |
|-------|-------------|
| `DEFECTIVE` | Producto defectuoso |
| `NOT_AS_DESCRIBED` | No coincide con la descripción |
| `WRONG_ITEM` | Artículo incorrecto |
| `DAMAGED_SHIPPING` | Dañado en envío |
| `CHANGED_MIND` | Cambió de opinión |
| `OTHER` | Otra razón |

**Response (201 CREATED):**
```json
{
  "id": 21,
  "order": 264,
  "product": 153,
  "user": 49,
  "quantity": 1,
  "reason": "DEFECTIVE",
  "reason_display": "Producto defectuoso",
  "description": "El producto no cumple con las especificaciones...",
  "status": "REQUESTED",
  "status_display": "Solicitada por cliente",
  "product_details": {
    "id": 153,
    "name": "Tablet iPad Air",
    "price": "5999.99",
    "category": "Electrónica"
  },
  "order_details": {
    "id": 264,
    "order_number": "#264",
    "order_date": "2025-10-26T00:10:23.209078+00:00",
    "total_price": "5999.99",
    "status": "DELIVERED"
  },
  "customer_details": {
    "id": 49,
    "username": "juan_cliente",
    "email": "juan@email.com",
    "full_name": "Juan Pérez"
  },
  "refund_amount": "0.00",
  "refund_method": "WALLET",
  "refund_method_display": "Billetera virtual",
  "requested_at": "2025-11-10T22:30:54.390959Z",
  "evaluated_at": null,
  "processed_at": null,
  "completed_at": null,
  "message": "Solicitud de devolución creada. Un manager la revisará pronto."
}
```

**Ejemplo JavaScript:**
```javascript
const requestReturn = async (returnData) => {
  const response = await fetch('http://localhost:8000/api/deliveries/returns/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(returnData)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al solicitar devolución');
  }

  return await response.json();
};

// Uso
const newReturn = await requestReturn({
  order_id: 264,
  product_id: 153,
  quantity: 1,
  reason: 'DEFECTIVE',
  description: 'La pantalla tiene píxeles muertos y no enciende correctamente.',
  refund_method: 'WALLET'
});

console.log('✅ Devolución creada:', newReturn.id);
```

---

### 2. Ver Mis Devoluciones

**GET** `/api/deliveries/returns/`

**Query Parameters:**
- `status` - Filtrar por estado (`REQUESTED`, `IN_EVALUATION`, `COMPLETED`, `REJECTED`)
- `ordering` - Ordenar (`-created_at`, `created_at`)

**Response (200 OK):**
```json
{
  "count": 9,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 21,
      "order": 264,
      "product": 153,
      "status": "COMPLETED",
      "status_display": "Completada - Reembolso realizado",
      "reason_display": "Producto defectuoso",
      "refund_amount": "5999.99",
      "refund_method_display": "Billetera virtual",
      "requested_at": "2025-11-10T22:30:54Z",
      "completed_at": "2025-11-10T22:31:00Z",
      "product_details": {
        "id": 153,
        "name": "Tablet iPad Air",
        "price": "5999.99"
      }
    }
  ]
}
```

**Ejemplo JavaScript:**
```javascript
const getMyReturns = async (status = null) => {
  const params = status ? `?status=${status}` : '';
  
  const response = await fetch(`http://localhost:8000/api/deliveries/returns/${params}`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
  });

  return await response.json();
};

// Ver solo devoluciones completadas
const completedReturns = await getMyReturns('COMPLETED');
```

---

### 3. Ver Detalle de Devolución

**GET** `/api/deliveries/returns/{id}/`

**Response (200 OK):**
```json
{
  "id": 21,
  "order": 264,
  "product": 153,
  "user": 49,
  "quantity": 1,
  "reason": "DEFECTIVE",
  "reason_display": "Producto defectuoso",
  "description": "El producto no cumple con las especificaciones anunciadas...",
  "status": "COMPLETED",
  "status_display": "Completada - Reembolso realizado",
  "product_details": {
    "id": 153,
    "name": "Tablet iPad Air",
    "price": "5999.99",
    "category": "Electrónica"
  },
  "order_details": {
    "id": 264,
    "order_number": "#264",
    "order_date": "2025-10-26T00:10:23.209078+00:00",
    "total_price": "5999.99",
    "status": "DELIVERED"
  },
  "customer_details": {
    "id": 49,
    "username": "juan_cliente",
    "email": "juan@email.com",
    "full_name": "Juan Pérez"
  },
  "evaluation_notes": "Producto verificado. Píxeles muertos confirmados.",
  "manager_notes": "",
  "refund_amount": "5999.99",
  "refund_method": "WALLET",
  "refund_method_display": "Billetera virtual",
  "requested_at": "2025-11-10T22:30:54Z",
  "evaluated_at": "2025-11-10T22:31:00Z",
  "processed_at": "2025-11-10T22:31:00Z",
  "completed_at": "2025-11-10T22:31:00Z",
  "created_at": "2025-11-10T22:30:54Z",
  "updated_at": "2025-11-10T22:31:00Z"
}
```

---

## 📌 ENDPOINTS PARA MANAGER/ADMIN

### 4. Listar Todas las Devoluciones (Manager)

**GET** `/api/deliveries/returns/`

**Permisos:** Manager o Admin

**Response:** Igual que endpoint de cliente, pero devuelve TODAS las devoluciones del sistema.

---

### 5. Enviar a Evaluación Física

**POST** `/api/deliveries/returns/{id}/send_to_evaluation/`

**Permisos:** Manager o Admin

**Request Body:** Vacío `{}`

**Response (200 OK):**
```json
{
  "id": 21,
  "status": "IN_EVALUATION",
  "message": "Devolución enviada a evaluación física"
}
```

**Ejemplo JavaScript:**
```javascript
const sendToEvaluation = async (returnId) => {
  const response = await fetch(
    `http://localhost:8000/api/deliveries/returns/${returnId}/send_to_evaluation/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    }
  );

  return await response.json();
};
```

---

### 6. Aprobar Devolución y Procesar Reembolso

**POST** `/api/deliveries/returns/{id}/approve/`

**Permisos:** Manager o Admin

**Request Body:**
```json
{
  "evaluation_notes": "Producto verificado. Píxeles muertos confirmados en zona superior derecha. Aprobada para reembolso completo.",
  "refund_amount": 5999.99
}
```

**Campos:**
- `evaluation_notes` **(requerido)** - Notas del manager sobre la evaluación
- `refund_amount` **(requerido)** - Monto a reembolsar

**Response (200 OK):**
```json
{
  "id": 21,
  "status": "COMPLETED",
  "message": "✅ Devolución aprobada.",
  "refund_status": "success",
  "refund_message": "Reembolso de $5999.99 agregado a la billetera virtual.",
  "refund_details": {
    "method": "WALLET",
    "wallet_id": 2,
    "transaction_id": 6,
    "new_balance": "29999.95"
  },
  "evaluation_notes": "Producto verificado...",
  "refund_amount": "5999.99",
  "processed_at": "2025-11-10T22:31:00Z",
  "completed_at": "2025-11-10T22:31:00Z"
}
```

**Ejemplo JavaScript:**
```javascript
const approveReturn = async (returnId, evaluationNotes, refundAmount) => {
  const response = await fetch(
    `http://localhost:8000/api/deliveries/returns/${returnId}/approve/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        evaluation_notes: evaluationNotes,
        refund_amount: refundAmount
      })
    }
  );

  return await response.json();
};
```

---

### 7. Rechazar Devolución

**POST** `/api/deliveries/returns/{id}/reject/`

**Permisos:** Manager o Admin

**Request Body:**
```json
{
  "evaluation_notes": "El producto no presenta defectos. Los daños son por mal uso del cliente."
}
```

**Response (200 OK):**
```json
{
  "id": 21,
  "status": "REJECTED",
  "message": "Devolución rechazada",
  "evaluation_notes": "El producto no presenta defectos..."
}
```

---

## 📊 Estados de Devolución

| Estado | Valor | Descripción | Quién puede verlo |
|--------|-------|-------------|-------------------|
| Solicitada | `REQUESTED` | Cliente solicitó devolución | Cliente, Manager |
| En Evaluación | `IN_EVALUATION` | Manager envió a evaluación física | Cliente, Manager |
| Aprobada | `APPROVED` | Manager aprobó (temporal) | Manager |
| Completada | `COMPLETED` | Reembolso procesado exitosamente | Cliente, Manager |
| Rechazada | `REJECTED` | Manager rechazó la solicitud | Cliente, Manager |
| Cancelada | `CANCELLED` | Cliente canceló la solicitud | Cliente, Manager |

---

## 🎨 Componente Frontend: Formulario de Devolución

```jsx
import { useState } from 'react';

const ReturnRequestForm = ({ order, product, onSuccess }) => {
  const [formData, setFormData] = useState({
    order_id: order.id,
    product_id: product.id,
    quantity: 1,
    reason: '',
    description: '',
    refund_method: 'WALLET'
  });

  const reasons = [
    { value: 'DEFECTIVE', label: 'Producto defectuoso' },
    { value: 'NOT_AS_DESCRIBED', label: 'No coincide con descripción' },
    { value: 'WRONG_ITEM', label: 'Artículo incorrecto' },
    { value: 'DAMAGED_SHIPPING', label: 'Dañado en envío' },
    { value: 'CHANGED_MIND', label: 'Cambié de opinión' },
    { value: 'OTHER', label: 'Otra razón' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const result = await requestReturn(formData);
      alert('✅ Devolución solicitada correctamente');
      onSuccess(result);
    } catch (error) {
      alert('❌ Error: ' + error.message);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="return-form">
      <h2>Solicitar Devolución</h2>
      
      <div className="form-group">
        <label>Producto:</label>
        <p><strong>{product.name}</strong></p>
        <p>Precio: ${product.price}</p>
      </div>

      <div className="form-group">
        <label>Cantidad a devolver:</label>
        <input
          type="number"
          min="1"
          max={product.quantity}
          value={formData.quantity}
          onChange={(e) => setFormData({...formData, quantity: parseInt(e.target.value)})}
          required
        />
      </div>

      <div className="form-group">
        <label>Razón de la devolución: *</label>
        <select
          value={formData.reason}
          onChange={(e) => setFormData({...formData, reason: e.target.value})}
          required
        >
          <option value="">Seleccionar...</option>
          {reasons.map(r => (
            <option key={r.value} value={r.value}>{r.label}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Descripción detallada del problema: *</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({...formData, description: e.target.value})}
          placeholder="Explica detalladamente el motivo de la devolución..."
          rows="4"
          required
          minLength="20"
        />
        <small>{formData.description.length} caracteres (mínimo 20)</small>
      </div>

      <div className="form-group">
        <label>Método de reembolso:</label>
        <div className="radio-group">
          <label>
            <input
              type="radio"
              value="WALLET"
              checked={formData.refund_method === 'WALLET'}
              onChange={(e) => setFormData({...formData, refund_method: e.target.value})}
            />
            Billetera virtual (más rápido)
          </label>
          <label>
            <input
              type="radio"
              value="ORIGINAL"
              checked={formData.refund_method === 'ORIGINAL'}
              onChange={(e) => setFormData({...formData, refund_method: e.target.value})}
            />
            Método de pago original (3-5 días)
          </label>
        </div>
      </div>

      <button type="submit" className="btn-primary">
        Solicitar Devolución
      </button>
    </form>
  );
};
```

---

## ⚠️ Validaciones del Backend

### Errores Comunes:

**400 - Orden no está DELIVERED:**
```json
{
  "error": "La orden debe estar en estado DELIVERED para solicitar una devolución"
}
```

**400 - Producto no está en la orden:**
```json
{
  "error": "El producto no se encuentra en esta orden"
}
```

**400 - Cantidad excede disponible:**
```json
{
  "quantity": ["La cantidad a devolver no puede exceder la cantidad comprada"]
}
```

---

**Siguiente:** Ver `04_BILLETERA_VIRTUAL.md` para sistema de wallet y transacciones
