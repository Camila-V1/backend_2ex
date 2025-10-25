# SmartSales365 API

**Versión:** 1.0.0

**Descripción:** 
    Documentación oficial para la API del sistema de gestión comercial inteligente SmartSales365.
    
    ## 🎯 Características Principales
    
    - **Autenticación JWT**: Sistema seguro con tokens de acceso y refresco
    - **E-commerce Completo**: Productos, categorías, órdenes de compra
    - **Integración Stripe**: Pagos en línea con webhooks automáticos
    - **Reportes Inteligentes**: Generación de reportes PDF/Excel con IA
    - **Machine Learning**: Predicciones de ventas con Random Forest
    - **Comprobantes**: Generación automática de facturas en PDF
    
    ## 🔐 Autenticación
    
    1. Obtén un token JWT desde `/api/token/` con tus credenciales
    2. Usa el token en el header: `Authorization: Bearer <tu_token>`
    3. Refresca el token cuando expire usando `/api/token/refresh/`
    
    ## 📚 Documentación Adicional
    
    - [Guía de URLs](/api/docs/)
    - [Configuración de Stripe](STRIPE_SETUP_GUIDE.md)
    - [Reportes con IA](AI_REPORTS_IMPLEMENTATION.md)
    - [Machine Learning](ML_PREDICTIONS_IMPLEMENTATION.md)
    

## 📊 Estadísticas

- **Total de Rutas:** 30
- **Total de Endpoints:** 51
- **Componentes (Schemas):** 53

## 📑 Tabla de Contenidos

- [Admin](#admin) (3 endpoints)
- [Users](#users) (1 endpoints)
- [api](#api) (47 endpoints)

---

## Admin

### 🔵 GET `/api/orders/admin/analytics/sales/`

**Descripción:**

Análisis detallado de ventas diarias (últimos 30 días)

**Operation ID:** `api_orders_admin_analytics_sales_retrieve`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`SalesAnalyticsResponse`](#schema-salesanalyticsresponse)


---

### 🔵 GET `/api/orders/admin/dashboard/`

**Descripción:**

Dashboard con estadísticas administrativas. Incluye overview, ventas, productos top, órdenes recientes y stock bajo.

**Operation ID:** `api_orders_admin_dashboard_retrieve`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`DashboardResponse`](#schema-dashboardresponse)


---

### 🔵 GET `/api/orders/admin/users/`

**Descripción:**

Lista de todos los usuarios del sistema (excepto administradores) con sus estadísticas de compras

**Operation ID:** `api_orders_admin_users_retrieve`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`AdminUsersResponse`](#schema-adminusersresponse)


---

## Users

### 🔵 GET `/api/users/profile/`

**Descripción:**

Obtiene el perfil del usuario autenticado actualmente

**Operation ID:** `api_users_profile_retrieve`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`UserProfile`](#schema-userprofile)


---

## api

### 🔵 GET `/api/orders/`

**Descripción:**

ViewSet para ver órdenes. La creación se manejará en un endpoint aparte.
- list: Un usuario ve sus propias órdenes. Un admin ve todas.
- retrieve: Un usuario ve el detalle de su orden. Un admin ve cualquiera.

**Operation ID:** `api_orders_list`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Respuestas:**

**200** - 


---

### 🟢 POST `/api/orders/{order_id}/create-checkout-session/`

**Descripción:**

Crea una sesión de pago en Stripe para una orden específica.

**Operation ID:** `api_orders_create_checkout_session_create`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `order_id` | path | integer | ✅ Sí |  |

**Cuerpo de Solicitud:**

⚠️ **Requerido**

**Content-Type:** `application/json`

**Schema:** [`OrderCreateRequest`](#schema-ordercreaterequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`OrderCreateRequest`](#schema-ordercreaterequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`OrderCreateRequest`](#schema-ordercreaterequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`OrderCreate`](#schema-ordercreate)


---

### 🔵 GET `/api/orders/{id}/`

**Descripción:**

ViewSet para ver órdenes. La creación se manejará en un endpoint aparte.
- list: Un usuario ve sus propias órdenes. Un admin ve todas.
- retrieve: Un usuario ve el detalle de su orden. Un admin ve cualquiera.

**Operation ID:** `api_orders_retrieve`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | string | ✅ Sí |  |

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`Order`](#schema-order)


---

### 🔵 GET `/api/orders/admin/`

**Descripción:**

ViewSet para administración completa de órdenes (solo admins)
- GET /api/admin/orders/ - Lista todas las órdenes
- GET /api/admin/orders/{id}/ - Detalle de una orden
- PATCH /api/admin/orders/{id}/ - Actualizar estado de orden
- DELETE /api/admin/orders/{id}/ - Eliminar orden

**Operation ID:** `api_orders_admin_list`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Respuestas:**

**200** - 


---

### 🟢 POST `/api/orders/admin/`

**Descripción:**

ViewSet para administración completa de órdenes (solo admins)
- GET /api/admin/orders/ - Lista todas las órdenes
- GET /api/admin/orders/{id}/ - Detalle de una orden
- PATCH /api/admin/orders/{id}/ - Actualizar estado de orden
- DELETE /api/admin/orders/{id}/ - Eliminar orden

**Operation ID:** `api_orders_admin_create`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Cuerpo de Solicitud:**

**Content-Type:** `application/json`

**Schema:** [`OrderRequest`](#schema-orderrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`OrderRequest`](#schema-orderrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`OrderRequest`](#schema-orderrequest)

**Respuestas:**

**201** - 

- Content-Type: `application/json`
- Schema: [`Order`](#schema-order)


---

### 🔵 GET `/api/orders/admin/{id}/`

**Descripción:**

ViewSet para administración completa de órdenes (solo admins)
- GET /api/admin/orders/ - Lista todas las órdenes
- GET /api/admin/orders/{id}/ - Detalle de una orden
- PATCH /api/admin/orders/{id}/ - Actualizar estado de orden
- DELETE /api/admin/orders/{id}/ - Eliminar orden

**Operation ID:** `api_orders_admin_retrieve`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | string | ✅ Sí |  |

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`Order`](#schema-order)


---

### 🟠 PUT `/api/orders/admin/{id}/`

**Descripción:**

ViewSet para administración completa de órdenes (solo admins)
- GET /api/admin/orders/ - Lista todas las órdenes
- GET /api/admin/orders/{id}/ - Detalle de una orden
- PATCH /api/admin/orders/{id}/ - Actualizar estado de orden
- DELETE /api/admin/orders/{id}/ - Eliminar orden

**Operation ID:** `api_orders_admin_update`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | string | ✅ Sí |  |

**Cuerpo de Solicitud:**

**Content-Type:** `application/json`

**Schema:** [`OrderRequest`](#schema-orderrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`OrderRequest`](#schema-orderrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`OrderRequest`](#schema-orderrequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`Order`](#schema-order)


---

### 🟣 PATCH `/api/orders/admin/{id}/`

**Descripción:**

ViewSet para administración completa de órdenes (solo admins)
- GET /api/admin/orders/ - Lista todas las órdenes
- GET /api/admin/orders/{id}/ - Detalle de una orden
- PATCH /api/admin/orders/{id}/ - Actualizar estado de orden
- DELETE /api/admin/orders/{id}/ - Eliminar orden

**Operation ID:** `api_orders_admin_partial_update`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | string | ✅ Sí |  |

**Cuerpo de Solicitud:**

**Content-Type:** `application/json`

**Schema:** [`PatchedOrderRequest`](#schema-patchedorderrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`PatchedOrderRequest`](#schema-patchedorderrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`PatchedOrderRequest`](#schema-patchedorderrequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`Order`](#schema-order)


---

### 🔴 DELETE `/api/orders/admin/{id}/`

**Descripción:**

ViewSet para administración completa de órdenes (solo admins)
- GET /api/admin/orders/ - Lista todas las órdenes
- GET /api/admin/orders/{id}/ - Detalle de una orden
- PATCH /api/admin/orders/{id}/ - Actualizar estado de orden
- DELETE /api/admin/orders/{id}/ - Eliminar orden

**Operation ID:** `api_orders_admin_destroy`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | string | ✅ Sí |  |

**Respuestas:**

**204** - No response body


---

### 🟢 POST `/api/orders/admin/{id}/update_status/`

**Descripción:**

Endpoint especial para cambiar el estado de una orden
POST /api/admin/orders/{id}/update_status/
Body: {"status": "shipped"}

**Operation ID:** `api_orders_admin_update_status_create`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | string | ✅ Sí |  |

**Cuerpo de Solicitud:**

**Content-Type:** `application/json`

**Schema:** [`OrderRequest`](#schema-orderrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`OrderRequest`](#schema-orderrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`OrderRequest`](#schema-orderrequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`Order`](#schema-order)


---

### 🟢 POST `/api/orders/cart/add-natural-language/`

**Descripción:**

🎤 Vista para agregar productos al carrito usando lenguaje natural (texto o voz)
POST /api/cart/add-natural-language/

Ejemplos de comandos:
- "Agrega 2 smartphones al carrito"
- "Quiero 3 laptops y 1 mouse"
- "Añade el curso de Python"
- "Comprar 5 auriculares bluetooth"

**Operation ID:** `api_orders_cart_add_natural_language_create`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Cuerpo de Solicitud:**

⚠️ **Requerido**

**Content-Type:** `application/json`

**Schema:** [`NLPCartRequestRequest`](#schema-nlpcartrequestrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`NLPCartRequestRequest`](#schema-nlpcartrequestrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`NLPCartRequestRequest`](#schema-nlpcartrequestrequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`NLPCartRequest`](#schema-nlpcartrequest)


---

### 🔵 GET `/api/orders/cart/suggestions/`

**Descripción:**

🔍 Vista para obtener sugerencias de productos (autocompletado)
GET /api/cart/suggestions/?q=smart

**Operation ID:** `api_orders_cart_suggestions_retrieve`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`ProductSuggestionsResponse`](#schema-productsuggestionsresponse)


---

### 🟢 POST `/api/orders/create/`

**Descripción:**

Vista para crear una nueva orden a partir del carrito de compras.
Permisos: CAJERO, MANAGER o ADMIN pueden crear órdenes.

**Operation ID:** `api_orders_create_create`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Cuerpo de Solicitud:**

⚠️ **Requerido**

**Content-Type:** `application/json`

**Schema:** [`OrderCreateRequest`](#schema-ordercreaterequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`OrderCreateRequest`](#schema-ordercreaterequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`OrderCreateRequest`](#schema-ordercreaterequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`OrderCreate`](#schema-ordercreate)


---

### 🟢 POST `/api/orders/stripe-webhook/`

**Descripción:**

Escucha los eventos de Stripe. Específicamente, cuando una sesión de checkout se completa,
actualiza el estado de la orden correspondiente a 'PAGADO'.

**Operation ID:** `api_orders_stripe_webhook_create`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Cuerpo de Solicitud:**

⚠️ **Requerido**

**Content-Type:** `application/json`

**Schema:** [`StripeWebhookRequest`](#schema-stripewebhookrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`StripeWebhookRequest`](#schema-stripewebhookrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`StripeWebhookRequest`](#schema-stripewebhookrequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`StripeWebhook`](#schema-stripewebhook)


---

### 🔵 GET `/api/predictions/sales/`

**Descripción:**

API endpoint para obtener predicciones de ventas futuras usando el modelo entrenado.

Requiere que el modelo haya sido entrenado previamente con:
python manage.py train_sales_model

**Operation ID:** `api_predictions_sales_retrieve`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`SalesPredictionResponse`](#schema-salespredictionresponse)


---

### 🔵 GET `/api/products/`

**Operation ID:** `api_products_list`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Respuestas:**

**200** - 


---

### 🟢 POST `/api/products/`

**Operation ID:** `api_products_create`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Cuerpo de Solicitud:**

⚠️ **Requerido**

**Content-Type:** `application/json`

**Schema:** [`ProductRequest`](#schema-productrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`ProductRequest`](#schema-productrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`ProductRequest`](#schema-productrequest)

**Respuestas:**

**201** - 

- Content-Type: `application/json`
- Schema: [`Product`](#schema-product)


---

### 🔵 GET `/api/products/{id}/`

**Operation ID:** `api_products_retrieve`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí |  |

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`Product`](#schema-product)


---

### 🟠 PUT `/api/products/{id}/`

**Operation ID:** `api_products_update`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí |  |

**Cuerpo de Solicitud:**

⚠️ **Requerido**

**Content-Type:** `application/json`

**Schema:** [`ProductRequest`](#schema-productrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`ProductRequest`](#schema-productrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`ProductRequest`](#schema-productrequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`Product`](#schema-product)


---

### 🟣 PATCH `/api/products/{id}/`

**Operation ID:** `api_products_partial_update`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí |  |

**Cuerpo de Solicitud:**

**Content-Type:** `application/json`

**Schema:** [`PatchedProductRequest`](#schema-patchedproductrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`PatchedProductRequest`](#schema-patchedproductrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`PatchedProductRequest`](#schema-patchedproductrequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`Product`](#schema-product)


---

### 🔴 DELETE `/api/products/{id}/`

**Operation ID:** `api_products_destroy`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí |  |

**Respuestas:**

**204** - No response body


---

### 🔵 GET `/api/products/{id}/recommendations/`

**Descripción:**

Sistema de recomendación simple: productos comprados junto con este.
GET /api/products/{id}/recommendations/

**Operation ID:** `api_products_recommendations_retrieve`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí |  |

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`Product`](#schema-product)


---

### 🔵 GET `/api/products/{id}/reviews/`

**Descripción:**

Endpoint para gestionar reseñas de un producto.
GET /api/products/{id}/reviews/ - Lista todas las reseñas
POST /api/products/{id}/reviews/ - Crear una reseña (requiere autenticación)

**Operation ID:** `api_products_reviews_retrieve_2`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí |  |

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`Product`](#schema-product)


---

### 🟢 POST `/api/products/{id}/reviews/`

**Descripción:**

Endpoint para gestionar reseñas de un producto.
GET /api/products/{id}/reviews/ - Lista todas las reseñas
POST /api/products/{id}/reviews/ - Crear una reseña (requiere autenticación)

**Operation ID:** `api_products_reviews_create_2`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí |  |

**Cuerpo de Solicitud:**

⚠️ **Requerido**

**Content-Type:** `application/json`

**Schema:** [`ProductRequest`](#schema-productrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`ProductRequest`](#schema-productrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`ProductRequest`](#schema-productrequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`Product`](#schema-product)


---

### 🔵 GET `/api/products/categories/`

**Operation ID:** `api_products_categories_list`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Respuestas:**

**200** - 


---

### 🟢 POST `/api/products/categories/`

**Operation ID:** `api_products_categories_create`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Cuerpo de Solicitud:**

⚠️ **Requerido**

**Content-Type:** `application/json`

**Schema:** [`CategoryRequest`](#schema-categoryrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`CategoryRequest`](#schema-categoryrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`CategoryRequest`](#schema-categoryrequest)

**Respuestas:**

**201** - 

- Content-Type: `application/json`
- Schema: [`Category`](#schema-category)


---

### 🔵 GET `/api/products/categories/{id}/`

**Operation ID:** `api_products_categories_retrieve`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí | A unique integer value identifying this Categoría. |

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`Category`](#schema-category)


---

### 🟠 PUT `/api/products/categories/{id}/`

**Operation ID:** `api_products_categories_update`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí | A unique integer value identifying this Categoría. |

**Cuerpo de Solicitud:**

⚠️ **Requerido**

**Content-Type:** `application/json`

**Schema:** [`CategoryRequest`](#schema-categoryrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`CategoryRequest`](#schema-categoryrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`CategoryRequest`](#schema-categoryrequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`Category`](#schema-category)


---

### 🟣 PATCH `/api/products/categories/{id}/`

**Operation ID:** `api_products_categories_partial_update`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí | A unique integer value identifying this Categoría. |

**Cuerpo de Solicitud:**

**Content-Type:** `application/json`

**Schema:** [`PatchedCategoryRequest`](#schema-patchedcategoryrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`PatchedCategoryRequest`](#schema-patchedcategoryrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`PatchedCategoryRequest`](#schema-patchedcategoryrequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`Category`](#schema-category)


---

### 🔴 DELETE `/api/products/categories/{id}/`

**Operation ID:** `api_products_categories_destroy`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí | A unique integer value identifying this Categoría. |

**Respuestas:**

**204** - No response body


---

### 🔵 GET `/api/products/reviews/`

**Descripción:**

ViewSet para gestionar reseñas.
Solo el autor o un admin pueden editar/eliminar una reseña.

**Operation ID:** `api_products_reviews_list`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Respuestas:**

**200** - 


---

### 🟢 POST `/api/products/reviews/`

**Descripción:**

ViewSet para gestionar reseñas.
Solo el autor o un admin pueden editar/eliminar una reseña.

**Operation ID:** `api_products_reviews_create`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Cuerpo de Solicitud:**

⚠️ **Requerido**

**Content-Type:** `application/json`

**Schema:** [`ReviewRequest`](#schema-reviewrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`ReviewRequest`](#schema-reviewrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`ReviewRequest`](#schema-reviewrequest)

**Respuestas:**

**201** - 

- Content-Type: `application/json`
- Schema: [`Review`](#schema-review)


---

### 🔵 GET `/api/products/reviews/{id}/`

**Descripción:**

ViewSet para gestionar reseñas.
Solo el autor o un admin pueden editar/eliminar una reseña.

**Operation ID:** `api_products_reviews_retrieve`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí | A unique integer value identifying this Reseña. |

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`Review`](#schema-review)


---

### 🟠 PUT `/api/products/reviews/{id}/`

**Descripción:**

Solo el autor o admin pueden actualizar.

**Operation ID:** `api_products_reviews_update`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí | A unique integer value identifying this Reseña. |

**Cuerpo de Solicitud:**

⚠️ **Requerido**

**Content-Type:** `application/json`

**Schema:** [`ReviewRequest`](#schema-reviewrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`ReviewRequest`](#schema-reviewrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`ReviewRequest`](#schema-reviewrequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`Review`](#schema-review)


---

### 🟣 PATCH `/api/products/reviews/{id}/`

**Descripción:**

ViewSet para gestionar reseñas.
Solo el autor o un admin pueden editar/eliminar una reseña.

**Operation ID:** `api_products_reviews_partial_update`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí | A unique integer value identifying this Reseña. |

**Cuerpo de Solicitud:**

**Content-Type:** `application/json`

**Schema:** [`PatchedReviewRequest`](#schema-patchedreviewrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`PatchedReviewRequest`](#schema-patchedreviewrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`PatchedReviewRequest`](#schema-patchedreviewrequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`Review`](#schema-review)


---

### 🔴 DELETE `/api/products/reviews/{id}/`

**Descripción:**

Solo el autor o admin pueden eliminar.

**Operation ID:** `api_products_reviews_destroy`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí | A unique integer value identifying this Reseña. |

**Respuestas:**

**204** - No response body


---

### 🟢 POST `/api/reports/dynamic-parser/`

**Descripción:**

Vista inteligente que interpreta comandos en lenguaje natural para generar reportes.

Ejemplos de comandos:
- "Quiero un reporte de ventas del mes de octubre en PDF"
- "Dame el reporte de ventas de septiembre en excel"
- "Genera un reporte de productos en PDF"
- "Reporte de ventas del 01/10/2025 al 31/10/2025 en excel"
- "Reporte de ventas agrupado por producto del mes de octubre"
- "Muestra las ventas con nombres de clientes del mes pasado"
- "Dame un reporte de compras por cliente con sus nombres"

**Operation ID:** `api_reports_dynamic_parser_create`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Cuerpo de Solicitud:**

⚠️ **Requerido**

**Content-Type:** `application/json`

**Schema:** [`DynamicReportRequestRequest`](#schema-dynamicreportrequestrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`DynamicReportRequestRequest`](#schema-dynamicreportrequestrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`DynamicReportRequestRequest`](#schema-dynamicreportrequestrequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`DynamicReportRequest`](#schema-dynamicreportrequest)


---

### 🔵 GET `/api/reports/orders/{order_id}/invoice/`

**Descripción:**

Vista para generar el comprobante de venta (invoice/factura) de una orden individual.

Permisos:
- El usuario debe ser el dueño de la orden O ser administrador

**Operation ID:** `api_reports_orders_invoice_retrieve`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `order_id` | path | integer | ✅ Sí |  |

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`InvoiceResponse`](#schema-invoiceresponse)


---

### 🟢 POST `/api/token/`

**Descripción:**

Takes a set of user credentials and returns an access and refresh JSON web
token pair to prove the authentication of those credentials.

**Operation ID:** `api_token_create`

**Autenticación:** Requerida

- `Bearer`: type, scheme, bearerFormat

**Cuerpo de Solicitud:**

⚠️ **Requerido**

**Content-Type:** `application/json`

**Schema:** [`TokenObtainPairRequest`](#schema-tokenobtainpairrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`TokenObtainPairRequest`](#schema-tokenobtainpairrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`TokenObtainPairRequest`](#schema-tokenobtainpairrequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`TokenObtainPair`](#schema-tokenobtainpair)


---

### 🟢 POST `/api/token/refresh/`

**Descripción:**

Takes a refresh type JSON web token and returns an access type JSON web
token if the refresh token is valid.

**Operation ID:** `api_token_refresh_create`

**Autenticación:** Requerida

- `Bearer`: type, scheme, bearerFormat

**Cuerpo de Solicitud:**

⚠️ **Requerido**

**Content-Type:** `application/json`

**Schema:** [`TokenRefreshRequest`](#schema-tokenrefreshrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`TokenRefreshRequest`](#schema-tokenrefreshrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`TokenRefreshRequest`](#schema-tokenrefreshrequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`TokenRefresh`](#schema-tokenrefresh)


---

### 🟢 POST `/api/token/verify/`

**Descripción:**

Takes a token and indicates if it is valid.  This view provides no
information about a token's fitness for a particular use.

**Operation ID:** `api_token_verify_create`

**Autenticación:** Requerida

- `Bearer`: type, scheme, bearerFormat

**Cuerpo de Solicitud:**

⚠️ **Requerido**

**Content-Type:** `application/json`

**Schema:** [`TokenVerifyRequest`](#schema-tokenverifyrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`TokenVerifyRequest`](#schema-tokenverifyrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`TokenVerifyRequest`](#schema-tokenverifyrequest)

**Respuestas:**

**200** - No response body


---

### 🔵 GET `/api/users/`

**Descripción:**

ViewSet que maneja el CRUD completo para los Usuarios.
- list: GET /api/users/ (Solo Admins)
- create: POST /api/users/ (Cualquiera puede registrarse)
- retrieve: GET /api/users/{id}/ (Admin o el propio usuario)
- update: PUT /api/users/{id}/ (Admin o el propio usuario)
- partial_update: PATCH /api/users/{id}/ (Admin o el propio usuario)
- destroy: DELETE /api/users/{id}/ (Admin o el propio usuario)

**Operation ID:** `api_users_list`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Respuestas:**

**200** - 


---

### 🟢 POST `/api/users/`

**Descripción:**

ViewSet que maneja el CRUD completo para los Usuarios.
- list: GET /api/users/ (Solo Admins)
- create: POST /api/users/ (Cualquiera puede registrarse)
- retrieve: GET /api/users/{id}/ (Admin o el propio usuario)
- update: PUT /api/users/{id}/ (Admin o el propio usuario)
- partial_update: PATCH /api/users/{id}/ (Admin o el propio usuario)
- destroy: DELETE /api/users/{id}/ (Admin o el propio usuario)

**Operation ID:** `api_users_create`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Cuerpo de Solicitud:**

⚠️ **Requerido**

**Content-Type:** `application/json`

**Schema:** [`UserRegistrationRequest`](#schema-userregistrationrequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`UserRegistrationRequest`](#schema-userregistrationrequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`UserRegistrationRequest`](#schema-userregistrationrequest)

**Respuestas:**

**201** - 

- Content-Type: `application/json`
- Schema: [`UserRegistration`](#schema-userregistration)


---

### 🔵 GET `/api/users/{id}/`

**Descripción:**

ViewSet que maneja el CRUD completo para los Usuarios.
- list: GET /api/users/ (Solo Admins)
- create: POST /api/users/ (Cualquiera puede registrarse)
- retrieve: GET /api/users/{id}/ (Admin o el propio usuario)
- update: PUT /api/users/{id}/ (Admin o el propio usuario)
- partial_update: PATCH /api/users/{id}/ (Admin o el propio usuario)
- destroy: DELETE /api/users/{id}/ (Admin o el propio usuario)

**Operation ID:** `api_users_retrieve`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí | A unique integer value identifying this user. |

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`UserProfile`](#schema-userprofile)


---

### 🟠 PUT `/api/users/{id}/`

**Descripción:**

ViewSet que maneja el CRUD completo para los Usuarios.
- list: GET /api/users/ (Solo Admins)
- create: POST /api/users/ (Cualquiera puede registrarse)
- retrieve: GET /api/users/{id}/ (Admin o el propio usuario)
- update: PUT /api/users/{id}/ (Admin o el propio usuario)
- partial_update: PATCH /api/users/{id}/ (Admin o el propio usuario)
- destroy: DELETE /api/users/{id}/ (Admin o el propio usuario)

**Operation ID:** `api_users_update`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí | A unique integer value identifying this user. |

**Cuerpo de Solicitud:**

**Content-Type:** `application/json`

**Schema:** [`UserProfileRequest`](#schema-userprofilerequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`UserProfileRequest`](#schema-userprofilerequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`UserProfileRequest`](#schema-userprofilerequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`UserProfile`](#schema-userprofile)


---

### 🟣 PATCH `/api/users/{id}/`

**Descripción:**

ViewSet que maneja el CRUD completo para los Usuarios.
- list: GET /api/users/ (Solo Admins)
- create: POST /api/users/ (Cualquiera puede registrarse)
- retrieve: GET /api/users/{id}/ (Admin o el propio usuario)
- update: PUT /api/users/{id}/ (Admin o el propio usuario)
- partial_update: PATCH /api/users/{id}/ (Admin o el propio usuario)
- destroy: DELETE /api/users/{id}/ (Admin o el propio usuario)

**Operation ID:** `api_users_partial_update`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí | A unique integer value identifying this user. |

**Cuerpo de Solicitud:**

**Content-Type:** `application/json`

**Schema:** [`PatchedUserProfileRequest`](#schema-patcheduserprofilerequest)

**Content-Type:** `application/x-www-form-urlencoded`

**Schema:** [`PatchedUserProfileRequest`](#schema-patcheduserprofilerequest)

**Content-Type:** `multipart/form-data`

**Schema:** [`PatchedUserProfileRequest`](#schema-patcheduserprofilerequest)

**Respuestas:**

**200** - 

- Content-Type: `application/json`
- Schema: [`UserProfile`](#schema-userprofile)


---

### 🔴 DELETE `/api/users/{id}/`

**Descripción:**

ViewSet que maneja el CRUD completo para los Usuarios.
- list: GET /api/users/ (Solo Admins)
- create: POST /api/users/ (Cualquiera puede registrarse)
- retrieve: GET /api/users/{id}/ (Admin o el propio usuario)
- update: PUT /api/users/{id}/ (Admin o el propio usuario)
- partial_update: PATCH /api/users/{id}/ (Admin o el propio usuario)
- destroy: DELETE /api/users/{id}/ (Admin o el propio usuario)

**Operation ID:** `api_users_destroy`

**Autenticación:** Requerida

- `jwtAuth`
- `Bearer`: type, scheme, bearerFormat

**Parámetros:**

| Nombre | Ubicación | Tipo | Requerido | Descripción |
|--------|-----------|------|-----------|-------------|
| `id` | path | integer | ✅ Sí | A unique integer value identifying this user. |

**Respuestas:**

**204** - No response body


---

## 🗂️ Modelos de Datos (Schemas)

### Schema: `AdminUser`

Serializer para usuario en lista de admin

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | integer | ✅ Sí |  |
| `username` | string | ✅ Sí |  |
| `email` | string (email) | ✅ Sí |  |
| `first_name` | string | ✅ Sí |  |
| `last_name` | string | ✅ Sí |  |
| `is_active` | boolean | ✅ Sí |  |
| `date_joined` | string (date-time) | ✅ Sí |  |
| `total_orders` | integer | ✅ Sí |  |
| `total_spent` | number (double) | ✅ Sí |  |

---

### Schema: `AdminUsersResponse`

Serializer para respuesta de lista de usuarios

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `count` | integer | ✅ Sí |  |
| `users` | array\<[AdminUser](#schema-adminuser)\> | ✅ Sí |  |

---

### Schema: `BlankEnum`

---

### Schema: `Category`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | integer | ✅ Sí |  |
| `name` | string | ✅ Sí |  |
| `description` | string | ❌ No |  |

---

### Schema: `CategoryRequest`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `name` | string | ✅ Sí |  |
| `description` | string | ❌ No |  |

---

### Schema: `DailySales`

Serializer para ventas diarias

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `day` | string (date) | ✅ Sí |  |
| `orders_count` | integer | ✅ Sí |  |
| `revenue` | string (decimal) | ✅ Sí |  |

---

### Schema: `DashboardOverview`

Serializer para overview del dashboard

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `total_orders` | integer | ✅ Sí |  |
| `total_users` | integer | ✅ Sí |  |
| `total_products` | integer | ✅ Sí |  |
| `active_products` | integer | ✅ Sí |  |
| `total_revenue` | number (double) | ✅ Sí |  |

---

### Schema: `DashboardResponse`

Serializer para respuesta completa del dashboard

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `overview` | object | ✅ Sí |  |
| `sales` | object | ✅ Sí |  |
| `orders_by_status` | array\<object\> | ✅ Sí |  |
| `top_products` | array\<[TopProduct](#schema-topproduct)\> | ✅ Sí |  |
| `recent_orders` | array\<[Order](#schema-order)\> | ✅ Sí |  |
| `low_stock_products` | array\<[LowStockProduct](#schema-lowstockproduct)\> | ✅ Sí |  |
| `_from_cache` | boolean | ✅ Sí |  |

---

### Schema: `DashboardSales`

Serializer para datos de ventas del dashboard

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `current_month_revenue` | number (double) | ✅ Sí |  |
| `last_month_revenue` | number (double) | ✅ Sí |  |
| `growth_percentage` | number (double) | ✅ Sí |  |

---

### Schema: `DynamicReportRequest`

Serializer para solicitud de reporte dinámico con lenguaje natural

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `prompt` | string | ✅ Sí | Comando en lenguaje natural para generar reportes.                  Ejemplos:         - "Quiero un reporte de ventas del mes de octubre en PDF"         - "Dame el reporte de ventas de septiembre en excel"         - "Genera un reporte de productos en PDF"         - "Reporte de ventas del 01/10/2025 al 31/10/2025 en excel"         - "Reporte de ventas agrupado por producto del mes de octubre"         - "Muestra las ventas con nombres de clientes del mes pasado"          |

---

### Schema: `DynamicReportRequestRequest`

Serializer para solicitud de reporte dinámico con lenguaje natural

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `prompt` | string | ✅ Sí | Comando en lenguaje natural para generar reportes.                  Ejemplos:         - "Quiero un reporte de ventas del mes de octubre en PDF"         - "Dame el reporte de ventas de septiembre en excel"         - "Genera un reporte de productos en PDF"         - "Reporte de ventas del 01/10/2025 al 31/10/2025 en excel"         - "Reporte de ventas agrupado por producto del mes de octubre"         - "Muestra las ventas con nombres de clientes del mes pasado"          |

---

### Schema: `InvoiceResponse`

Serializer para respuesta de factura PDF (solo para documentación)

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `message` | string | ❌ No |  |
| `filename` | string | ✅ Sí |  |

---

### Schema: `LowStockProduct`

Serializer para productos con stock bajo

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | integer | ✅ Sí |  |
| `name` | string | ✅ Sí |  |
| `stock` | integer | ✅ Sí |  |
| `price` | string (decimal) | ✅ Sí |  |

---

### Schema: `ModelInfo`

Serializer para información del modelo ML

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `trained` | boolean | ✅ Sí |  |
| `model_path` | string | ✅ Sí |  |
| `prediction_period` | string | ✅ Sí |  |
| `start_date` | string (date) | ✅ Sí |  |
| `end_date` | string (date) | ✅ Sí |  |

---

### Schema: `NLPCartRequest`

Serializer para solicitud de carrito con lenguaje natural

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `prompt` | string | ✅ Sí | Comando en lenguaje natural, ej: 'Agrega 2 smartphones al carrito' |

---

### Schema: `NLPCartRequestRequest`

Serializer para solicitud de carrito con lenguaje natural

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `prompt` | string | ✅ Sí | Comando en lenguaje natural, ej: 'Agrega 2 smartphones al carrito' |

---

### Schema: `NullEnum`

---

### Schema: `Order`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | integer | ✅ Sí |  |
| `user` | string | ✅ Sí |  |
| `created_at` | string (date-time) | ✅ Sí |  |
| `status` | object | ❌ No |  |
| `total_price` | string (decimal) | ❌ No |  |
| `total_amount` | string (decimal) | ✅ Sí |  |
| `items` | array\<[OrderItem](#schema-orderitem)\> | ✅ Sí |  |

---

### Schema: `OrderCreate`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `items` | array\<[OrderItemCreate](#schema-orderitemcreate)\> | ✅ Sí |  |

---

### Schema: `OrderCreateRequest`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `items` | array\<[OrderItemCreateRequest](#schema-orderitemcreaterequest)\> | ✅ Sí |  |

---

### Schema: `OrderItem`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | integer | ✅ Sí |  |
| `product` | integer | ❌ No |  |
| `quantity` | integer | ❌ No |  |
| `price` | string (decimal) | ✅ Sí |  |

---

### Schema: `OrderItemCreate`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `product_id` | integer | ✅ Sí |  |
| `quantity` | integer | ✅ Sí |  |

---

### Schema: `OrderItemCreateRequest`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `product_id` | integer | ✅ Sí |  |
| `quantity` | integer | ✅ Sí |  |

---

### Schema: `OrderItemRequest`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `product` | integer | ❌ No |  |
| `quantity` | integer | ❌ No |  |
| `price` | string (decimal) | ✅ Sí |  |

---

### Schema: `OrderRequest`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `status` | object | ❌ No |  |
| `total_price` | string (decimal) | ❌ No |  |

---

### Schema: `PatchedCategoryRequest`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `name` | string | ❌ No |  |
| `description` | string | ❌ No |  |

---

### Schema: `PatchedOrderRequest`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `status` | object | ❌ No |  |
| `total_price` | string (decimal) | ❌ No |  |

---

### Schema: `PatchedProductRequest`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `name` | string | ❌ No |  |
| `description` | string | ❌ No |  |
| `price` | string (decimal) | ❌ No |  |
| `stock` | integer | ❌ No |  |
| `category` | integer | ❌ No |  |
| `warranty_info` | string | ❌ No |  |
| `is_active` | boolean | ❌ No |  |

---

### Schema: `PatchedReviewRequest`

Serializer para Reseñas de productos.

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `product` | integer | ❌ No |  |
| `rating` | integer | ❌ No |  |
| `comment` | string | ❌ No |  |

---

### Schema: `PatchedUserProfileRequest`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `email` | string (email) | ❌ No |  |
| `first_name` | string | ❌ No |  |
| `last_name` | string | ❌ No |  |
| `role` | object | ❌ No |  |

---

### Schema: `PredictionItem`

Serializer para un item de predicción individual

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `date` | string (date) | ✅ Sí | Fecha de la predicción |
| `predicted_sales` | number (double) | ✅ Sí | Cantidad de unidades predichas |
| `day_of_week` | string | ✅ Sí | Día de la semana |

---

### Schema: `Product`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | integer | ✅ Sí |  |
| `name` | string | ✅ Sí |  |
| `description` | string | ✅ Sí |  |
| `price` | string (decimal) | ✅ Sí |  |
| `stock` | integer | ❌ No |  |
| `category` | integer | ❌ No |  |
| `category_name` | string | ✅ Sí |  |
| `category_details` | object | ✅ Sí |  |
| `warranty_info` | string | ❌ No |  |
| `is_active` | boolean | ❌ No |  |
| `average_rating` | number (double) | ✅ Sí |  |
| `review_count` | integer | ✅ Sí |  |

---

### Schema: `ProductRequest`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `name` | string | ✅ Sí |  |
| `description` | string | ✅ Sí |  |
| `price` | string (decimal) | ✅ Sí |  |
| `stock` | integer | ❌ No |  |
| `category` | integer | ❌ No |  |
| `warranty_info` | string | ❌ No |  |
| `is_active` | boolean | ❌ No |  |

---

### Schema: `ProductSuggestion`

Serializer para sugerencias de productos

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | integer | ✅ Sí |  |
| `name` | string | ✅ Sí |  |
| `price` | string (decimal) | ✅ Sí |  |
| `category` | string | ✅ Sí |  |

---

### Schema: `ProductSuggestionsResponse`

Serializer para respuesta de sugerencias

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `query` | string | ✅ Sí |  |
| `count` | integer | ✅ Sí |  |
| `suggestions` | array\<[ProductSuggestion](#schema-productsuggestion)\> | ✅ Sí |  |

---

### Schema: `Review`

Serializer para Reseñas de productos.

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | integer | ✅ Sí |  |
| `product` | integer | ✅ Sí |  |
| `user` | integer | ✅ Sí |  |
| `user_username` | string | ✅ Sí |  |
| `user_email` | string | ✅ Sí |  |
| `rating` | integer | ✅ Sí |  |
| `comment` | string | ❌ No |  |
| `created_at` | string (date-time) | ✅ Sí |  |
| `updated_at` | string (date-time) | ✅ Sí |  |

---

### Schema: `ReviewRequest`

Serializer para Reseñas de productos.

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `product` | integer | ✅ Sí |  |
| `rating` | integer | ✅ Sí |  |
| `comment` | string | ❌ No |  |

---

### Schema: `RoleEnum`

* `ADMIN` - Administrador
* `MANAGER` - Gerente
* `CAJERO` - Cajero

---

### Schema: `SalesAnalyticsResponse`

Serializer para respuesta de analytics de ventas

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `daily_sales` | array\<[DailySales](#schema-dailysales)\> | ✅ Sí |  |

---

### Schema: `SalesPredictionResponse`

Serializer para respuesta de predicciones de ventas

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `predictions` | array\<[PredictionItem](#schema-predictionitem)\> | ✅ Sí |  |
| `model_info` | object | ✅ Sí |  |

---

### Schema: `StatusEnum`

* `PENDING` - Pendiente
* `PAID` - Pagado
* `SHIPPED` - Enviado
* `CANCELLED` - Cancelado

---

### Schema: `StripeWebhook`

Serializer para webhook de Stripe (solo para documentación)

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `type` | string | ✅ Sí | Tipo de evento de Stripe |
| `data` | object | ✅ Sí | Datos del evento |

---

### Schema: `StripeWebhookRequest`

Serializer para webhook de Stripe (solo para documentación)

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `type` | string | ✅ Sí | Tipo de evento de Stripe |
| `data` | object | ✅ Sí | Datos del evento |

---

### Schema: `TokenObtainPair`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `access` | string | ✅ Sí |  |
| `refresh` | string | ✅ Sí |  |

---

### Schema: `TokenObtainPairRequest`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `username` | string | ✅ Sí |  |
| `password` | string | ✅ Sí |  |

---

### Schema: `TokenRefresh`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `access` | string | ✅ Sí |  |

---

### Schema: `TokenRefreshRequest`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `refresh` | string | ✅ Sí |  |

---

### Schema: `TokenVerifyRequest`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `token` | string | ✅ Sí |  |

---

### Schema: `TopProduct`

Serializer para productos más vendidos

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `product__id` | integer | ✅ Sí |  |
| `product__name` | string | ✅ Sí |  |
| `product__price` | string (decimal) | ✅ Sí |  |
| `total_sold` | integer | ✅ Sí |  |
| `total_revenue` | string (decimal) | ✅ Sí |  |

---

### Schema: `UserProfile`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | integer | ✅ Sí |  |
| `username` | string | ✅ Sí | Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. |
| `email` | string (email) | ❌ No |  |
| `first_name` | string | ❌ No |  |
| `last_name` | string | ❌ No |  |
| `role` | object | ❌ No |  |
| `is_staff` | boolean | ✅ Sí | Designates whether the user can log into this admin site. |
| `is_superuser` | boolean | ✅ Sí | Designates that this user has all permissions without explicitly assigning them. |
| `is_active` | boolean | ✅ Sí | Designates whether this user should be treated as active. Unselect this instead of deleting accounts. |

---

### Schema: `UserProfileRequest`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `email` | string (email) | ❌ No |  |
| `first_name` | string | ❌ No |  |
| `last_name` | string | ❌ No |  |
| `role` | object | ❌ No |  |

---

### Schema: `UserRegistration`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | integer | ✅ Sí |  |
| `username` | string | ✅ Sí | Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. |
| `email` | string (email) | ❌ No |  |
| `first_name` | string | ✅ Sí |  |
| `last_name` | string | ✅ Sí |  |
| `role` | object | ✅ Sí |  |

---

### Schema: `UserRegistrationRequest`

**Propiedades:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `username` | string | ✅ Sí | Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. |
| `email` | string (email) | ❌ No |  |
| `password` | string | ✅ Sí |  |
| `password2` | string | ✅ Sí |  |
| `first_name` | string | ✅ Sí |  |
| `last_name` | string | ✅ Sí |  |
| `role` | object | ✅ Sí |  |

---

## 🔒 Esquemas de Seguridad

### `jwtAuth`

- **Tipo:** http
- **Esquema:** bearer
- **Formato:** JWT

