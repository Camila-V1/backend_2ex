# 🛒 02. PRODUCTOS Y ÓRDENES

## 📝 Descripción General

Antes de solicitar una devolución, el usuario debe tener una **orden entregada**. Esta sección explica cómo obtener productos y órdenes.

---

## 📦 ENDPOINTS DE PRODUCTOS

### 1. Listar Todos los Productos

**GET** `/api/products/`

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters (Opcionales):**
- `search` - Buscar por nombre
- `category` - Filtrar por categoría ID
- `ordering` - Ordenar (`price`, `-price`, `name`, `-name`)
- `page` - Número de página
- `page_size` - Cantidad por página

**Response (200 OK):**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 185,
      "name": "Banda Elástica Set",
      "description": "Set de bandas elásticas para ejercicio",
      "price": "299.99",
      "stock": 60,
      "category": {
        "id": 5,
        "name": "Deportes"
      },
      "warranty_info": "6 meses",
      "is_active": true,
      "created_at": "2025-10-01T10:00:00Z"
    },
    {
      "id": 153,
      "name": "Tablet iPad Air",
      "description": "Tablet de última generación",
      "price": "5999.99",
      "stock": 25,
      "category": {
        "id": 1,
        "name": "Electrónica"
      },
      "warranty_info": "12 meses",
      "is_active": true,
      "created_at": "2025-09-15T14:30:00Z"
    }
  ]
}
```

**Ejemplo JavaScript:**
```javascript
const getProducts = async (filters = {}) => {
  const queryParams = new URLSearchParams(filters).toString();
  const url = `http://localhost:8000/api/products/${queryParams ? '?' + queryParams : ''}`;
  
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
  });
  
  return await response.json();
};

// Uso
const products = await getProducts({ search: 'tablet', ordering: '-price' });
```

---

### 2. Ver Detalle de Producto

**GET** `/api/products/{id}/`

**Response (200 OK):**
```json
{
  "id": 153,
  "name": "Tablet iPad Air",
  "description": "Tablet de última generación con pantalla Retina",
  "price": "5999.99",
  "stock": 25,
  "category": {
    "id": 1,
    "name": "Electrónica"
  },
  "warranty_info": "12 meses de garantía del fabricante",
  "is_active": true,
  "created_at": "2025-09-15T14:30:00Z",
  "updated_at": "2025-10-20T08:15:00Z"
}
```

---

## 📋 ENDPOINTS DE ÓRDENES

### 1. Listar Mis Órdenes (Cliente)

**GET** `/api/orders/`

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters (Opcionales):**
- `status` - Filtrar por estado (`PENDING`, `PAID`, `DELIVERED`, etc.)
- `ordering` - Ordenar (`-created_at`, `created_at`)
- `page` - Número de página

**Response (200 OK):**
```json
{
  "count": 12,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 264,
      "user": 49,
      "status": "DELIVERED",
      "status_display": "Entregado",
      "total_price": "5999.99",
      "shipping_address": "Calle Falsa 123, La Paz",
      "payment_method": "CARD",
      "items": [
        {
          "id": 512,
          "product": {
            "id": 153,
            "name": "Tablet iPad Air",
            "price": "5999.99"
          },
          "quantity": 1,
          "price": "5999.99"
        }
      ],
      "created_at": "2025-10-26T00:10:23Z",
      "updated_at": "2025-10-28T15:20:00Z",
      "delivered_at": "2025-10-28T15:20:00Z"
    }
  ]
}
```

**Ejemplo JavaScript:**
```javascript
const getMyOrders = async (status = null) => {
  const params = status ? `?status=${status}` : '';
  
  const response = await fetch(`http://localhost:8000/api/orders/${params}`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
  });
  
  return await response.json();
};

// Obtener solo órdenes entregadas (elegibles para devolución)
const deliveredOrders = await getMyOrders('DELIVERED');
```

---

### 2. Ver Detalle de Orden

**GET** `/api/orders/{id}/`

**Response (200 OK):**
```json
{
  "id": 264,
  "user": 49,
  "status": "DELIVERED",
  "status_display": "Entregado",
  "total_price": "5999.99",
  "shipping_address": "Calle Falsa 123, La Paz",
  "payment_method": "CARD",
  "payment_method_display": "Tarjeta de crédito",
  "items": [
    {
      "id": 512,
      "product": {
        "id": 153,
        "name": "Tablet iPad Air",
        "price": "5999.99",
        "category": "Electrónica"
      },
      "quantity": 1,
      "price": "5999.99"
    }
  ],
  "created_at": "2025-10-26T00:10:23.209078Z",
  "updated_at": "2025-10-28T15:20:00Z",
  "paid_at": "2025-10-26T00:15:30Z",
  "delivered_at": "2025-10-28T15:20:00Z"
}
```

---

## 📊 Estados de Órdenes

| Estado | Valor | Descripción | ¿Puede solicitar devolución? |
|--------|-------|-------------|------------------------------|
| Pendiente | `PENDING` | Orden creada, esperando pago | ❌ NO |
| Pagada | `PAID` | Pago confirmado, procesando | ❌ NO |
| En camino | `SHIPPED` | Orden enviada al cliente | ❌ NO |
| Entregada | `DELIVERED` | Orden recibida por cliente | ✅ **SÍ** |
| Cancelada | `CANCELLED` | Orden cancelada | ❌ NO |

**IMPORTANTE:** Solo órdenes con estado `DELIVERED` pueden tener devoluciones.

---

## 🎨 Componentes Frontend Sugeridos

### Componente: Lista de Órdenes

```jsx
import { useState, useEffect } from 'react';

const MyOrders = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      const data = await getMyOrders();
      setOrders(data.results);
    } catch (error) {
      console.error('Error loading orders:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando órdenes...</div>;

  return (
    <div className="orders-list">
      <h2>Mis Órdenes</h2>
      {orders.map(order => (
        <OrderCard key={order.id} order={order} />
      ))}
    </div>
  );
};

const OrderCard = ({ order }) => {
  const canReturn = order.status === 'DELIVERED';

  return (
    <div className="order-card">
      <div className="order-header">
        <h3>Orden #{order.id}</h3>
        <span className={`status status-${order.status.toLowerCase()}`}>
          {order.status_display}
        </span>
      </div>

      <div className="order-items">
        {order.items.map(item => (
          <div key={item.id} className="order-item">
            <span>{item.product.name}</span>
            <span>x{item.quantity}</span>
            <span>${item.price}</span>
          </div>
        ))}
      </div>

      <div className="order-footer">
        <div className="order-total">
          Total: ${order.total_price}
        </div>
        
        {canReturn && (
          <button 
            onClick={() => openReturnModal(order)}
            className="btn-return"
          >
            Solicitar Devolución
          </button>
        )}
      </div>

      <div className="order-dates">
        <small>Creada: {new Date(order.created_at).toLocaleDateString()}</small>
        {order.delivered_at && (
          <small>Entregada: {new Date(order.delivered_at).toLocaleDateString()}</small>
        )}
      </div>
    </div>
  );
};
```

---

### Componente: Selector de Producto para Devolución

```jsx
const ProductSelector = ({ order, onSelect }) => {
  const [selectedProduct, setSelectedProduct] = useState(null);

  const handleSelect = (item) => {
    setSelectedProduct(item);
    onSelect({
      order_id: order.id,
      product_id: item.product.id,
      max_quantity: item.quantity,
      product_name: item.product.name,
      product_price: item.product.price
    });
  };

  return (
    <div className="product-selector">
      <h3>Seleccionar producto a devolver:</h3>
      <p className="order-info">Orden #{order.id}</p>
      
      <div className="products-grid">
        {order.items.map(item => (
          <div 
            key={item.id}
            className={`product-item ${selectedProduct?.id === item.id ? 'selected' : ''}`}
            onClick={() => handleSelect(item)}
          >
            <h4>{item.product.name}</h4>
            <p>Cantidad: {item.quantity}</p>
            <p>Precio: ${item.price}</p>
            <span className="category">{item.product.category}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

## 🔍 Filtros Útiles

### Filtrar órdenes entregadas (elegibles para devolución):

```javascript
const getReturnableOrders = async () => {
  return await getMyOrders('DELIVERED');
};
```

### Buscar productos por categoría:

```javascript
const getProductsByCategory = async (categoryId) => {
  return await getProducts({ category: categoryId });
};
```

### Productos ordenados por precio:

```javascript
const getExpensiveProducts = async () => {
  return await getProducts({ ordering: '-price' }); // De mayor a menor
};
```

---

## ⚠️ Validaciones Importantes

### Antes de mostrar botón "Solicitar Devolución":

```javascript
const canRequestReturn = (order) => {
  // 1. Debe estar entregada
  if (order.status !== 'DELIVERED') {
    return { can: false, reason: 'La orden debe estar entregada' };
  }

  // 2. No debe tener más de 30 días (opcional, según política)
  const deliveredDate = new Date(order.delivered_at);
  const daysSinceDelivery = (new Date() - deliveredDate) / (1000 * 60 * 60 * 24);
  
  if (daysSinceDelivery > 30) {
    return { can: false, reason: 'Han pasado más de 30 días desde la entrega' };
  }

  return { can: true };
};
```

---

**Siguiente:** Ver `03_DEVOLUCIONES.md` para el sistema completo de devoluciones (PRINCIPAL)
