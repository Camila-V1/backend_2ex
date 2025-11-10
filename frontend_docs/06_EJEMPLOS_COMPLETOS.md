# 🎯 06. EJEMPLOS COMPLETOS DE INTEGRACIÓN

## 📝 Descripción

Esta sección contiene **ejemplos completos** de código React/JavaScript que puedes copiar y adaptar directamente en tu frontend.

---

## 🔐 1. SISTEMA DE AUTENTICACIÓN COMPLETO

### AuthContext.jsx (Context Global)

```jsx
import { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tokens, setTokens] = useState({
    access: localStorage.getItem('access_token'),
    refresh: localStorage.getItem('refresh_token')
  });

  useEffect(() => {
    if (tokens.access) {
      loadUserProfile();
    } else {
      setLoading(false);
    }
  }, [tokens.access]);

  const login = async (username, password) => {
    try {
      const response = await fetch('http://localhost:8000/api/users/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (!response.ok) throw new Error('Login failed');

      const data = await response.json();
      
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      
      setTokens({ access: data.access, refresh: data.refresh });
      setUser(data.user);
      
      return { success: true, user: data.user };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setTokens({ access: null, refresh: null });
    setUser(null);
  };

  const loadUserProfile = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/users/profile/', {
        headers: { 'Authorization': `Bearer ${tokens.access}` }
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data);
      } else {
        logout();
      }
    } catch (error) {
      console.error('Error loading profile:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const refreshAccessToken = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/users/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: tokens.refresh })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access);
        setTokens(prev => ({ ...prev, access: data.access }));
        return data.access;
      } else {
        logout();
        return null;
      }
    } catch (error) {
      console.error('Error refreshing token:', error);
      logout();
      return null;
    }
  };

  const value = {
    user,
    tokens,
    login,
    logout,
    refreshAccessToken,
    loading,
    isAuthenticated: !!user,
    isCliente: user?.role === 'CLIENTE',
    isManager: user?.role === 'MANAGER',
    isAdmin: user?.role === 'ADMIN'
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
```

### LoginPage.jsx

```jsx
import { useState } from 'react';
import { useAuth } from './AuthContext';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(username, password);

    if (result.success) {
      // Redirigir según el rol
      if (result.user.role === 'CLIENTE') {
        navigate('/dashboard');
      } else if (result.user.role === 'MANAGER') {
        navigate('/manager/returns');
      } else {
        navigate('/admin');
      }
    } else {
      setError('Usuario o contraseña incorrectos');
    }

    setLoading(false);
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>🔐 Iniciar Sesión</h1>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Usuario:</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="juan_cliente"
              required
            />
          </div>

          <div className="form-group">
            <label>Contraseña:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="password123"
              required
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={loading}>
            {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
          </button>
        </form>

        <div className="test-users">
          <h4>Usuarios de prueba:</h4>
          <ul>
            <li>Cliente: juan_cliente / password123</li>
            <li>Manager: carlos_manager / manager123</li>
            <li>Admin: admin / admin123</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
```

---

## 🛒 2. FLUJO COMPLETO: DEL PRODUCTO A LA DEVOLUCIÓN

### ProductToPurchasePage.jsx

```jsx
import { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const ProductToPurchasePage = () => {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const { tokens } = useAuth();

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    const response = await fetch('http://localhost:8000/api/products/');
    const data = await response.json();
    setProducts(data.results);
  };

  const createOrder = async () => {
    const response = await fetch('http://localhost:8000/api/orders/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${tokens.access}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        items: [{
          product: selectedProduct.id,
          quantity: quantity,
          price: selectedProduct.price
        }],
        payment_method: 'CREDIT_CARD'
      })
    });

    const order = await response.json();
    
    if (response.ok) {
      alert(`✅ Orden #${order.id} creada exitosamente!`);
      return order;
    } else {
      alert('❌ Error al crear orden');
      return null;
    }
  };

  return (
    <div className="product-to-purchase">
      <h2>🛍️ Comprar Producto</h2>
      
      <div className="products-grid">
        {products.map(product => (
          <div
            key={product.id}
            className={`product-card ${selectedProduct?.id === product.id ? 'selected' : ''}`}
            onClick={() => setSelectedProduct(product)}
          >
            <h3>{product.name}</h3>
            <p className="price">${product.price}</p>
            <p className="stock">Stock: {product.stock}</p>
          </div>
        ))}
      </div>

      {selectedProduct && (
        <div className="purchase-section">
          <h3>Producto seleccionado: {selectedProduct.name}</h3>
          
          <div className="quantity-selector">
            <label>Cantidad:</label>
            <input
              type="number"
              min="1"
              max={selectedProduct.stock}
              value={quantity}
              onChange={(e) => setQuantity(parseInt(e.target.value))}
            />
          </div>

          <div className="total">
            <strong>Total: ${(selectedProduct.price * quantity).toFixed(2)}</strong>
          </div>

          <button onClick={createOrder} className="btn-purchase">
            💳 Comprar Ahora
          </button>
        </div>
      )}
    </div>
  );
};

export default ProductToPurchasePage;
```

---

## ↩️ 3. FLUJO COMPLETO DE DEVOLUCIÓN

### ReturnFlowPage.jsx (Vista del Cliente)

```jsx
import { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const ReturnFlowPage = () => {
  const [orders, setOrders] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [reason, setReason] = useState('');
  const [refundMethod, setRefundMethod] = useState('WALLET');
  const { tokens } = useAuth();

  useEffect(() => {
    loadMyOrders();
  }, []);

  const loadMyOrders = async () => {
    const response = await fetch('http://localhost:8000/api/orders/my_orders/', {
      headers: { 'Authorization': `Bearer ${tokens.access}` }
    });
    const data = await response.json();
    
    // Filtrar solo órdenes entregadas
    const deliveredOrders = data.results.filter(order => order.status === 'DELIVERED');
    setOrders(deliveredOrders);
  };

  const canRequestReturn = (order) => {
    if (order.status !== 'DELIVERED') return false;
    
    const deliveryDate = new Date(order.updated_at);
    const now = new Date();
    const daysSinceDelivery = (now - deliveryDate) / (1000 * 60 * 60 * 24);
    
    return daysSinceDelivery <= 30;
  };

  const requestReturn = async () => {
    if (!selectedOrder || !reason) {
      alert('Selecciona una orden y escribe la razón');
      return;
    }

    const response = await fetch('http://localhost:8000/api/deliveries/returns/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${tokens.access}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        order: selectedOrder.id,
        product: selectedOrder.items[0].product.id, // Primer producto
        reason: reason,
        refund_method: refundMethod
      })
    });

    if (response.ok) {
      const returnData = await response.json();
      alert(`✅ Devolución #${returnData.id} creada exitosamente!`);
      alert('📧 Se notificó a 6 managers por email');
      
      // Limpiar formulario
      setSelectedOrder(null);
      setReason('');
    } else {
      const error = await response.json();
      alert(`❌ Error: ${JSON.stringify(error)}`);
    }
  };

  return (
    <div className="return-flow-page">
      <h1>↩️ Solicitar Devolución</h1>

      <div className="step step-1">
        <h2>Paso 1: Selecciona tu orden</h2>
        <div className="orders-list">
          {orders.map(order => (
            <div
              key={order.id}
              className={`order-card ${selectedOrder?.id === order.id ? 'selected' : ''}`}
              onClick={() => setSelectedOrder(order)}
            >
              <div className="order-header">
                <span className="order-id">Orden #{order.id}</span>
                <span className="order-date">
                  {new Date(order.created_at).toLocaleDateString()}
                </span>
              </div>
              
              <div className="order-items">
                {order.items.map(item => (
                  <div key={item.id} className="item">
                    <span>{item.product.name}</span>
                    <span>${item.price}</span>
                  </div>
                ))}
              </div>
              
              <div className="order-total">
                Total: ${order.total}
              </div>

              {canRequestReturn(order) ? (
                <span className="badge-success">✅ Puede devolverse</span>
              ) : (
                <span className="badge-error">❌ Fuera de plazo</span>
              )}
            </div>
          ))}
        </div>
      </div>

      {selectedOrder && (
        <>
          <div className="step step-2">
            <h2>Paso 2: Razón de la devolución</h2>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Explica por qué deseas devolver este producto..."
              rows="4"
            />
          </div>

          <div className="step step-3">
            <h2>Paso 3: Método de reembolso</h2>
            <div className="refund-methods">
              <label className={refundMethod === 'WALLET' ? 'selected' : ''}>
                <input
                  type="radio"
                  value="WALLET"
                  checked={refundMethod === 'WALLET'}
                  onChange={(e) => setRefundMethod(e.target.value)}
                />
                💰 Billetera Virtual (Recomendado)
              </label>

              <label className={refundMethod === 'ORIGINAL_PAYMENT' ? 'selected' : ''}>
                <input
                  type="radio"
                  value="ORIGINAL_PAYMENT"
                  checked={refundMethod === 'ORIGINAL_PAYMENT'}
                  onChange={(e) => setRefundMethod(e.target.value)}
                />
                💳 Método de pago original
              </label>
            </div>
          </div>

          <button onClick={requestReturn} className="btn-submit">
            📤 Enviar Solicitud de Devolución
          </button>
        </>
      )}
    </div>
  );
};

export default ReturnFlowPage;
```

---

## 👔 4. PANEL DEL MANAGER

### ManagerReturnsPanel.jsx

```jsx
import { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const ManagerReturnsPanel = () => {
  const [returns, setReturns] = useState([]);
  const [filter, setFilter] = useState('ALL');
  const { tokens } = useAuth();

  useEffect(() => {
    loadReturns();
  }, [filter]);

  const loadReturns = async () => {
    let url = 'http://localhost:8000/api/deliveries/returns/';
    if (filter !== 'ALL') {
      url += `?status=${filter}`;
    }

    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${tokens.access}` }
    });
    const data = await response.json();
    setReturns(data.results);
  };

  const sendToEvaluation = async (returnId) => {
    const response = await fetch(
      `http://localhost:8000/api/deliveries/returns/${returnId}/send_to_evaluation/`,
      {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${tokens.access}` }
      }
    );

    if (response.ok) {
      alert('✅ Enviado a evaluación');
      loadReturns();
    }
  };

  const approveReturn = async (returnId) => {
    const response = await fetch(
      `http://localhost:8000/api/deliveries/returns/${returnId}/approve/`,
      {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${tokens.access}` }
      }
    );

    if (response.ok) {
      const data = await response.json();
      alert(`✅ Devolución aprobada! Reembolso: $${data.refund_amount}`);
      loadReturns();
    }
  };

  const rejectReturn = async (returnId) => {
    const reason = prompt('Razón del rechazo:');
    if (!reason) return;

    const response = await fetch(
      `http://localhost:8000/api/deliveries/returns/${returnId}/reject/`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${tokens.access}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ rejection_reason: reason })
      }
    );

    if (response.ok) {
      alert('❌ Devolución rechazada');
      loadReturns();
    }
  };

  return (
    <div className="manager-panel">
      <h1>👔 Panel de Devoluciones</h1>

      <div className="filters">
        <button
          className={filter === 'ALL' ? 'active' : ''}
          onClick={() => setFilter('ALL')}
        >
          Todas ({returns.length})
        </button>
        <button
          className={filter === 'REQUESTED' ? 'active' : ''}
          onClick={() => setFilter('REQUESTED')}
        >
          Solicitadas
        </button>
        <button
          className={filter === 'IN_EVALUATION' ? 'active' : ''}
          onClick={() => setFilter('IN_EVALUATION')}
        >
          En Evaluación
        </button>
        <button
          className={filter === 'APPROVED' ? 'active' : ''}
          onClick={() => setFilter('APPROVED')}
        >
          Aprobadas
        </button>
        <button
          className={filter === 'REJECTED' ? 'active' : ''}
          onClick={() => setFilter('REJECTED')}
        >
          Rechazadas
        </button>
      </div>

      <div className="returns-list">
        {returns.map(ret => (
          <div key={ret.id} className={`return-card status-${ret.status.toLowerCase()}`}>
            <div className="return-header">
              <h3>Devolución #{ret.id}</h3>
              <span className={`status-badge status-${ret.status.toLowerCase()}`}>
                {ret.status_display}
              </span>
            </div>

            <div className="return-details">
              <p><strong>Cliente:</strong> {ret.customer_details?.name}</p>
              <p><strong>Producto:</strong> {ret.product_details?.name}</p>
              <p><strong>Precio:</strong> ${ret.product_details?.price}</p>
              <p><strong>Orden:</strong> #{ret.order_details?.id}</p>
              <p><strong>Razón:</strong> {ret.reason}</p>
              <p><strong>Método:</strong> {ret.refund_method_display}</p>
              <p><strong>Fecha:</strong> {new Date(ret.created_at).toLocaleString()}</p>
            </div>

            <div className="return-actions">
              {ret.status === 'REQUESTED' && (
                <button
                  onClick={() => sendToEvaluation(ret.id)}
                  className="btn-evaluation"
                >
                  📦 Enviar a Evaluación
                </button>
              )}

              {ret.status === 'IN_EVALUATION' && (
                <>
                  <button
                    onClick={() => approveReturn(ret.id)}
                    className="btn-approve"
                  >
                    ✅ Aprobar
                  </button>
                  <button
                    onClick={() => rejectReturn(ret.id)}
                    className="btn-reject"
                  >
                    ❌ Rechazar
                  </button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ManagerReturnsPanel;
```

---

## 💰 5. BILLETERA COMPLETA

### WalletPage.jsx

```jsx
import { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const WalletPage = () => {
  const [wallet, setWallet] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [stats, setStats] = useState(null);
  const { tokens } = useAuth();

  useEffect(() => {
    loadWalletData();
  }, []);

  const loadWalletData = async () => {
    try {
      // Balance
      const balanceRes = await fetch(
        'http://localhost:8000/api/users/wallets/my_balance/',
        { headers: { 'Authorization': `Bearer ${tokens.access}` } }
      );
      
      if (balanceRes.ok) {
        setWallet(await balanceRes.json());
      }

      // Transacciones
      const txRes = await fetch(
        'http://localhost:8000/api/users/wallet-transactions/my_transactions/',
        { headers: { 'Authorization': `Bearer ${tokens.access}` } }
      );
      const txData = await txRes.json();
      setTransactions(txData.results);

      // Estadísticas
      const statsRes = await fetch(
        'http://localhost:8000/api/users/wallet-transactions/statistics/',
        { headers: { 'Authorization': `Bearer ${tokens.access}` } }
      );
      setStats(await statsRes.json());
    } catch (error) {
      console.error('Error loading wallet:', error);
    }
  };

  if (!wallet) {
    return (
      <div className="no-wallet">
        <h2>💰 Billetera Virtual</h2>
        <p>Aún no tienes una billetera.</p>
        <p>Se creará automáticamente cuando aprueban tu primera devolución.</p>
      </div>
    );
  }

  return (
    <div className="wallet-page">
      <div className="wallet-header">
        <h1>💰 Mi Billetera</h1>
        <div className="balance-card">
          <span className="label">Saldo Disponible</span>
          <span className="amount">${wallet.balance}</span>
        </div>
      </div>

      {stats && (
        <div className="wallet-stats">
          <div className="stat-card">
            <h3>Total Recibido</h3>
            <p className="value green">${stats.total_credits}</p>
          </div>
          <div className="stat-card">
            <h3>Total Gastado</h3>
            <p className="value red">${stats.total_debits}</p>
          </div>
          <div className="stat-card">
            <h3>Transacciones</h3>
            <p className="value">{stats.transaction_count}</p>
          </div>
        </div>
      )}

      <div className="transactions-section">
        <h2>📋 Historial de Transacciones</h2>
        
        {transactions.length === 0 ? (
          <p className="no-transactions">No hay transacciones</p>
        ) : (
          <div className="transactions-list">
            {transactions.map(tx => (
              <div key={tx.id} className={`transaction-card ${tx.is_credit ? 'credit' : 'debit'}`}>
                <div className="tx-icon">
                  {tx.transaction_type === 'REFUND' ? '💰' : '💳'}
                </div>
                
                <div className="tx-info">
                  <h4>{tx.transaction_type_display}</h4>
                  <p>{tx.description}</p>
                  <small>{new Date(tx.created_at).toLocaleString()}</small>
                </div>
                
                <div className="tx-amount">
                  <span className={tx.is_credit ? 'credit' : 'debit'}>
                    {tx.is_credit ? '+' : '-'}${tx.amount}
                  </span>
                  <small>Saldo: ${tx.balance_after}</small>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default WalletPage;
```

---

## 🔄 6. APP COMPLETA CON ROUTING

### App.jsx

```jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import LoginPage from './LoginPage';
import ProductToPurchasePage from './ProductToPurchasePage';
import ReturnFlowPage from './ReturnFlowPage';
import ManagerReturnsPanel from './ManagerReturnsPanel';
import WalletPage from './WalletPage';
import Navbar from './Navbar';

const PrivateRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) return <div>Cargando...</div>;
  if (!user) return <Navigate to="/login" />;
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" />;
  }

  return children;
};

const App = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Navbar />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          
          <Route
            path="/products"
            element={
              <PrivateRoute allowedRoles={['CLIENTE']}>
                <ProductToPurchasePage />
              </PrivateRoute>
            }
          />
          
          <Route
            path="/returns/new"
            element={
              <PrivateRoute allowedRoles={['CLIENTE']}>
                <ReturnFlowPage />
              </PrivateRoute>
            }
          />
          
          <Route
            path="/wallet"
            element={
              <PrivateRoute allowedRoles={['CLIENTE']}>
                <WalletPage />
              </PrivateRoute>
            }
          />
          
          <Route
            path="/manager/returns"
            element={
              <PrivateRoute allowedRoles={['MANAGER', 'ADMIN']}>
                <ManagerReturnsPanel />
              </PrivateRoute>
            }
          />
          
          <Route path="/" element={<Navigate to="/products" />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
```

---

**Siguiente:** Ver `07_FLUJO_USUARIO.md` para diagramas visuales del flujo
