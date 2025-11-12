# 🎯 Menú de Publicidad Personalizada - Guía Implementación Frontend

## 📊 Resumen

El backend ahora cuenta con un **sistema de IA** que genera recomendaciones personalizadas para cada cliente, listo para crear un **menú de publicidad inteligente**.

---

## 🔌 API Endpoint

### **GET** `/api/products/personalized/`

Retorna productos recomendados específicamente para el usuario autenticado.

**Headers requeridos:**
```http
Authorization: Bearer {access_token}
```

**Parámetros opcionales:**
```
?limit=6    # Número de productos a retornar (default: 10)
```

---

## 🤖 Cómo Funciona la IA

El sistema usa **3 estrategias** de recomendación:

### 1️⃣ **Análisis de Historial** (Estrategia Principal)
- Analiza las categorías que más compra el usuario
- Recomienda productos similares que NO ha comprado aún
- Prioriza productos nuevos de sus categorías favoritas

### 2️⃣ **Collaborative Filtering** 
- Encuentra usuarios con gustos similares
- Recomienda productos que ellos compraron
- "Usuarios que compraron X también compraron Y"

### 3️⃣ **Productos Populares** (Fallback)
- Para usuarios nuevos sin historial
- Muestra los productos más vendidos del sitio

---

## 📦 Respuesta del API

```json
{
  "user": "juan_cliente",
  "count": 6,
  "strategy_used": "personalized_ai",
  "favorite_categories": ["Electrónica", "Gaming", "Computadoras"],
  "recommendations": [
    {
      "id": 5,
      "name": "Auriculares SteelSeries Arctis",
      "description": "Auriculares gaming profesionales...",
      "price": "2499.99",
      "stock": 30,
      "category": 2,
      "category_name": "Gaming",
      "image": "/media/products/auriculares.jpg",
      "is_active": true,
      "created_at": "2025-11-10T10:30:00Z",
      "average_rating": 4.5
    },
    // ... más productos
  ]
}
```

---

## 💻 Implementación Frontend

### 1. **Crear componente de Banner Publicitario**

```jsx
// components/PersonalizedBanner.jsx
import { useState, useEffect } from 'react';
import axios from '../api/axios';

const PersonalizedBanner = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        setLoading(false);
        return; // No mostrar banner si no está logueado
      }

      const response = await axios.get('/products/personalized/', {
        headers: {
          Authorization: `Bearer ${token}`
        },
        params: {
          limit: 6 // Mostrar 6 productos en el banner
        }
      });

      setRecommendations(response.data.recommendations);
    } catch (error) {
      console.error('Error al cargar recomendaciones:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="personalized-banner loading">
        <p>Cargando recomendaciones personalizadas...</p>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return null; // No mostrar nada si no hay recomendaciones
  }

  return (
    <div className="personalized-banner">
      <div className="banner-header">
        <h2>🎯 Recomendado para ti</h2>
        <p>Basado en tus compras anteriores</p>
      </div>

      <div className="products-grid">
        {recommendations.map(product => (
          <div key={product.id} className="product-card-mini">
            <img 
              src={product.image || '/placeholder.jpg'} 
              alt={product.name}
            />
            <div className="product-info">
              <h4>{product.name}</h4>
              <p className="category">{product.category_name}</p>
              <p className="price">${product.price}</p>
              <button 
                className="btn-add-cart"
                onClick={() => handleAddToCart(product.id)}
              >
                Agregar al carrito
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PersonalizedBanner;
```

---

### 2. **Estilos CSS**

```css
/* styles/PersonalizedBanner.css */

.personalized-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
  margin: 20px 0;
  border-radius: 15px;
  color: white;
}

.banner-header {
  text-align: center;
  margin-bottom: 30px;
}

.banner-header h2 {
  font-size: 2rem;
  margin-bottom: 10px;
}

.banner-header p {
  opacity: 0.9;
  font-size: 1.1rem;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.product-card-mini {
  background: white;
  color: #333;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.product-card-mini:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.2);
}

.product-card-mini img {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.product-info {
  padding: 15px;
}

.product-info h4 {
  font-size: 1rem;
  margin-bottom: 8px;
  height: 40px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-info .category {
  color: #667eea;
  font-size: 0.85rem;
  margin-bottom: 8px;
}

.product-info .price {
  font-size: 1.3rem;
  font-weight: bold;
  color: #764ba2;
  margin-bottom: 10px;
}

.btn-add-cart {
  width: 100%;
  padding: 10px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.3s;
}

.btn-add-cart:hover {
  background: #764ba2;
}

/* Versión responsive */
@media (max-width: 768px) {
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .banner-header h2 {
    font-size: 1.5rem;
  }
}
```

---

### 3. **Integrar en la página principal**

```jsx
// pages/Home.jsx
import PersonalizedBanner from '../components/PersonalizedBanner';
import ProductList from '../components/ProductList';

const Home = () => {
  return (
    <div className="home-page">
      {/* Banner de bienvenida */}
      <div className="hero-section">
        <h1>Bienvenido a nuestra tienda</h1>
      </div>

      {/* 🎯 BANNER PERSONALIZADO CON IA */}
      <PersonalizedBanner />

      {/* Productos generales */}
      <section className="products-section">
        <h2>Todos los productos</h2>
        <ProductList />
      </section>
    </div>
  );
};

export default Home;
```

---

## 🎨 Variantes de Diseño

### **Opción 1: Carrusel Horizontal**

```jsx
import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';

<Swiper
  spaceBetween={20}
  slidesPerView={4}
  breakpoints={{
    320: { slidesPerView: 1 },
    640: { slidesPerView: 2 },
    1024: { slidesPerView: 4 }
  }}
>
  {recommendations.map(product => (
    <SwiperSlide key={product.id}>
      <ProductCard product={product} />
    </SwiperSlide>
  ))}
</Swiper>
```

### **Opción 2: Grid Simple**
```jsx
<div className="recommendations-grid">
  {recommendations.slice(0, 6).map(product => (
    <ProductCard key={product.id} product={product} />
  ))}
</div>
```

### **Opción 3: Banner Hero Grande**
```jsx
<div className="hero-recommendations">
  <div className="featured-large">
    <ProductCard product={recommendations[0]} size="large" />
  </div>
  <div className="featured-small-grid">
    {recommendations.slice(1, 5).map(product => (
      <ProductCard key={product.id} product={product} size="small" />
    ))}
  </div>
</div>
```

---

## 🔄 Cuándo Actualizar las Recomendaciones

```jsx
// Actualizar cuando el usuario:
useEffect(() => {
  fetchRecommendations();
}, [
  // Triggers de actualización:
  userLoggedIn,        // Cuando inicia sesión
  newPurchase,         // Después de una compra
  // O cada X minutos:
]);

// Auto-refresh cada 5 minutos
useEffect(() => {
  const interval = setInterval(() => {
    fetchRecommendations();
  }, 5 * 60 * 1000); // 5 minutos

  return () => clearInterval(interval);
}, []);
```

---

## 📊 Métricas y Analytics (Opcional)

```jsx
const trackRecommendationClick = (productId) => {
  // Enviar evento a Google Analytics
  gtag('event', 'recommendation_click', {
    product_id: productId,
    user_id: currentUser.id
  });
  
  // O enviar a tu propio backend
  axios.post('/api/analytics/recommendation-click/', {
    product_id: productId
  });
};
```

---

## ✅ Checklist de Implementación

- [ ] Crear componente `PersonalizedBanner.jsx`
- [ ] Agregar estilos CSS personalizados
- [ ] Integrar en página de inicio (`Home.jsx`)
- [ ] Probar con usuario CON historial de compras
- [ ] Probar con usuario SIN historial (debe mostrar populares)
- [ ] Verificar responsive en móvil
- [ ] Implementar botón "Agregar al carrito" funcional
- [ ] Agregar loading state mientras carga
- [ ] Manejar errores de red
- [ ] (Opcional) Agregar analytics para medir clicks

---

## 🚀 Despliegue

1. **Commitear cambios en backend:**
```bash
cd backend_2ex
git add products/views.py products/urls.py
git commit -m "feat: agregar endpoint de recomendaciones personalizadas con IA"
git push origin main
```

2. **Render desplegará automáticamente** (unos 5-10 minutos)

3. **Actualizar frontend en Vercel:**
```bash
cd frontend
# Implementar componente PersonalizedBanner
git add .
git commit -m "feat: agregar banner de recomendaciones personalizadas"
git push origin main
```

---

## 🧪 Pruebas

### **Probar el endpoint directamente:**
```bash
# 1. Obtener token
curl -X POST https://backend-2ex-ecommerce.onrender.com/api/users/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"juan_cliente","password":"password123"}'

# 2. Obtener recomendaciones
curl -X GET "https://backend-2ex-ecommerce.onrender.com/api/products/personalized/?limit=6" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### **Resultado esperado:**
```json
{
  "user": "juan_cliente",
  "count": 6,
  "strategy_used": "personalized_ai",
  "favorite_categories": ["Electrónica", "Gaming"],
  "recommendations": [...]
}
```

---

## 📚 Documentación Adicional

- **Endpoint completo:** `GET /api/products/personalized/`
- **Autenticación:** JWT Bearer Token requerido
- **Estrategias de IA:** 
  1. Historial de compras + categorías favoritas
  2. Collaborative filtering (usuarios similares)
  3. Productos populares (fallback)

---

## 💡 Tips de UX

1. **Mostrar indicador visual:** "Recomendado para ti 🎯"
2. **Explicar por qué:** "Basado en tus compras en Electrónica"
3. **Limitar a 4-6 productos** para no abrumar
4. **Auto-scroll horizontal** en móvil
5. **Actualizar periódicamente** (no en cada carga de página)

---

## 🎉 Resultado Final

```
┌─────────────────────────────────────────────────────┐
│   🎯 Recomendado para ti - Gaming & Electrónica     │
│   Basado en tu historial de compras                 │
├─────────────────────────────────────────────────────┤
│                                                       │
│  [Img]  [Img]  [Img]  [Img]  [Img]  [Img]          │
│  $99    $199   $499   $299   $799   $149            │
│  [🛒]   [🛒]   [🛒]   [🛒]   [🛒]   [🛒]            │
│                                                       │
└─────────────────────────────────────────────────────┘
```

**El backend está 100% listo. Solo falta implementar el componente en el frontend.** ✅
