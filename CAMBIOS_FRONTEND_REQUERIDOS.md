# 🚀 CAMBIOS REQUERIDOS EN EL FRONTEND

## 📋 Resumen

Después de implementar las correcciones en el backend para:
1. **NLP mejorado** (búsqueda inteligente con plurales/sinónimos)
2. **Agregar al carrito sin crear orden** (permite al usuario seguir comprando)
3. **Flujo de pago seguro** (stock se reduce solo después del pago confirmado)

El frontend **DEBE** actualizarse para manejar el nuevo flujo de respuestas del backend.

---

## ✅ NUEVO COMPORTAMIENTO: Agregar al Carrito

### 🎯 Flujo Actual (v2.2)

El backend ahora **NO crea una orden inmediatamente**. En su lugar, devuelve la información de los productos para que el frontend los agregue al carrito:

```json
{
  "success": true,
  "message": "Se encontraron 2 producto(s) para agregar al carrito",
  "prompt": "agrega 2 laptops",
  "interpreted_action": "add_to_cart",
  "cart_action": "add_to_cart",
  "items": [
    {
      "product_id": 5,
      "name": "Laptop Dell Inspiron 15",
      "description": "Laptop potente para trabajo y gaming",
      "price": "799.99",
      "quantity": 2,
      "subtotal": "1599.98",
      "stock_available": 15,
      "image_url": "https://..."
    }
  ],
  "total": "1599.98"
}
```

**✅ VENTAJAS:**
- Usuario puede seguir agregando productos
- No crea órdenes innecesarias
- Carrito persiste en localStorage
- Usuario decide cuándo hacer checkout

---

## 🔧 CAMBIOS ESPECÍFICOS POR COMPONENTE

### 1️⃣ Servicio NLP (`nlpService.js`)

**Archivo:** `src/services/nlpService.js`

**✅ Código Recomendado:**
```javascript
export const nlpService = {
  async addToCartNLP(prompt) {
    const response = await api.post('/orders/cart/add-natural-language/', {
      prompt
    });
    
    // El backend ahora devuelve items para agregar al carrito
    return response.data;
  }
};
```

---

### 2️⃣ Componente VoiceCart (`VoiceCart.jsx`)

**Archivo:** `src/components/VoiceCart.jsx`

**✅ Código Nuevo:**
```jsx
import { useState } from 'react';
import { nlpService } from '../services/nlpService';
import { useCart } from '../hooks/useCart';  // Hook del carrito

function VoiceCart() {
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState(null);
  const [listening, setListening] = useState(false);
  const [loading, setLoading] = useState(false);
  const { addToCart } = useCart();  // Función para agregar al carrito

  const handleSubmit = async (text = prompt) => {
    if (!text.trim()) return;
    setLoading(true);

    try {
      const data = await nlpService.addToCartNLP(text);
      
      if (data.success && data.cart_action === 'add_to_cart') {
        // ✅ NUEVO: Agregar productos al carrito del frontend
        data.items.forEach(item => {
          addToCart({
            id: item.product_id,
            name: item.name,
            price: parseFloat(item.price),
            image_url: item.image_url,
            stock: item.stock_available
          }, item.quantity);
        });
        
        // Mostrar mensaje de éxito
        alert(`✅ ${data.message}\n\nTotal: $${data.total}`);
        setResult(data);
        setPrompt(''); // Limpiar input
        
      } else if (data.error) {
        alert(`❌ ${data.error}`);
        setResult(data);
      }
    } catch (error) {
      alert('Error: ' + (error.response?.data?.error || error.detail || 'Error desconocido'));
    } finally {
      setLoading(false);
    }
  };

  // Reconocimiento de voz (Web Speech API)
  const startListening = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Tu navegador no soporta reconocimiento de voz');
      return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'es-ES';
    recognition.continuous = false;

    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setPrompt(transcript);
      handleSubmit(transcript);
    };

    recognition.start();
  };

  return (
    <div className="voice-cart">
      <h3>🎤 Agregar Productos por Voz o Texto</h3>

      <div className="input-group">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder='Ej: "Agrega 2 laptops al carrito"'
          onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
          disabled={loading}
        />
        <button onClick={() => handleSubmit()} disabled={loading}>
          {loading ? 'Procesando...' : 'Enviar'}
        </button>
        <button
          onClick={startListening}
          disabled={listening || loading}
          className="voice-button"
        >
          {listening ? '🔴 Escuchando...' : '🎤 Hablar'}
        </button>
      </div>

      {result && result.success && (
        <div className="result success">
          <p><strong>✅ {result.message}</strong></p>
          <div className="items-added">
            <h4>Productos agregados:</h4>
            {result.items.map(item => (
              <div key={item.product_id} className="item-card">
                <span className="item-name">{item.name}</span>
                <span className="item-quantity">x{item.quantity}</span>
                <span className="item-price">${item.subtotal}</span>
              </div>
            ))}
            <div className="total">
              <strong>Total: ${result.total}</strong>
            </div>
          </div>
        </div>
      )}

      {result && !result.success && (
        <div className="result error">
          <p><strong>❌ {result.error}</strong></p>
        </div>
      )}

      <div className="examples">
        <p><strong>Ejemplos:</strong></p>
        <ul>
          <li>"Agrega 2 laptops al carrito"</li>
          <li>"Quiero 3 smartphones"</li>
          <li>"Añade 1 mouse inalámbrico"</li>
          <li>"Comprar 5 auriculares"</li>
        </ul>
      </div>
    </div>
  );
}

export default VoiceCart;
```

---

### 3️⃣ Hook de Carrito (`useCart.js`)

**Archivo:** `src/hooks/useCart.js`

Si no tienes este hook, créalo. Es esencial para manejar el carrito en el frontend:

```javascript
import { useState, useEffect } from 'react';

export function useCart() {
  const [cart, setCart] = useState([]);

  // Cargar carrito desde localStorage al iniciar
  useEffect(() => {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      try {
        setCart(JSON.parse(savedCart));
      } catch (error) {
        console.error('Error al cargar carrito:', error);
        setCart([]);
      }
    }
  }, []);

  // Guardar carrito en localStorage cada vez que cambie
  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cart));
  }, [cart]);

  // Agregar producto al carrito
  const addToCart = (product, quantity = 1) => {
    setCart(prevCart => {
      const existingItem = prevCart.find(item => item.id === product.id);
      
      if (existingItem) {
        // Si ya existe, actualizar cantidad
        return prevCart.map(item =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      }

      // Si no existe, agregar nuevo item
      return [...prevCart, {
        id: product.id,
        name: product.name,
        price: product.price,
        quantity: quantity,
        image_url: product.image_url,
        stock: product.stock
      }];
    });
  };

  // Remover producto del carrito
  const removeFromCart = (productId) => {
    setCart(prevCart => prevCart.filter(item => item.id !== productId));
  };

  // Actualizar cantidad de un producto
  const updateQuantity = (productId, quantity) => {
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }

    setCart(prevCart =>
      prevCart.map(item =>
        item.id === productId ? { ...item, quantity } : item
      )
    );
  };

  // Limpiar carrito
  const clearCart = () => {
    setCart([]);
    localStorage.removeItem('cart');
  };

  // Calcular total
  const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  // Calcular cantidad total de items
  const itemCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  return {
    cart,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    total,
    itemCount
  };
}
```

---

### 4️⃣ Componente de Checkout (`Checkout.jsx`)

**Archivo:** `src/components/Checkout.jsx`

**✅ Código Completo:**
```jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../hooks/useCart';
import { orderService } from '../services/orderService';
import { stripeService } from '../services/stripeService';

function Checkout() {
  const { cart, total, clearCart } = useCart();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleCheckout = async () => {
    if (cart.length === 0) {
      alert('El carrito está vacío');
      return;
    }

    setLoading(true);

    try {
      // 1. Crear la orden desde el carrito
      const order = await orderService.createOrder(cart);
      
      // 2. Crear sesión de Stripe para pagar
      const checkoutUrl = await stripeService.createCheckoutSession(order.id);
      
      // 3. Guardar order_id para referencia después del pago
      localStorage.setItem('pending_order_id', order.id);
      
      // 4. Redirigir a Stripe Checkout
      window.location.href = checkoutUrl;
      
    } catch (error) {
      alert('Error: ' + (error.response?.data?.error || error.detail || 'Error desconocido'));
      setLoading(false);
    }
  };

  if (cart.length === 0) {
    return (
      <div className="checkout-empty">
        <h2>Tu carrito está vacío</h2>
        <p>Agrega productos para continuar</p>
        <button onClick={() => navigate('/products')}>
          Ver Productos
        </button>
      </div>
    );
  }

  return (
    <div className="checkout">
      <h2>Resumen de Compra</h2>

      <div className="cart-items">
        {cart.map(item => (
          <div key={item.id} className="cart-item">
            <div className="item-image">
              {item.image_url && <img src={item.image_url} alt={item.name} />}
            </div>
            <div className="item-details">
              <h4>{item.name}</h4>
              <p className="item-quantity">Cantidad: {item.quantity}</p>
              <p className="item-price">
                ${item.price} x {item.quantity} = ${(item.price * item.quantity).toFixed(2)}
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="checkout-summary">
        <div className="summary-row">
          <span>Subtotal:</span>
          <span>${total.toFixed(2)}</span>
        </div>
        <div className="summary-row total">
          <strong>Total:</strong>
          <strong>${total.toFixed(2)}</strong>
        </div>
      </div>

      <button 
        className="btn-checkout"
        onClick={handleCheckout} 
        disabled={loading}
      >
        {loading ? 'Procesando...' : '💳 Proceder al Pago'}
      </button>

      <button 
        className="btn-back"
        onClick={() => navigate('/products')}
        disabled={loading}
      >
        ← Seguir Comprando
      </button>
    </div>
  );
}

export default Checkout;
```

---

### 5️⃣ Componente de Carrito (`Cart.jsx`)

**Archivo:** `src/components/Cart.jsx`

Componente para visualizar y editar el carrito:

```jsx
import { useCart } from '../hooks/useCart';
import { useNavigate } from 'react-router-dom';

function Cart() {
  const { cart, removeFromCart, updateQuantity, clearCart, total, itemCount } = useCart();
  const navigate = useNavigate();

  if (cart.length === 0) {
    return (
      <div className="cart-empty">
        <h2>🛒 Tu carrito está vacío</h2>
        <p>Usa el buscador por voz o navega por los productos</p>
        <button onClick={() => navigate('/products')}>
          Ver Productos
        </button>
      </div>
    );
  }

  return (
    <div className="cart-page">
      <div className="cart-header">
        <h2>🛒 Mi Carrito ({itemCount} items)</h2>
        <button className="btn-clear" onClick={clearCart}>
          Vaciar Carrito
        </button>
      </div>

      <div className="cart-items">
        {cart.map(item => (
          <div key={item.id} className="cart-item-card">
            {item.image_url && (
              <img src={item.image_url} alt={item.name} className="item-image" />
            )}
            
            <div className="item-info">
              <h3>{item.name}</h3>
              <p className="item-price">${item.price}</p>
              {item.stock && (
                <p className="item-stock">Stock: {item.stock} disponibles</p>
              )}
            </div>

            <div className="item-actions">
              <div className="quantity-control">
                <button
                  onClick={() => updateQuantity(item.id, item.quantity - 1)}
                  disabled={item.quantity <= 1}
                >
                  -
                </button>
                <input
                  type="number"
                  value={item.quantity}
                  onChange={(e) => updateQuantity(item.id, parseInt(e.target.value) || 1)}
                  min="1"
                  max={item.stock || 999}
                />
                <button
                  onClick={() => updateQuantity(item.id, item.quantity + 1)}
                  disabled={item.stock && item.quantity >= item.stock}
                >
                  +
                </button>
              </div>

              <p className="item-subtotal">
                Subtotal: ${(item.price * item.quantity).toFixed(2)}
              </p>

              <button
                className="btn-remove"
                onClick={() => removeFromCart(item.id)}
              >
                🗑️ Eliminar
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="cart-summary">
        <div className="summary-details">
          <p>Items: {itemCount}</p>
          <h3>Total: ${total.toFixed(2)}</h3>
        </div>

        <button
          className="btn-checkout-primary"
          onClick={() => navigate('/checkout')}
        >
          💳 Proceder al Pago
        </button>

        <button
          className="btn-continue-shopping"
          onClick={() => navigate('/products')}
        >
          ← Continuar Comprando
        </button>
      </div>
    </div>
  );
}

export default Cart;
```

**Estas páginas YA deberían existir, pero verifica que funcionen correctamente.**

#### Página de Éxito (`PaymentSuccess.jsx`)

**Archivo:** `src/pages/PaymentSuccess.jsx`

```jsx
import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { orderService } from '../services/orderService';

function PaymentSuccess() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const sessionId = searchParams.get('session_id');
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadOrderDetails();
  }, []);

  const loadOrderDetails = async () => {
    try {
      // Recuperar order_id guardado
      const orderId = localStorage.getItem('pending_order_id');
      
      if (orderId) {
        const orderData = await orderService.getOrderById(orderId);
        setOrder(orderData);
        
        // Limpiar carrito si existe
        localStorage.removeItem('cart');
        localStorage.removeItem('pending_order_id');
      }
    } catch (error) {
      console.error('Error al cargar orden:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Verificando pago...</div>;
  }

  return (
    <div className="payment-success">
      <div className="success-icon">✅</div>
      <h1>¡Pago Exitoso!</h1>
      
      {order && (
        <div className="order-details">
          <h2>Orden #{order.id}</h2>
          <p><strong>Estado:</strong> {order.status}</p>
          <p><strong>Total pagado:</strong> ${order.total_price}</p>
          
          <div className="order-items">
            <h3>Productos:</h3>
            {order.items.map(item => (
              <div key={item.id}>
                {item.product_name} x{item.quantity} - ${item.price}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="actions">
        <button onClick={() => navigate('/orders')}>
          Ver todas mis órdenes
        </button>
        <button onClick={() => navigate('/products')}>
          Seguir comprando
        </button>
      </div>

      {sessionId && (
        <small>Stripe Session ID: {sessionId}</small>
      )}
    </div>
  );
}

export default PaymentSuccess;
```

#### Página de Cancelación (`PaymentCancelled.jsx`)

**Archivo:** `src/pages/PaymentCancelled.jsx`

```jsx
import { useNavigate } from 'react-router-dom';

function PaymentCancelled() {
  const navigate = useNavigate();

  return (
    <div className="payment-cancelled">
      <div className="cancel-icon">❌</div>
      <h1>Pago Cancelado</h1>
      <p>No se realizó ningún cargo a tu tarjeta.</p>
      <p>Tu orden sigue pendiente de pago.</p>

      <div className="actions">
        <button onClick={() => navigate('/cart')}>
          Volver al carrito
        </button>
        <button onClick={() => navigate('/orders')}>
          Ver mis órdenes pendientes
        </button>
      </div>
    </div>
  );
}

export default PaymentCancelled;
```

---

### 5️⃣ Lista de Órdenes (`OrderList.jsx`)

**Archivo:** `src/components/OrderList.jsx`

**Cambio:** Ahora las órdenes tienen estado `PENDING` hasta que se pague. Mostrar botón de pago para órdenes pendientes.

```jsx
import { useState, useEffect } from 'react';
import { orderService } from '../services/orderService';
import { stripeService } from '../services/stripeService';

function OrderList() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      const data = await orderService.getMyOrders();
      setOrders(data);
    } catch (error) {
      console.error('Error al cargar órdenes:', error);
    }
  };

  const handlePayPendingOrder = async (orderId) => {
    try {
      const checkoutUrl = await stripeService.createCheckoutSession(orderId);
      localStorage.setItem('pending_order_id', orderId);
      window.location.href = checkoutUrl;
    } catch (error) {
      alert('Error al iniciar pago: ' + error.detail);
    }
  };

  // Función para obtener clase CSS según estado
  const getStatusClass = (status) => {
    const classes = {
      'pending': 'status-pending',
      'paid': 'status-paid',
      'shipped': 'status-shipped',
      'delivered': 'status-delivered',
      'cancelled': 'status-cancelled'
    };
    return classes[status.toLowerCase()] || 'status-default';
  };

  // Función para traducir estado
  const getStatusLabel = (status) => {
    const labels = {
      'pending': '⏳ Pendiente de Pago',
      'paid': '✅ Pagado',
      'shipped': '📦 Enviado',
      'delivered': '🎉 Entregado',
      'cancelled': '❌ Cancelado'
    };
    return labels[status.toLowerCase()] || status;
  };

  return (
    <div className="order-list">
      <h2>Mis Órdenes</h2>

      {orders.length === 0 ? (
        <p>No tienes órdenes aún.</p>
      ) : (
        <div className="orders-grid">
          {orders.map(order => (
            <div key={order.id} className="order-card">
              <div className="order-header">
                <h3>Orden #{order.id}</h3>
                <span className={getStatusClass(order.status)}>
                  {getStatusLabel(order.status)}
                </span>
              </div>

              <div className="order-details">
                <p><strong>Fecha:</strong> {new Date(order.created_at).toLocaleDateString()}</p>
                <p><strong>Total:</strong> ${order.total_price}</p>
                <p><strong>Items:</strong> {order.items?.length || 0}</p>
              </div>

              <div className="order-items">
                {order.items?.map(item => (
                  <div key={item.id} className="order-item">
                    {item.product_name} x{item.quantity}
                  </div>
                ))}
              </div>

              <div className="order-actions">
                {/* Botón de pago solo para órdenes pendientes */}
                {order.status.toLowerCase() === 'pending' && (
                  <button
                    className="btn-pay"
                    onClick={() => handlePayPendingOrder(order.id)}
                  >
                    💳 Pagar Ahora
                  </button>
                )}

                <button onClick={() => viewOrderDetails(order.id)}>
                  Ver Detalles
                </button>

                {/* Botón de cancelar solo para órdenes pendientes */}
                {order.status.toLowerCase() === 'pending' && (
                  <button
                    className="btn-cancel"
                    onClick={() => cancelOrder(order.id)}
                  >
                    Cancelar
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default OrderList;
```

---

### 6️⃣ Estilos CSS para Estados de Orden

**Archivo:** `src/styles/orders.css`

```css
/* Estados de orden */
.status-pending {
  background-color: #fef3c7;
  color: #92400e;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.status-paid {
  background-color: #d1fae5;
  color: #065f46;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.status-shipped {
  background-color: #dbeafe;
  color: #1e40af;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.status-delivered {
  background-color: #e9d5ff;
  color: #6b21a8;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.status-cancelled {
  background-color: #fee2e2;
  color: #991b1b;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

/* Botones de acción */
.btn-pay {
  background-color: #10b981;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s;
}

.btn-pay:hover {
  background-color: #059669;
}

.btn-cancel {
  background-color: #ef4444;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s;
}

.btn-cancel:hover {
  background-color: #dc2626;
}

/* Orden card */
.order-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.order-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}
```

---

## 7️⃣ Rutas de la Aplicación

**Archivo:** `src/App.jsx` o `src/router.jsx`

Asegúrate de tener estas rutas configuradas:

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import PaymentSuccess from './pages/PaymentSuccess';
import PaymentCancelled from './pages/PaymentCancelled';
import OrderList from './components/OrderList';
import Checkout from './components/Checkout';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Rutas existentes */}
        <Route path="/" element={<Home />} />
        <Route path="/products" element={<ProductList />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/checkout" element={<Checkout />} />
        <Route path="/orders" element={<OrderList />} />
        
        {/* ✅ NUEVAS RUTAS REQUERIDAS para Stripe */}
        <Route path="/payment-success" element={<PaymentSuccess />} />
        <Route path="/payment-cancelled" element={<PaymentCancelled />} />
        <Route path="/orders/:id/success" element={<PaymentSuccess />} />
        
        {/* Otras rutas */}
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 📦 Variables de Entorno

**Archivo:** `.env`

Verifica que tengas estas variables configuradas:

```env
# API Backend
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000

# Frontend URL (para callbacks de Stripe)
VITE_FRONTEND_URL=http://localhost:5173

# Stripe Public Key (NO es secreto, puede ir en frontend)
VITE_STRIPE_PUBLIC_KEY=pk_test_...
```

**Uso en el código:**

```javascript
const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL || 'http://localhost:5173';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
```

---

## ⚙️ Configuración del Backend

**IMPORTANTE:** Verifica que el backend tenga configuradas las URLs de éxito/cancelación correctas.

En el archivo `backend_2ex/ecommerce_api/settings.py`:

```python
# URLs del Frontend
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')

# En views.py, las URLs de Stripe usan estas rutas:
success_url = f'{FRONTEND_URL}/payment-success?session_id={{CHECKOUT_SESSION_ID}}'
cancel_url = f'{FRONTEND_URL}/payment-cancelled'
```

---

## 🧪 TESTING: Flujo Completo

### Paso a Paso para Probar:

1. **Inicia el backend:**
   ```bash
   cd backend_2ex
   python manage.py runserver
   ```

2. **Inicia el frontend:**
   ```bash
   cd frontend  # Tu carpeta de frontend
   npm run dev  # o yarn dev
   ```

3. **Prueba el flujo NLP:**
   - Ve al componente de búsqueda por voz
   - Di o escribe: "agrega 2 laptops"
   - **RESULTADO ESPERADO:**
     - ✅ Mensaje: "Se encontraron 2 producto(s) para agregar al carrito"
     - ✅ Productos agregados al carrito (visible en localStorage)
     - ✅ NO se crea ninguna orden aún

4. **Revisa el carrito:**
   - Ve a `/cart`
   - Verifica que los 2 laptops estén en el carrito
   - Puedes agregar más productos o modificar cantidades

5. **Procede al checkout:**
   - Click en "Proceder al Pago"
   - Ve a `/checkout`
   - Revisa el resumen de la orden
   - Click en "💳 Proceder al Pago"
   - **AHORA** se crea la orden con estado PENDING
   - Redirección a Stripe Checkout

6. **En Stripe Checkout:**
   - Usa tarjeta de prueba: `4242 4242 4242 4242`
   - Fecha: Cualquier fecha futura
   - CVC: Cualquier 3 dígitos
   - Click en "Pay"

7. **Después del pago:**
   - ✅ Redirección a `/payment-success`
   - ✅ Muestra "¡Pago Exitoso!"
   - ✅ Orden muestra estado "PAID"
   - ✅ Stock del producto reducido (verificar en admin)
   - ✅ Carrito se limpia automáticamente

8. **Si cancelas el pago:**
   - ✅ Redirección a `/payment-cancelled`
   - ✅ Muestra "Pago Cancelado"
   - ✅ Orden sigue en estado "PENDING"
   - ✅ Stock del producto NO reducido
   - ✅ Puedes intentar pagar de nuevo

---

## 🐛 Problemas Comunes y Soluciones

### Problema 1: "payment_url is undefined"

**Causa:** El backend no está devolviendo `payment_url` en la respuesta.

**Solución:**
- Verifica que el backend tenga las últimas correcciones
- Verifica que Stripe esté configurado con las API keys correctas
- Revisa los logs del backend para ver errores de Stripe

### Problema 2: Redirección a Stripe falla

**Causa:** La URL de Stripe es inválida o está vacía.

**Solución:**
```javascript
if (data.payment_url && data.payment_url.startsWith('https://')) {
  window.location.href = data.payment_url;
} else {
  console.error('Invalid payment URL:', data.payment_url);
  alert('Error: URL de pago inválida');
}
```

### Problema 3: Después del pago, no muestra la orden

**Causa:** El `order_id` no se guardó en localStorage o se perdió.

**Solución:**
```javascript
// Al crear la orden, guardar SIEMPRE:
localStorage.setItem('pending_order_id', order.id);

// En PaymentSuccess, verificar:
const orderId = localStorage.getItem('pending_order_id');
if (!orderId) {
  console.error('Order ID not found in localStorage');
  // Intentar obtener desde URL o Stripe session
}
```

### Problema 4: El stock se sigue reduciendo inmediatamente

**Causa:** Estás usando una versión vieja del backend.

**Solución:**
- Haz `git pull` en el repositorio del backend
- Verifica que `shop_orders/views.py` tenga los cambios recientes
- Busca que NO haya `product.stock -= quantity` en `CartNaturalLanguageView.post()`

---

## 📚 Resumen de Archivos a Modificar/Crear

### ✅ Archivos a MODIFICAR:

1. ✏️ `src/components/VoiceCart.jsx` - Agregar productos al carrito en lugar de crear orden
2. ✏️ `src/components/Checkout.jsx` - Crear orden desde carrito + pagar
3. ✏️ `src/components/OrderList.jsx` - Mostrar botón de pago para PENDING
4. ✏️ `src/App.jsx` o `src/router.jsx` - Agregar rutas de pago
5. ✏️ `.env` - Verificar variables de entorno

### ✅ Archivos a CREAR:

1. ➕ `src/hooks/useCart.js` - **Hook del carrito (ESENCIAL)**
2. ➕ `src/components/Cart.jsx` - Página del carrito
3. ➕ `src/pages/PaymentSuccess.jsx` - Página de éxito del pago
4. ➕ `src/pages/PaymentCancelled.jsx` - Página de cancelación
5. ➕ `src/styles/cart.css` - Estilos para el carrito
6. ➕ `src/styles/orders.css` - Estilos para estados de orden

---

## 🎯 Checklist de Implementación

Marca cada item cuando lo completes:

### Fase 1: Carrito (ESENCIAL)
- [ ] Creado `useCart.js` hook con funciones de carrito
- [ ] Actualizado `VoiceCart.jsx` para agregar al carrito
- [ ] Creado `Cart.jsx` para visualizar/editar carrito
- [ ] Agregada ruta `/cart` en el router
- [ ] Testeado: NLP agrega productos al carrito correctamente

### Fase 2: Checkout y Pago
- [ ] Actualizado `Checkout.jsx` para crear orden desde carrito
- [ ] Creado `PaymentSuccess.jsx`
- [ ] Creado `PaymentCancelled.jsx`
- [ ] Actualizado `OrderList.jsx` con botones de pago
- [ ] Agregadas rutas `/checkout`, `/payment-success`, `/payment-cancelled`

### Fase 3: Configuración
- [ ] Configuradas variables de entorno en `.env`
- [ ] Agregados estilos CSS para carrito
- [ ] Agregados estilos CSS para estados de orden

### Fase 4: Testing Completo
- [ ] Testeado: Agregar productos por voz al carrito
- [ ] Testeado: Modificar cantidades en el carrito
- [ ] Testeado: Checkout crea orden PENDING
- [ ] Testeado: Pago en Stripe cambia orden a PAID
- [ ] Testeado: Stock NO se reduce al agregar al carrito
- [ ] Testeado: Stock NO se reduce al crear orden PENDING
- [ ] Testeado: Stock SÍ se reduce después del pago confirmado
- [ ] Testeado: Carrito persiste en localStorage
- [ ] Testeado: Carrito se limpia después del pago exitoso

---

## 🚀 Siguiente Paso

Después de implementar estos cambios:

1. **Reinicia ambos servidores** (backend y frontend)
2. **Prueba el flujo completo:**
   - Agregar productos por voz/texto al carrito
   - Ver carrito y modificar cantidades
   - Hacer checkout (crea orden PENDING)
   - Pagar con Stripe (cambia a PAID y reduce stock)
3. **Verifica en el admin de Django:**
   - NO existen órdenes al agregar al carrito
   - Las órdenes se crean con estado `PENDING` en checkout
   - Después del pago, cambian a `PAID`
   - El stock se reduce solo después del pago

---

## 🔄 Flujo Visual Completo

```
┌─────────────────────────────────────────────────────────────┐
│                    NUEVO FLUJO v2.2                         │
└─────────────────────────────────────────────────────────────┘

1. 🎤 Usuario: "agrega 2 laptops"
   │
   ├─> Backend: Valida stock, devuelve productos
   │
   └─> Frontend: Agrega al carrito (localStorage)
       ✅ NO crea orden
       ✅ NO reduce stock

2. 👤 Usuario: Sigue comprando...
   │
   └─> Agrega más productos con voz o manualmente

3. 🛒 Usuario: Ve al carrito (/cart)
   │
   ├─> Modifica cantidades
   ├─> Elimina productos
   └─> Click en "Proceder al Pago"

4. 💳 Usuario: Checkout (/checkout)
   │
   ├─> Frontend: Crea orden desde carrito
   ├─> Backend: Orden creada con estado PENDING
   │   ✅ NO reduce stock aún
   │
   ├─> Frontend: Crea sesión de Stripe
   └─> Redirige a Stripe Checkout

5. 💰 Usuario: Paga en Stripe
   │
   ├─> Stripe: Procesa el pago
   └─> Webhook: Notifica al backend

6. ✅ Backend: Webhook recibido
   │
   ├─> Valida stock disponible
   ├─> Reduce stock de productos
   └─> Cambia orden a PAID

7. 🎉 Usuario: Redirección a /payment-success
   │
   ├─> Muestra orden pagada
   └─> Carrito limpio

┌─────────────────────────────────────────────────────────────┐
│  VENTAJAS DE ESTE FLUJO:                                    │
├─────────────────────────────────────────────────────────────┤
│  ✅ Usuario puede agregar múltiples productos               │
│  ✅ Carrito persiste en navegador                           │
│  ✅ NO se crean órdenes innecesarias                        │
│  ✅ Stock solo se afecta con pagos confirmados             │
│  ✅ Experiencia de compra más natural                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 💡 Mejoras Opcionales Futuras

1. **Loader durante redirección:**
   ```jsx
   <div className="payment-redirect-loader">
     <div className="spinner"></div>
     <p>Redirigiendo al pago seguro...</p>
   </div>
   ```

2. **Notificaciones con toast:**
   ```jsx
   import { toast } from 'react-toastify';
   
   toast.success('¡Orden creada! Redirigiendo al pago...');
   ```

3. **Webhook confirmation en frontend:**
   - Agregar polling para verificar si la orden cambió a PAID
   - Mostrar notificación en tiempo real cuando el pago se confirma

4. **Historial de intentos de pago:**
   - Guardar en localStorage intentos fallidos
   - Mostrar botón "Reintentar pago" en órdenes pendientes

---

**Última actualización:** Octubre 26, 2025  
**Versión del Backend:** v2.2 (carrito + flujo de pago seguro)  
**Cambio Principal:** NLP ahora agrega al carrito en lugar de crear orden inmediata
