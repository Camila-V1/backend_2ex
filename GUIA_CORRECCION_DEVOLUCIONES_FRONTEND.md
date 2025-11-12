# 🔧 GUÍA DE CORRECCIONES: Sistema de Devoluciones en Frontend

## 📋 **PROBLEMA DETECTADO**

El frontend **NO tiene el botón "Solicitar Devolución"** en las órdenes con estado `DELIVERED`.

---

## ✅ **CHECKLIST DE VERIFICACIÓN**

### **1. Verificar página de Órdenes (`/orders`)**

**Archivo:** `src/pages/Orders.jsx` o `src/pages/MyOrders.jsx`

**¿Qué revisar?**
- [ ] ¿Muestra las órdenes del usuario?
- [ ] ¿Muestra el estado de cada orden?
- [ ] ¿Tiene botón "Solicitar Devolución" para órdenes DELIVERED?
- [ ] ¿El botón solo aparece si `status === 'DELIVERED'`?

---

### **2. Verificar página de Devoluciones (`/returns`)**

**Archivo:** `src/pages/Returns.jsx` o `src/pages/MyReturns.jsx`

**¿Qué revisar?**
- [ ] ¿Existe la página?
- [ ] ¿Carga las devoluciones desde `/api/deliveries/returns/`?
- [ ] ¿Muestra el listado de devoluciones?
- [ ] ¿Muestra el estado de cada devolución?

---

### **3. Verificar navegación**

**Archivo:** `src/App.jsx` o `src/routes/index.jsx`

**¿Qué revisar?**
- [ ] ¿Existe la ruta `/returns`?
- [ ] ¿Existe la ruta `/orders/:id/return` para crear devolución?
- [ ] ¿El menú tiene enlace a "Devoluciones"?

---

## 🛠️ **CORRECCIONES NECESARIAS**

### **CORRECCIÓN 1: Agregar botón "Solicitar Devolución" en Órdenes**

**Ubicación:** `src/pages/Orders.jsx` o `src/pages/MyOrders.jsx`

**Código actual (probablemente):**
```jsx
// Sin botón de devolución
<div className="order-card">
  <h3>Orden #{order.id}</h3>
  <p>Estado: {order.status}</p>
  <p>Total: ${order.total_price}</p>
  <button onClick={() => navigate(`/orders/${order.id}`)}>
    Ver detalles
  </button>
</div>
```

**Código CORRECTO:**
```jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function OrderCard({ order }) {
  const navigate = useNavigate();

  // Traducción de estados
  const getStatusText = (status) => {
    const translations = {
      'PENDING': 'Pendiente',
      'PAID': 'Pagado',
      'SHIPPED': 'Enviado',
      'DELIVERED': 'Entregado',
      'CANCELLED': 'Cancelado'
    };
    return translations[status] || status;
  };

  // Color del badge según estado
  const getStatusColor = (status) => {
    const colors = {
      'PENDING': 'bg-yellow-100 text-yellow-800',
      'PAID': 'bg-blue-100 text-blue-800',
      'SHIPPED': 'bg-purple-100 text-purple-800',
      'DELIVERED': 'bg-green-100 text-green-800',
      'CANCELLED': 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-900">
            Orden #{order.id}
          </h3>
          <p className="text-sm text-gray-500">
            {new Date(order.created_at).toLocaleDateString('es-ES')}
          </p>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(order.status)}`}>
          {getStatusText(order.status)}
        </span>
      </div>

      <div className="mb-4">
        <p className="text-2xl font-bold text-gray-900">
          ${order.total_price}
        </p>
        <p className="text-sm text-gray-600">
          {order.items?.length || 0} producto(s)
        </p>
      </div>

      <div className="flex gap-3">
        <button
          onClick={() => navigate(`/orders/${order.id}`)}
          className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition"
        >
          Ver detalles
        </button>

        {/* ✅ BOTÓN DE DEVOLUCIÓN - SOLO PARA DELIVERED */}
        {order.status === 'DELIVERED' && (
          <button
            onClick={() => navigate(`/orders/${order.id}/return`)}
            className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition"
          >
            Solicitar Devolución
          </button>
        )}

        {/* Botón para pagar si está PENDING */}
        {order.status === 'PENDING' && (
          <button
            onClick={() => navigate(`/orders/${order.id}/checkout`)}
            className="flex-1 bg-orange-600 text-white py-2 px-4 rounded-lg hover:bg-orange-700 transition"
          >
            Pagar ahora
          </button>
        )}
      </div>
    </div>
  );
}

export default function MyOrders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await axios.get('/orders/');
      setOrders(response.data);
    } catch (error) {
      console.error('Error cargando órdenes:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Cargando...</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Mis Órdenes</h1>
      
      {orders.length === 0 ? (
        <p className="text-gray-600">No tienes órdenes aún.</p>
      ) : (
        <div className="grid gap-4">
          {orders.map(order => (
            <OrderCard key={order.id} order={order} />
          ))}
        </div>
      )}
    </div>
  );
}
```

---

### **CORRECCIÓN 2: Crear página de Devoluciones**

**Crear archivo:** `src/pages/Returns.jsx`

```jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function Returns() {
  const [returns, setReturns] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchReturns();
  }, []);

  const fetchReturns = async () => {
    try {
      const response = await axios.get('/deliveries/returns/');
      setReturns(response.data);
    } catch (error) {
      console.error('Error cargando devoluciones:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusText = (status) => {
    const translations = {
      'PENDING': 'Pendiente',
      'APPROVED': 'Aprobada',
      'REJECTED': 'Rechazada',
      'COMPLETED': 'Completada'
    };
    return translations[status] || status;
  };

  const getStatusColor = (status) => {
    const colors = {
      'PENDING': 'bg-yellow-100 text-yellow-800',
      'APPROVED': 'bg-blue-100 text-blue-800',
      'REJECTED': 'bg-red-100 text-red-800',
      'COMPLETED': 'bg-green-100 text-green-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando devoluciones...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Mis Devoluciones</h1>
        <button
          onClick={() => navigate('/orders')}
          className="bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition"
        >
          Ver Órdenes
        </button>
      </div>

      {returns.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-gray-600 mb-4">No tienes devoluciones aún.</p>
          <button
            onClick={() => navigate('/orders')}
            className="bg-blue-600 text-white py-2 px-6 rounded-lg hover:bg-blue-700 transition"
          >
            Ver mis órdenes
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {returns.map(returnItem => (
            <div key={returnItem.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">
                    Devolución #{returnItem.id}
                  </h3>
                  <p className="text-sm text-gray-500">
                    Orden #{returnItem.order}
                  </p>
                  <p className="text-sm text-gray-500">
                    {new Date(returnItem.created_at).toLocaleDateString('es-ES')}
                  </p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(returnItem.status)}`}>
                  {getStatusText(returnItem.status)}
                </span>
              </div>

              <div className="mb-4">
                <p className="text-sm font-medium text-gray-700">Razón:</p>
                <p className="text-gray-600">{returnItem.reason}</p>
              </div>

              {returnItem.admin_notes && (
                <div className="mb-4 bg-blue-50 p-3 rounded-lg">
                  <p className="text-sm font-medium text-blue-900">Notas del administrador:</p>
                  <p className="text-blue-700">{returnItem.admin_notes}</p>
                </div>
              )}

              {returnItem.refund_amount && (
                <div className="text-lg font-bold text-green-600">
                  Reembolso: ${returnItem.refund_amount}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

### **CORRECCIÓN 3: Crear formulario de Devolución**

**Crear archivo:** `src/pages/CreateReturn.jsx`

```jsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function CreateReturn() {
  const { id } = useParams(); // order ID
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    reason: '',
    description: ''
  });

  useEffect(() => {
    fetchOrder();
  }, [id]);

  const fetchOrder = async () => {
    try {
      const response = await axios.get(`/orders/${id}/`);
      setOrder(response.data);
      
      // Verificar que la orden esté DELIVERED
      if (response.data.status !== 'DELIVERED') {
        alert('Solo puedes solicitar devolución de órdenes entregadas');
        navigate('/orders');
      }
    } catch (error) {
      console.error('Error cargando orden:', error);
      alert('Error al cargar la orden');
      navigate('/orders');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      await axios.post('/deliveries/returns/', {
        order: id,
        reason: formData.reason,
        description: formData.description
      });

      alert('¡Devolución solicitada exitosamente!');
      navigate('/returns');
    } catch (error) {
      console.error('Error creando devolución:', error);
      alert('Error al solicitar devolución: ' + (error.response?.data?.detail || 'Error desconocido'));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <h1 className="text-3xl font-bold mb-8">Solicitar Devolución</h1>

      {/* Información de la orden */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">Información de la Orden</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Orden #</p>
            <p className="font-bold">{order?.id}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Total</p>
            <p className="font-bold">${order?.total_price}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Fecha</p>
            <p className="font-bold">
              {new Date(order?.created_at).toLocaleDateString('es-ES')}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Productos</p>
            <p className="font-bold">{order?.items?.length || 0}</p>
          </div>
        </div>
      </div>

      {/* Formulario de devolución */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6">
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Razón de la devolución *
          </label>
          <select
            value={formData.reason}
            onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Selecciona una razón</option>
            <option value="DEFECTIVE">Producto defectuoso</option>
            <option value="WRONG_ITEM">Producto incorrecto</option>
            <option value="NOT_AS_DESCRIBED">No como se describe</option>
            <option value="DAMAGED">Producto dañado</option>
            <option value="CHANGED_MIND">Cambié de opinión</option>
            <option value="OTHER">Otro</option>
          </select>
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Descripción detallada *
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            required
            rows="4"
            placeholder="Explica detalladamente el motivo de tu devolución..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-yellow-800">
            <strong>Nota:</strong> Una vez enviada la solicitud, será revisada por nuestro equipo. 
            Recibirás una respuesta en un plazo de 24-48 horas.
          </p>
        </div>

        <div className="flex gap-4">
          <button
            type="button"
            onClick={() => navigate('/orders')}
            className="flex-1 bg-gray-200 text-gray-700 py-3 px-6 rounded-lg hover:bg-gray-300 transition"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {submitting ? 'Enviando...' : 'Solicitar Devolución'}
          </button>
        </div>
      </form>
    </div>
  );
}
```

---

### **CORRECCIÓN 4: Agregar rutas en App.jsx**

**Archivo:** `src/App.jsx`

```jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Orders from './pages/Orders';
import Returns from './pages/Returns';
import CreateReturn from './pages/CreateReturn';

function App() {
  return (
    <Router>
      <Routes>
        {/* ... otras rutas ... */}
        
        {/* ✅ RUTAS DE ÓRDENES Y DEVOLUCIONES */}
        <Route path="/orders" element={<Orders />} />
        <Route path="/orders/:id" element={<OrderDetail />} />
        <Route path="/orders/:id/return" element={<CreateReturn />} />
        <Route path="/returns" element={<Returns />} />
        
        {/* ... otras rutas ... */}
      </Routes>
    </Router>
  );
}
```

---

### **CORRECCIÓN 5: Agregar enlace en el menú de navegación**

**Archivo:** `src/components/Navbar.jsx` o `src/components/Header.jsx`

```jsx
<nav className="flex gap-6">
  <Link to="/" className="hover:text-blue-600">Inicio</Link>
  <Link to="/products" className="hover:text-blue-600">Productos</Link>
  <Link to="/orders" className="hover:text-blue-600">Mis Órdenes</Link>
  {/* ✅ AGREGAR ENLACE A DEVOLUCIONES */}
  <Link to="/returns" className="hover:text-blue-600">Devoluciones</Link>
  <Link to="/cart" className="hover:text-blue-600">Carrito</Link>
</nav>
```

---

## 📊 **RESUMEN DE ARCHIVOS A CREAR/MODIFICAR**

### **Archivos a MODIFICAR:**
1. ✅ `src/pages/Orders.jsx` - Agregar botón "Solicitar Devolución"
2. ✅ `src/App.jsx` - Agregar rutas `/returns` y `/orders/:id/return`
3. ✅ `src/components/Navbar.jsx` - Agregar enlace a Devoluciones

### **Archivos a CREAR:**
1. ✅ `src/pages/Returns.jsx` - Página de listado de devoluciones
2. ✅ `src/pages/CreateReturn.jsx` - Formulario de devolución

---

## 🧪 **PRUEBAS**

Una vez implementadas las correcciones:

1. **Ir a `/orders`**
   - ✅ Deberías ver tus 21 órdenes
   - ✅ Las 5 órdenes DELIVERED (#180-184) deben tener botón "Solicitar Devolución"

2. **Hacer clic en "Solicitar Devolución"**
   - ✅ Te redirige a `/orders/180/return` (por ejemplo)
   - ✅ Muestra formulario con razón y descripción

3. **Completar formulario y enviar**
   - ✅ Crea la devolución en el backend
   - ✅ Redirige a `/returns`

4. **Ir a `/returns`**
   - ✅ Muestra la devolución recién creada
   - ✅ Estado: PENDING
   - ✅ Razón y descripción visibles

---

## 📞 **SIGUIENTE PASO**

1. **Copia los archivos** que te proporcioné arriba
2. **Créalos en tu proyecto** de frontend
3. **Haz commit y push** a GitHub
4. **Vercel desplegará** automáticamente
5. **Prueba** el flujo completo

¿Necesitas ayuda con alguna parte específica de la implementación?
