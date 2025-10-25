# 🚀 Guía de Implementación Frontend - SmartSales365 API

## 📋 Tabla de Contenidos

1. [Configuración Inicial](#configuración-inicial)
2. [Autenticación JWT](#autenticación-jwt)
3. [Gestión de Usuarios](#gestión-de-usuarios)
4. [Productos y Categorías](#productos-y-categorías)
5. [Sistema de Reseñas](#sistema-de-reseñas)
6. [Recomendaciones](#recomendaciones)
7. [Carrito y Órdenes](#carrito-y-órdenes)
8. [Pagos con Stripe](#pagos-con-stripe)
9. [NLP - Carrito con Lenguaje Natural](#nlp---carrito-con-lenguaje-natural)
10. [Panel de Administración](#panel-de-administración)
11. [Reportes](#reportes)
12. [Predicciones ML](#predicciones-ml)
13. [Manejo de Errores](#manejo-de-errores)
14. [Ejemplos Completos](#ejemplos-completos)

---

## 🔧 Configuración Inicial

### 1. Variables de Entorno

Crea un archivo `.env` en tu proyecto frontend:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000

# Stripe (Frontend)
VITE_STRIPE_PUBLIC_KEY=pk_test_...
```

### 2. Axios Instance (Recomendado)

```javascript
// src/api/axios.js
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: import.meta.env.VITE_API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Interceptor para agregar token automáticamente
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si el token expiró, intentar renovar
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const { data } = await axios.post(
          `${import.meta.env.VITE_API_BASE_URL}/token/refresh/`,
          { refresh: refreshToken }
        );

        localStorage.setItem('access_token', data.access);
        originalRequest.headers.Authorization = `Bearer ${data.access}`;

        return api(originalRequest);
      } catch (refreshError) {
        // Si falla el refresh, logout
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

---

## 🔐 Autenticación JWT

### 1. Login (Iniciar Sesión)

**Endpoint:** `POST /api/token/`

```javascript
// src/services/authService.js
import api from '../api/axios';

export const authService = {
  // Login
  async login(username, password) {
    try {
      const response = await api.post('/token/', {
        username,
        password
      });

      const { access, refresh } = response.data;

      // Guardar tokens
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);

      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Error de conexión' };
    }
  },

  // Logout
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  // Verificar si está autenticado
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }
};
```

**Ejemplo de uso en componente React:**

```jsx
// LoginForm.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';

function LoginForm() {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await authService.login(formData.username, formData.password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.detail || 'Usuario o contraseña incorrectos');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Usuario"
        value={formData.username}
        onChange={(e) => setFormData({ ...formData, username: e.target.value })}
        required
      />
      <input
        type="password"
        placeholder="Contraseña"
        value={formData.password}
        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
        required
      />
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
      </button>
    </form>
  );
}
```

### 2. Renovar Token

**Endpoint:** `POST /api/token/refresh/`

```javascript
// Ya implementado en el interceptor de axios
// Se ejecuta automáticamente cuando el token expira

// Uso manual si lo necesitas:
async refreshToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  const { data } = await api.post('/token/refresh/', {
    refresh: refreshToken
  });
  localStorage.setItem('access_token', data.access);
  return data.access;
}
```

### 3. Verificar Token

**Endpoint:** `POST /api/token/verify/`

```javascript
async verifyToken(token) {
  try {
    await api.post('/token/verify/', { token });
    return true;
  } catch (error) {
    return false;
  }
}
```

---

## 👥 Gestión de Usuarios

### 1. Registro de Usuario

**Endpoint:** `POST /api/users/`

```javascript
// src/services/userService.js
import api from '../api/axios';

export const userService = {
  // Registrar nuevo usuario
  async register(userData) {
    try {
      const response = await api.post('/users/', {
        username: userData.username,
        email: userData.email,
        password: userData.password,
        first_name: userData.firstName,
        last_name: userData.lastName
      });

      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Error al registrar usuario' };
    }
  },

  // Obtener perfil del usuario actual
  async getProfile() {
    const response = await api.get('/users/profile/');
    return response.data;
  },

  // Actualizar perfil
  async updateProfile(userId, updates) {
    const response = await api.patch(`/users/${userId}/`, updates);
    return response.data;
  },

  // Listar todos los usuarios (solo admin)
  async listUsers() {
    const response = await api.get('/users/');
    return response.data;
  }
};
```

**Ejemplo de formulario de registro:**

```jsx
// RegisterForm.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { userService } from '../services/userService';
import { authService } from '../services/authService';

function RegisterForm() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: ''
  });
  const [errors, setErrors] = useState({});
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});

    // Validación básica
    if (formData.password !== formData.confirmPassword) {
      setErrors({ confirmPassword: 'Las contraseñas no coinciden' });
      return;
    }

    try {
      await userService.register(formData);
      
      // Auto-login después del registro
      await authService.login(formData.username, formData.password);
      
      navigate('/dashboard');
    } catch (err) {
      setErrors(err);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Usuario"
        value={formData.username}
        onChange={(e) => setFormData({ ...formData, username: e.target.value })}
        required
      />
      {errors.username && <p className="error">{errors.username}</p>}

      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        required
      />
      {errors.email && <p className="error">{errors.email}</p>}

      {/* Más campos... */}

      <button type="submit">Registrarse</button>
    </form>
  );
}
```

---

## 🛍️ Productos y Categorías

### 1. Listar Productos

**Endpoint:** `GET /api/products/`

```javascript
// src/services/productService.js
import api from '../api/axios';

export const productService = {
  // Listar productos con paginación y filtros
  async getProducts(params = {}) {
    const response = await api.get('/products/', {
      params: {
        page: params.page || 1,
        search: params.search || '',
        category: params.category || '',
        ordering: params.ordering || '-id' // -id para descendente
      }
    });
    return response.data;
  },

  // Obtener detalle de un producto
  async getProductById(id) {
    const response = await api.get(`/products/${id}/`);
    return response.data;
  },

  // Crear producto (solo admin)
  async createProduct(productData) {
    const response = await api.post('/products/', productData);
    return response.data;
  },

  // Actualizar producto (solo admin)
  async updateProduct(id, updates) {
    const response = await api.patch(`/products/${id}/`, updates);
    return response.data;
  },

  // Eliminar producto (solo admin)
  async deleteProduct(id) {
    await api.delete(`/products/${id}/`);
  }
};
```

**Componente de lista de productos:**

```jsx
// ProductList.jsx
import { useState, useEffect } from 'react';
import { productService } from '../services/productService';

function ProductList() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    page: 1
  });

  useEffect(() => {
    loadProducts();
  }, [filters]);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const data = await productService.getProducts(filters);
      setProducts(data.results || data);
    } catch (error) {
      console.error('Error al cargar productos:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando productos...</div>;

  return (
    <div className="product-list">
      {/* Filtros */}
      <div className="filters">
        <input
          type="text"
          placeholder="Buscar productos..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
        />
      </div>

      {/* Grid de productos */}
      <div className="product-grid">
        {products.map(product => (
          <div key={product.id} className="product-card">
            <h3>{product.name}</h3>
            <p>{product.description}</p>
            <p className="price">${product.price}</p>
            <p className="stock">Stock: {product.stock}</p>
            {product.average_rating > 0 && (
              <div className="rating">
                ⭐ {product.average_rating} ({product.review_count} reseñas)
              </div>
            )}
            <button onClick={() => addToCart(product)}>
              Agregar al Carrito
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 2. Categorías

```javascript
export const categoryService = {
  // Listar categorías
  async getCategories() {
    const response = await api.get('/products/categories/');
    return response.data;
  },

  // Crear categoría (solo admin)
  async createCategory(categoryData) {
    const response = await api.post('/products/categories/', categoryData);
    return response.data;
  }
};
```

---

## ⭐ Sistema de Reseñas

**Endpoints:** 
- `GET /api/products/{id}/reviews/` - Listar reseñas de un producto
- `POST /api/products/reviews/` - Crear reseña
- `PATCH /api/products/reviews/{id}/` - Actualizar reseña
- `DELETE /api/products/reviews/{id}/` - Eliminar reseña

```javascript
// src/services/reviewService.js
import api from '../api/axios';

export const reviewService = {
  // Obtener reseñas de un producto
  async getProductReviews(productId) {
    const response = await api.get(`/products/${productId}/reviews/`);
    return response.data;
  },

  // Crear reseña
  async createReview(productId, rating, comment) {
    const response = await api.post('/products/reviews/', {
      product: productId,
      rating,
      comment
    });
    return response.data;
  },

  // Actualizar reseña
  async updateReview(reviewId, updates) {
    const response = await api.patch(`/products/reviews/${reviewId}/`, updates);
    return response.data;
  },

  // Eliminar reseña
  async deleteReview(reviewId) {
    await api.delete(`/products/reviews/${reviewId}/`);
  }
};
```

**Componente de reseñas:**

```jsx
// ProductReviews.jsx
import { useState, useEffect } from 'react';
import { reviewService } from '../services/reviewService';

function ProductReviews({ productId, currentUserId }) {
  const [reviews, setReviews] = useState([]);
  const [newReview, setNewReview] = useState({ rating: 5, comment: '' });
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    loadReviews();
  }, [productId]);

  const loadReviews = async () => {
    try {
      const data = await reviewService.getProductReviews(productId);
      setReviews(data);
    } catch (error) {
      console.error('Error al cargar reseñas:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await reviewService.createReview(
        productId,
        newReview.rating,
        newReview.comment
      );
      setNewReview({ rating: 5, comment: '' });
      setShowForm(false);
      loadReviews();
    } catch (error) {
      alert('Error al crear reseña: ' + (error.detail || 'Error desconocido'));
    }
  };

  return (
    <div className="reviews-section">
      <h3>Reseñas</h3>

      {/* Formulario de nueva reseña */}
      {!showForm ? (
        <button onClick={() => setShowForm(true)}>Escribir Reseña</button>
      ) : (
        <form onSubmit={handleSubmit}>
          <div>
            <label>Calificación:</label>
            <select
              value={newReview.rating}
              onChange={(e) => setNewReview({ ...newReview, rating: parseInt(e.target.value) })}
            >
              <option value="5">5 ⭐⭐⭐⭐⭐</option>
              <option value="4">4 ⭐⭐⭐⭐</option>
              <option value="3">3 ⭐⭐⭐</option>
              <option value="2">2 ⭐⭐</option>
              <option value="1">1 ⭐</option>
            </select>
          </div>
          <textarea
            placeholder="Escribe tu opinión..."
            value={newReview.comment}
            onChange={(e) => setNewReview({ ...newReview, comment: e.target.value })}
            required
          />
          <button type="submit">Publicar</button>
          <button type="button" onClick={() => setShowForm(false)}>Cancelar</button>
        </form>
      )}

      {/* Lista de reseñas */}
      <div className="reviews-list">
        {reviews.map(review => (
          <div key={review.id} className="review-card">
            <div className="review-header">
              <strong>{review.user_username}</strong>
              <span>{'⭐'.repeat(review.rating)}</span>
            </div>
            <p>{review.comment}</p>
            <small>{new Date(review.created_at).toLocaleDateString()}</small>
            
            {/* Opciones de edición/eliminación para el autor */}
            {review.user === currentUserId && (
              <div className="review-actions">
                <button onClick={() => handleEdit(review.id)}>Editar</button>
                <button onClick={() => handleDelete(review.id)}>Eliminar</button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 🎯 Recomendaciones

**Endpoint:** `GET /api/products/{id}/recommendations/`

```javascript
// src/services/recommendationService.js
import api from '../api/axios';

export const recommendationService = {
  // Obtener productos recomendados basados en un producto
  async getRecommendations(productId) {
    const response = await api.get(`/products/${productId}/recommendations/`);
    return response.data;
  }
};
```

**Componente de recomendaciones:**

```jsx
// RecommendedProducts.jsx
import { useState, useEffect } from 'react';
import { recommendationService } from '../services/recommendationService';

function RecommendedProducts({ productId }) {
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {
    loadRecommendations();
  }, [productId]);

  const loadRecommendations = async () => {
    try {
      const data = await recommendationService.getRecommendations(productId);
      setRecommendations(data);
    } catch (error) {
      console.error('Error al cargar recomendaciones:', error);
    }
  };

  if (recommendations.length === 0) return null;

  return (
    <div className="recommendations">
      <h3>🎯 También te puede interesar</h3>
      <div className="product-carousel">
        {recommendations.map(product => (
          <div key={product.id} className="recommended-product">
            <h4>{product.name}</h4>
            <p>${product.price}</p>
            <button>Ver Detalles</button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 🛒 Carrito y Órdenes

### 1. Crear Orden

**Endpoint:** `POST /api/orders/create/`

```javascript
// src/services/orderService.js
import api from '../api/axios';

export const orderService = {
  // Crear orden desde el carrito
  async createOrder(items) {
    const response = await api.post('/orders/create/', {
      items: items.map(item => ({
        product_id: item.productId,
        quantity: item.quantity
      }))
    });
    return response.data;
  },

  // Listar mis órdenes
  async getMyOrders() {
    const response = await api.get('/orders/');
    return response.data;
  },

  // Obtener detalle de una orden
  async getOrderById(orderId) {
    const response = await api.get(`/orders/${orderId}/`);
    return response.data;
  }
};
```

**Hook de carrito:**

```javascript
// src/hooks/useCart.js
import { useState, useEffect } from 'react';

export function useCart() {
  const [cart, setCart] = useState([]);

  // Cargar carrito desde localStorage
  useEffect(() => {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      setCart(JSON.parse(savedCart));
    }
  }, []);

  // Guardar carrito en localStorage
  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cart));
  }, [cart]);

  const addToCart = (product, quantity = 1) => {
    setCart(prevCart => {
      const existingItem = prevCart.find(item => item.productId === product.id);
      
      if (existingItem) {
        return prevCart.map(item =>
          item.productId === product.id
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      }

      return [...prevCart, {
        productId: product.id,
        name: product.name,
        price: product.price,
        quantity
      }];
    });
  };

  const removeFromCart = (productId) => {
    setCart(prevCart => prevCart.filter(item => item.productId !== productId));
  };

  const updateQuantity = (productId, quantity) => {
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }

    setCart(prevCart =>
      prevCart.map(item =>
        item.productId === productId ? { ...item, quantity } : item
      )
    );
  };

  const clearCart = () => {
    setCart([]);
  };

  const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  return {
    cart,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    total,
    itemCount: cart.length
  };
}
```

**Componente de checkout:**

```jsx
// Checkout.jsx
import { useNavigate } from 'react-router-dom';
import { useCart } from '../hooks/useCart';
import { orderService } from '../services/orderService';

function Checkout() {
  const { cart, total, clearCart } = useCart();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleCheckout = async () => {
    setLoading(true);

    try {
      const order = await orderService.createOrder(cart);
      
      alert(`¡Orden creada! #${order.id}`);
      clearCart();
      navigate(`/orders/${order.id}`);
    } catch (error) {
      alert('Error al crear la orden: ' + (error.detail || 'Error desconocido'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="checkout">
      <h2>Resumen de Compra</h2>

      <div className="cart-items">
        {cart.map(item => (
          <div key={item.productId} className="cart-item">
            <span>{item.name}</span>
            <span>x{item.quantity}</span>
            <span>${(item.price * item.quantity).toFixed(2)}</span>
          </div>
        ))}
      </div>

      <div className="total">
        <strong>Total: ${total.toFixed(2)}</strong>
      </div>

      <button onClick={handleCheckout} disabled={loading || cart.length === 0}>
        {loading ? 'Procesando...' : 'Confirmar Compra'}
      </button>
    </div>
  );
}
```

---

## 💳 Pagos con Stripe

**Endpoint:** `POST /api/orders/{id}/create-checkout-session/`

```javascript
// src/services/stripeService.js
import api from '../api/axios';

export const stripeService = {
  // Crear sesión de checkout de Stripe
  async createCheckoutSession(orderId) {
    const response = await api.post(`/orders/${orderId}/create-checkout-session/`);
    return response.data.checkout_url;
  }
};
```

**Componente de pago:**

```jsx
// PaymentButton.jsx
import { useState } from 'react';
import { stripeService } from '../services/stripeService';

function PaymentButton({ orderId }) {
  const [loading, setLoading] = useState(false);

  const handlePayment = async () => {
    setLoading(true);

    try {
      const checkoutUrl = await stripeService.createCheckoutSession(orderId);
      
      // Redirigir a Stripe Checkout
      window.location.href = checkoutUrl;
    } catch (error) {
      alert('Error al iniciar el pago: ' + (error.detail || 'Error desconocido'));
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handlePayment}
      disabled={loading}
      className="stripe-button"
    >
      {loading ? 'Procesando...' : '💳 Pagar con Stripe'}
    </button>
  );
}
```

**Páginas de éxito/cancelación:**

```jsx
// PaymentSuccess.jsx
import { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

function PaymentSuccess() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    // Aquí podrías verificar el estado del pago con el backend si lo necesitas
    console.log('Pago exitoso, session:', sessionId);
  }, [sessionId]);

  return (
    <div className="payment-success">
      <h1>✅ ¡Pago Exitoso!</h1>
      <p>Tu pedido ha sido procesado correctamente.</p>
      <button onClick={() => navigate('/orders')}>Ver mis órdenes</button>
    </div>
  );
}

// PaymentCancelled.jsx
function PaymentCancelled() {
  const navigate = useNavigate();

  return (
    <div className="payment-cancelled">
      <h1>❌ Pago Cancelado</h1>
      <p>No se realizó ningún cargo a tu tarjeta.</p>
      <button onClick={() => navigate('/cart')}>Volver al carrito</button>
    </div>
  );
}
```

---

## 🎤 NLP - Carrito con Lenguaje Natural

**Endpoints:**
- `POST /api/orders/cart/add-natural-language/` - Agregar productos con texto
- `GET /api/orders/cart/suggestions/?q=texto` - Sugerencias de productos

```javascript
// src/services/nlpService.js
import api from '../api/axios';

export const nlpService = {
  // Agregar productos usando lenguaje natural
  async addToCartNLP(prompt) {
    const response = await api.post('/orders/cart/add-natural-language/', {
      prompt
    });
    return response.data;
  },

  // Obtener sugerencias de productos
  async getProductSuggestions(query) {
    const response = await api.get('/orders/cart/suggestions/', {
      params: { q: query }
    });
    return response.data;
  }
};
```

**Componente de búsqueda por voz/texto:**

```jsx
// VoiceCart.jsx
import { useState } from 'react';
import { nlpService } from '../services/nlpService';

function VoiceCart() {
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState(null);
  const [listening, setListening] = useState(false);

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

  const handleSubmit = async (text = prompt) => {
    if (!text.trim()) return;

    try {
      const data = await nlpService.addToCartNLP(text);
      setResult(data);

      if (data.success) {
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ ${data.error}`);
      }
    } catch (error) {
      alert('Error: ' + (error.detail || 'Error desconocido'));
    }
  };

  return (
    <div className="voice-cart">
      <h3>🎤 Agregar Productos por Voz o Texto</h3>

      <div className="input-group">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder='Ej: "Agrega 2 smartphones al carrito"'
          onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
        />
        <button onClick={() => handleSubmit()}>
          Enviar
        </button>
        <button
          onClick={startListening}
          disabled={listening}
          className="voice-button"
        >
          {listening ? '🔴 Escuchando...' : '🎤 Hablar'}
        </button>
      </div>

      {result && (
        <div className={`result ${result.success ? 'success' : 'error'}`}>
          <p><strong>Interpretado como:</strong> {result.interpreted_action}</p>
          {result.order && (
            <div>
              <p>Orden #{result.order.id} creada</p>
              <p>Total: ${result.order.total}</p>
            </div>
          )}
        </div>
      )}

      <div className="examples">
        <p><strong>Ejemplos:</strong></p>
        <ul>
          <li>"Agrega 2 smartphones al carrito"</li>
          <li>"Quiero 3 laptops y 1 mouse"</li>
          <li>"Añade el curso de Python"</li>
          <li>"Comprar 5 auriculares bluetooth"</li>
        </ul>
      </div>
    </div>
  );
}
```

---

## 👨‍💼 Panel de Administración

### 1. Dashboard Administrativo

**Endpoint:** `GET /api/orders/admin/dashboard/`

```javascript
// src/services/adminService.js
import api from '../api/axios';

export const adminService = {
  // Obtener dashboard (con caché)
  async getDashboard() {
    const response = await api.get('/orders/admin/dashboard/');
    return response.data;
  },

  // Listar todas las órdenes
  async getAllOrders() {
    const response = await api.get('/orders/admin/');
    return response.data;
  },

  // Actualizar estado de orden
  async updateOrderStatus(orderId, newStatus) {
    const response = await api.patch(`/orders/admin/${orderId}/update_status/`, {
      status: newStatus
    });
    return response.data;
  },

  // Listar usuarios
  async getUsers() {
    const response = await api.get('/orders/admin/users/');
    return response.data;
  },

  // Analytics de ventas
  async getSalesAnalytics() {
    const response = await api.get('/orders/admin/analytics/sales/');
    return response.data;
  }
};
```

**Componente de dashboard:**

```jsx
// AdminDashboard.jsx
import { useState, useEffect } from 'react';
import { adminService } from '../services/adminService';

function AdminDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const data = await adminService.getDashboard();
      setDashboard(data);
    } catch (error) {
      console.error('Error al cargar dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando dashboard...</div>;
  if (!dashboard) return <div>Error al cargar datos</div>;

  return (
    <div className="admin-dashboard">
      <h1>📊 Dashboard Administrativo</h1>

      {/* Estadísticas generales */}
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Órdenes Totales</h3>
          <p className="stat-value">{dashboard.overview.total_orders}</p>
        </div>
        <div className="stat-card">
          <h3>Usuarios</h3>
          <p className="stat-value">{dashboard.overview.total_users}</p>
        </div>
        <div className="stat-card">
          <h3>Productos Activos</h3>
          <p className="stat-value">{dashboard.overview.active_products}</p>
        </div>
        <div className="stat-card">
          <h3>Revenue Total</h3>
          <p className="stat-value">${dashboard.overview.total_revenue.toFixed(2)}</p>
        </div>
      </div>

      {/* Ventas del mes */}
      <div className="sales-section">
        <h2>💰 Ventas del Mes</h2>
        <div className="sales-cards">
          <div className="sales-card">
            <h4>Mes Actual</h4>
            <p>${dashboard.sales.current_month_revenue.toFixed(2)}</p>
          </div>
          <div className="sales-card">
            <h4>Mes Anterior</h4>
            <p>${dashboard.sales.last_month_revenue.toFixed(2)}</p>
          </div>
          <div className={`sales-card ${dashboard.sales.growth_percentage >= 0 ? 'positive' : 'negative'}`}>
            <h4>Crecimiento</h4>
            <p>{dashboard.sales.growth_percentage.toFixed(1)}%</p>
          </div>
        </div>
      </div>

      {/* Órdenes por estado */}
      <div className="orders-by-status">
        <h2>📦 Órdenes por Estado</h2>
        <div className="status-list">
          {dashboard.orders_by_status.map(status => (
            <div key={status.status} className="status-item">
              <span className="status-label">{status.status}</span>
              <span className="status-count">{status.count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Top productos */}
      <div className="top-products">
        <h2>🏆 Productos Más Vendidos</h2>
        <table>
          <thead>
            <tr>
              <th>Producto</th>
              <th>Precio</th>
              <th>Unidades</th>
              <th>Revenue</th>
            </tr>
          </thead>
          <tbody>
            {dashboard.top_products.map(product => (
              <tr key={product.product__id}>
                <td>{product.product__name}</td>
                <td>${product.product__price}</td>
                <td>{product.total_sold}</td>
                <td>${product.total_revenue}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Productos con stock bajo */}
      {dashboard.low_stock_products.length > 0 && (
        <div className="low-stock-alert">
          <h2>⚠️ Stock Bajo</h2>
          <ul>
            {dashboard.low_stock_products.map(product => (
              <li key={product.id}>
                {product.name} - <strong>{product.stock} unidades</strong>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Indicador de caché */}
      {dashboard._from_cache && (
        <div className="cache-indicator">
          ⚡ Datos desde caché (actualización cada 5 min)
        </div>
      )}
    </div>
  );
}
```

### 2. Gestión de Órdenes

```jsx
// OrderManagement.jsx
import { useState, useEffect } from 'react';
import { adminService } from '../services/adminService';

function OrderManagement() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    const data = await adminService.getAllOrders();
    setOrders(data);
  };

  const handleStatusChange = async (orderId, newStatus) => {
    try {
      await adminService.updateOrderStatus(orderId, newStatus);
      alert('Estado actualizado');
      loadOrders();
    } catch (error) {
      alert('Error al actualizar estado');
    }
  };

  return (
    <div className="order-management">
      <h2>Gestión de Órdenes</h2>
      
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Cliente</th>
            <th>Total</th>
            <th>Estado</th>
            <th>Fecha</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {orders.map(order => (
            <tr key={order.id}>
              <td>#{order.id}</td>
              <td>{order.user}</td>
              <td>${order.total_price}</td>
              <td>
                <select
                  value={order.status}
                  onChange={(e) => handleStatusChange(order.id, e.target.value)}
                >
                  <option value="pending">Pendiente</option>
                  <option value="paid">Pagado</option>
                  <option value="shipped">Enviado</option>
                  <option value="delivered">Entregado</option>
                  <option value="cancelled">Cancelado</option>
                </select>
              </td>
              <td>{new Date(order.created_at).toLocaleDateString()}</td>
              <td>
                <button onClick={() => viewDetails(order.id)}>Ver</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

## 📊 Reportes

**Endpoints:**
- `GET /api/reports/sales/?format=pdf&start_date=...&end_date=...`
- `GET /api/reports/products/?format=excel`
- `POST /api/reports/dynamic-parser/` - IA con lenguaje natural
- `GET /api/orders/{id}/invoice/` - Factura de orden

```javascript
// src/services/reportService.js
import api from '../api/axios';

export const reportService = {
  // Generar reporte de ventas
  async generateSalesReport(startDate, endDate, format = 'pdf') {
    const response = await api.get('/reports/sales/', {
      params: {
        start_date: startDate,
        end_date: endDate,
        format
      },
      responseType: 'blob' // Importante para archivos
    });

    // Crear URL del blob y descargar
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `reporte_ventas.${format}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },

  // Generar reporte de productos
  async generateProductsReport(format = 'pdf') {
    const response = await api.get('/reports/products/', {
      params: { format },
      responseType: 'blob'
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `reporte_productos.${format}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },

  // Reporte dinámico con IA
  async generateDynamicReport(prompt) {
    const response = await api.post('/reports/dynamic-parser/', {
      prompt
    }, {
      responseType: 'blob'
    });

    // Detectar extensión del archivo desde headers
    const contentType = response.headers['content-type'];
    const extension = contentType.includes('pdf') ? 'pdf' : 'xlsx';

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `reporte_dinamico.${extension}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },

  // Descargar factura de orden
  async downloadInvoice(orderId) {
    const response = await api.get(`/orders/${orderId}/invoice/`, {
      responseType: 'blob'
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `factura_orden_${orderId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  }
};
```

**Componente de reportes:**

```jsx
// ReportsPage.jsx
import { useState } from 'react';
import { reportService } from '../services/reportService';

function ReportsPage() {
  const [dateRange, setDateRange] = useState({
    start: '',
    end: ''
  });
  const [nlpPrompt, setNlpPrompt] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSalesReport = async (format) => {
    if (!dateRange.start || !dateRange.end) {
      alert('Selecciona un rango de fechas');
      return;
    }

    setLoading(true);
    try {
      await reportService.generateSalesReport(
        dateRange.start,
        dateRange.end,
        format
      );
    } catch (error) {
      alert('Error al generar reporte');
    } finally {
      setLoading(false);
    }
  };

  const handleNLPReport = async () => {
    if (!nlpPrompt.trim()) {
      alert('Escribe una solicitud');
      return;
    }

    setLoading(true);
    try {
      await reportService.generateDynamicReport(nlpPrompt);
    } catch (error) {
      alert('Error al generar reporte: ' + (error.detail || 'Error desconocido'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reports-page">
      <h1>📊 Reportes</h1>

      {/* Reporte de Ventas */}
      <section className="report-section">
        <h2>Reporte de Ventas</h2>
        <div className="date-inputs">
          <input
            type="date"
            value={dateRange.start}
            onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
          />
          <input
            type="date"
            value={dateRange.end}
            onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
          />
        </div>
        <div className="buttons">
          <button onClick={() => handleSalesReport('pdf')} disabled={loading}>
            📄 Descargar PDF
          </button>
          <button onClick={() => handleSalesReport('excel')} disabled={loading}>
            📊 Descargar Excel
          </button>
        </div>
      </section>

      {/* Reporte de Productos */}
      <section className="report-section">
        <h2>Reporte de Productos</h2>
        <div className="buttons">
          <button
            onClick={() => reportService.generateProductsReport('pdf')}
            disabled={loading}
          >
            📄 Descargar PDF
          </button>
          <button
            onClick={() => reportService.generateProductsReport('excel')}
            disabled={loading}
          >
            📊 Descargar Excel
          </button>
        </div>
      </section>

      {/* Reporte Dinámico con IA */}
      <section className="report-section nlp-section">
        <h2>🤖 Reporte Personalizado con IA</h2>
        <textarea
          value={nlpPrompt}
          onChange={(e) => setNlpPrompt(e.target.value)}
          placeholder='Ejemplo: "Reporte de ventas del mes de octubre agrupado por producto en Excel"'
          rows={4}
        />
        <button onClick={handleNLPReport} disabled={loading}>
          Generar Reporte
        </button>

        <div className="examples">
          <p><strong>Ejemplos de solicitudes:</strong></p>
          <ul>
            <li>"Reporte de ventas del mes de octubre en PDF"</li>
            <li>"Dame el reporte de ventas de septiembre en excel"</li>
            <li>"Reporte de ventas agrupado por producto del mes actual"</li>
            <li>"Ventas con nombres de clientes del mes pasado en PDF"</li>
          </ul>
        </div>
      </section>
    </div>
  );
}
```

---

## 🤖 Predicciones ML

**Endpoint:** `GET /api/predictions/sales/`

```javascript
// src/services/predictionService.js
import api from '../api/axios';

export const predictionService = {
  // Obtener predicciones de ventas (30 días)
  async getSalesPredictions() {
    const response = await api.get('/predictions/sales/');
    return response.data;
  }
};
```

**Componente de predicciones:**

```jsx
// SalesPredictions.jsx
import { useState, useEffect } from 'react';
import { predictionService } from '../services/predictionService';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

function SalesPredictions() {
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPredictions();
  }, []);

  const loadPredictions = async () => {
    try {
      const data = await predictionService.getSalesPredictions();
      setPredictions(data);
    } catch (error) {
      console.error('Error al cargar predicciones:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando predicciones...</div>;
  if (!predictions) return <div>Error al cargar predicciones</div>;

  return (
    <div className="predictions-page">
      <h1>🤖 Predicciones de Ventas (ML)</h1>

      <div className="model-info">
        <p><strong>Modelo:</strong> {predictions.model_info.trained ? '✅ Entrenado' : '❌ No entrenado'}</p>
        <p><strong>Período:</strong> {predictions.model_info.prediction_period}</p>
        <p><strong>Desde:</strong> {predictions.model_info.start_date}</p>
        <p><strong>Hasta:</strong> {predictions.model_info.end_date}</p>
      </div>

      {/* Gráfico de predicciones */}
      <div className="chart-container">
        <LineChart width={800} height={400} data={predictions.predictions}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="predicted_sales"
            stroke="#8884d8"
            name="Ventas Predichas"
          />
        </LineChart>
      </div>

      {/* Tabla de predicciones */}
      <table className="predictions-table">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Día</th>
            <th>Ventas Predichas</th>
          </tr>
        </thead>
        <tbody>
          {predictions.predictions.map((pred, index) => (
            <tr key={index}>
              <td>{pred.date}</td>
              <td>{pred.day_of_week}</td>
              <td>{pred.predicted_sales.toFixed(2)} unidades</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

## ⚠️ Manejo de Errores

### Hook de manejo de errores centralizado:

```javascript
// src/hooks/useApiError.js
import { useState } from 'react';

export function useApiError() {
  const [error, setError] = useState(null);

  const handleError = (err) => {
    let errorMessage = 'Error desconocido';

    if (err.response) {
      // Error de respuesta del servidor
      const data = err.response.data;

      if (typeof data === 'string') {
        errorMessage = data;
      } else if (data.detail) {
        errorMessage = data.detail;
      } else if (data.error) {
        errorMessage = data.error;
      } else {
        // Errores de validación por campo
        const fieldErrors = Object.entries(data)
          .map(([field, errors]) => `${field}: ${errors.join(', ')}`)
          .join('\n');
        errorMessage = fieldErrors || JSON.stringify(data);
      }
    } else if (err.request) {
      // Error de red
      errorMessage = 'Error de conexión. Verifica tu internet.';
    } else {
      // Otro error
      errorMessage = err.message || 'Error inesperado';
    }

    setError(errorMessage);
    return errorMessage;
  };

  const clearError = () => setError(null);

  return { error, handleError, clearError };
}
```

**Uso en componentes:**

```jsx
import { useApiError } from '../hooks/useApiError';

function MyComponent() {
  const { error, handleError, clearError } = useApiError();

  const handleAction = async () => {
    clearError();
    try {
      await someApiCall();
    } catch (err) {
      handleError(err);
    }
  };

  return (
    <div>
      {error && (
        <div className="error-alert">
          {error}
          <button onClick={clearError}>×</button>
        </div>
      )}
      {/* resto del componente */}
    </div>
  );
}
```

---

## 📚 Ejemplos Completos

### Ejemplo 1: Flujo Completo de Compra

```jsx
// CompletePurchaseFlow.jsx
import { useState } from 'react';
import { useCart } from '../hooks/useCart';
import { authService } from '../services/authService';
import { orderService } from '../services/orderService';
import { stripeService } from '../services/stripeService';

function CompletePurchaseFlow() {
  const { cart, total, clearCart } = useCart();
  const [step, setStep] = useState(1); // 1: Cart, 2: Login, 3: Confirm, 4: Payment
  const [order, setOrder] = useState(null);

  const handleCheckout = async () => {
    // Paso 1: Verificar autenticación
    if (!authService.isAuthenticated()) {
      setStep(2);
      return;
    }

    // Paso 2: Crear orden
    try {
      const newOrder = await orderService.createOrder(cart);
      setOrder(newOrder);
      setStep(3);
    } catch (error) {
      alert('Error al crear orden: ' + error.detail);
    }
  };

  const handlePayment = async () => {
    try {
      const checkoutUrl = await stripeService.createCheckoutSession(order.id);
      window.location.href = checkoutUrl;
    } catch (error) {
      alert('Error al iniciar pago: ' + error.detail);
    }
  };

  return (
    <div className="purchase-flow">
      {/* Step 1: Carrito */}
      {step === 1 && (
        <div>
          <h2>Tu Carrito</h2>
          {cart.map(item => (
            <div key={item.productId}>
              {item.name} x{item.quantity} - ${item.price * item.quantity}
            </div>
          ))}
          <p>Total: ${total}</p>
          <button onClick={handleCheckout}>Proceder al Pago</button>
        </div>
      )}

      {/* Step 2: Login (si no está autenticado) */}
      {step === 2 && (
        <div>
          <h2>Inicia Sesión para Continuar</h2>
          {/* LoginForm component */}
        </div>
      )}

      {/* Step 3: Confirmación */}
      {step === 3 && order && (
        <div>
          <h2>Confirmar Orden</h2>
          <p>Orden #{order.id}</p>
          <p>Total: ${order.total_price}</p>
          <button onClick={handlePayment}>Pagar con Stripe</button>
        </div>
      )}
    </div>
  );
}
```

### Ejemplo 2: Protected Route (requiere autenticación)

```jsx
// ProtectedRoute.jsx
import { Navigate } from 'react-router-dom';
import { authService } from '../services/authService';

function ProtectedRoute({ children, adminOnly = false }) {
  const isAuthenticated = authService.isAuthenticated();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Si requiere admin, verificar rol (necesitarías almacenar esto en el token o estado)
  if (adminOnly) {
    // Implementar verificación de rol aquí
  }

  return children;
}

// Uso en rutas:
<Route path="/dashboard" element={
  <ProtectedRoute>
    <Dashboard />
  </ProtectedRoute>
} />

<Route path="/admin" element={
  <ProtectedRoute adminOnly>
    <AdminPanel />
  </ProtectedRoute>
} />
```

---

## 🎯 Notas Finales

### Headers Requeridos

Todos los endpoints (excepto login y registro) requieren:
```
Authorization: Bearer <access_token>
```

### Formato de Respuestas

La mayoría de endpoints retornan JSON con estructura:
```json
{
  "id": 123,
  "field": "value",
  ...
}
```

Errores retornan:
```json
{
  "detail": "Mensaje de error"
}
```

O errores de validación:
```json
{
  "field_name": ["Error en este campo"],
  "another_field": ["Otro error"]
}
```

### Paginación

Los endpoints de listado retornan:
```json
{
  "count": 100,
  "next": "http://api.com/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

### CORS

El backend está configurado para aceptar requests desde:
- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)

### Testing

Usa el script `test_api.ps1` del backend para verificar que todos los endpoints funcionen correctamente antes de integrarlos.

---

## 📞 Soporte

**Documentación adicional:**
- API Schema: `API_SCHEMA.md`
- Casos de Uso: `CASOS_DE_USO.md`
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

**Repositorio Backend:**
https://github.com/Camila-V1/backend_2ex

---

*Generado automáticamente para SmartSales365 - Octubre 2025*
