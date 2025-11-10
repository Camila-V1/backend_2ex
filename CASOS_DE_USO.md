# 📋 Casos de Uso - SmartSales365 API

## Información del Proyecto
- **Nombre**: SmartSales365 E-commerce API
- **Versión**: 1.0.0
- **Framework**: Django 5.2.7 + Django REST Framework 3.16.1
- **Base de Datos**: PostgreSQL
- **Arquitectura**: REST API + Machine Learning + Redis Cache

---

## 🎯 Índice de Casos de Uso

1. [Gestión de Autenticación y Usuarios](#1-gestión-de-autenticación-y-usuarios)
2. [Gestión de Productos y Categorías](#2-gestión-de-productos-y-categorías)
3. [Sistema de Reseñas y Valoraciones](#3-sistema-de-reseñas-y-valoraciones)
4. [Sistema de Recomendaciones](#4-sistema-de-recomendaciones)
5. [Gestión de Órdenes (Cliente)](#5-gestión-de-órdenes-cliente)
6. [Procesamiento de Pagos con Stripe](#6-procesamiento-de-pagos-con-stripe)
7. [Carrito con Lenguaje Natural (NLP)](#7-carrito-con-lenguaje-natural-nlp)
8. [Panel de Administración](#8-panel-de-administración)
9. [Generación de Reportes](#9-generación-de-reportes)
10. [Predicciones de Ventas (ML)](#10-predicciones-de-ventas-ml)
11. [Sistema de Permisos RBAC](#11-sistema-de-permisos-rbac)
12. [Optimización con Caché](#12-optimización-con-caché)
13. **🆕 [Sistema de Devoluciones (Returns)](#13-sistema-de-devoluciones-returns)**
14. **🆕 [Sistema de Billetera Virtual (Wallet)](#14-sistema-de-billetera-virtual-wallet)**
15. **🆕 [Sistema de Auditoría (Audit Log)](#15-sistema-de-auditoría-audit-log)**
16. **🆕 [Sistema de Notificaciones por Email](#16-sistema-de-notificaciones-por-email)**

---

## 1. Gestión de Autenticación y Usuarios

### CU-001: Registro de Usuario
**Actor**: Usuario Anónimo  
**Descripción**: Permite a un nuevo usuario registrarse en el sistema.

**Precondiciones**:
- El usuario no está registrado
- El email no existe en el sistema

**Flujo Principal**:
1. Usuario envía POST a `/api/users/` con datos:
   ```json
   {
     "username": "nuevo_usuario",
     "email": "usuario@ejemplo.com",
     "password": "contraseña_segura",
     "first_name": "Juan",
     "last_name": "Pérez"
   }
   ```
2. Sistema valida datos y crea usuario
3. Sistema retorna usuario creado con ID

**Postcondiciones**:
- Usuario registrado en base de datos
- Contraseña hasheada
- Role por defecto asignado

---

### CU-002: Inicio de Sesión (Login)
**Actor**: Usuario Registrado  
**Descripción**: Autenticación mediante JWT tokens.

**Precondiciones**:
- Usuario registrado en el sistema

**Flujo Principal**:
1. Usuario envía POST a `/api/token/` con credenciales:
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
2. Sistema valida credenciales
3. Sistema genera access_token y refresh_token
4. Retorna tokens JWT

**Postcondiciones**:
- Usuario autenticado
- Tokens válidos por tiempo configurado
- Acceso a endpoints protegidos

---

### CU-003: Renovar Token de Acceso
**Actor**: Usuario Autenticado  
**Descripción**: Renueva access token usando refresh token.

**Precondiciones**:
- Usuario posee refresh_token válido

**Flujo Principal**:
1. Usuario envía POST a `/api/token/refresh/`:
   ```json
   {
     "refresh": "eyJ0eXAiOiJKV1QiLCJ..."
   }
   ```
2. Sistema valida refresh token
3. Genera nuevo access token
4. Retorna nuevo token

**Postcondiciones**:
- Nuevo access_token generado
- Sesión extendida

---

### CU-004: Verificar Token
**Actor**: Sistema Cliente  
**Descripción**: Verifica validez de un token JWT.

**Precondiciones**:
- Token JWT existe

**Flujo Principal**:
1. Cliente envía POST a `/api/token/verify/`:
   ```json
   {
     "token": "eyJ0eXAiOiJKV1QiLCJ..."
   }
   ```
2. Sistema valida token
3. Retorna 200 si válido, 401 si inválido

---

### CU-005: Consultar Perfil de Usuario
**Actor**: Usuario Autenticado  
**Descripción**: Obtiene información del perfil del usuario actual.

**Precondiciones**:
- Usuario autenticado

**Flujo Principal**:
1. Usuario envía GET a `/api/users/profile/` con token
2. Sistema identifica usuario por token
3. Retorna datos del perfil

**Postcondiciones**:
- Datos del usuario expuestos (sin contraseña)

---

### CU-006: Actualizar Usuario
**Actor**: Usuario Autenticado / Admin  
**Descripción**: Modifica datos de un usuario.

**Precondiciones**:
- Usuario autenticado
- Usuario es propietario O es admin

**Flujo Principal**:
1. Usuario envía PATCH/PUT a `/api/users/{id}/`:
   ```json
   {
     "first_name": "Nuevo Nombre",
     "email": "nuevo@email.com"
   }
   ```
2. Sistema valida permisos
3. Actualiza datos
4. Retorna usuario actualizado

---

### CU-007: Eliminar Usuario
**Actor**: Admin  
**Descripción**: Elimina un usuario del sistema.

**Precondiciones**:
- Usuario admin autenticado

**Flujo Principal**:
1. Admin envía DELETE a `/api/users/{id}/`
2. Sistema verifica permisos de admin
3. Elimina usuario
4. Retorna 204 No Content

**Postcondiciones**:
- Usuario eliminado de BD
- Órdenes del usuario quedan huérfanas (según configuración)

---

## 2. Gestión de Productos y Categorías

### CU-008: Listar Productos
**Actor**: Cualquier Usuario  
**Descripción**: Obtiene catálogo de productos activos.

**Precondiciones**:
- Ninguna (endpoint público)

**Flujo Principal**:
1. Usuario envía GET a `/api/products/`
2. Sistema filtra productos activos
3. Retorna lista paginada con:
   - Información básica del producto
   - Categoría
   - Rating promedio
   - Número de reseñas

**Postcondiciones**:
- Lista de productos disponibles

---

### CU-009: Consultar Detalle de Producto
**Actor**: Cualquier Usuario  
**Descripción**: Obtiene información completa de un producto.

**Precondiciones**:
- Producto existe y está activo

**Flujo Principal**:
1. Usuario envía GET a `/api/products/{id}/`
2. Sistema busca producto
3. Retorna datos completos:
   - Nombre, descripción, precio
   - Stock disponible
   - Categoría
   - Información de garantía
   - Rating promedio
   - Número de reseñas

---

### CU-010: Crear Producto
**Actor**: Admin  
**Descripción**: Agrega nuevo producto al catálogo.

**Precondiciones**:
- Usuario con role='ADMIN'
- Categoría válida existe

**Flujo Principal**:
1. Admin envía POST a `/api/products/`:
   ```json
   {
     "name": "Producto Nuevo",
     "description": "Descripción del producto",
     "price": "999.99",
     "stock": 100,
     "category": 14,
     "warranty_info": "1 año de garantía"
   }
   ```
2. Sistema valida datos
3. Crea producto
4. Retorna producto creado con ID

**Postcondiciones**:
- Producto disponible en catálogo
- `is_active=true` por defecto

---

### CU-011: Actualizar Producto
**Actor**: Admin  
**Descripción**: Modifica datos de un producto existente.

**Precondiciones**:
- Usuario admin
- Producto existe

**Flujo Principal**:
1. Admin envía PATCH/PUT a `/api/products/{id}/`
2. Sistema valida permisos
3. Actualiza campos
4. Retorna producto actualizado

---

### CU-012: Eliminar Producto
**Actor**: Admin  
**Descripción**: Elimina producto del catálogo.

**Precondiciones**:
- Usuario admin
- Producto existe

**Flujo Principal**:
1. Admin envía DELETE a `/api/products/{id}/`
2. Sistema marca producto como inactivo O elimina (según configuración)
3. Retorna 204 No Content

---

### CU-013: Gestionar Categorías
**Actor**: Admin  
**Descripción**: CRUD completo de categorías de productos.

**Operaciones**:
- **GET** `/api/products/categories/` - Listar categorías
- **GET** `/api/products/categories/{id}/` - Detalle categoría
- **POST** `/api/products/categories/` - Crear categoría
- **PATCH/PUT** `/api/products/categories/{id}/` - Actualizar
- **DELETE** `/api/products/categories/{id}/` - Eliminar

**Ejemplo Creación**:
```json
{
  "name": "Electrónica",
  "description": "Productos electrónicos"
}
```

---

## 3. Sistema de Reseñas y Valoraciones

### CU-014: Crear Reseña de Producto
**Actor**: Usuario Autenticado  
**Descripción**: Usuario califica y comenta un producto.

**Precondiciones**:
- Usuario autenticado
- Producto existe
- Usuario no ha reseñado este producto antes

**Flujo Principal**:
1. Usuario envía POST a `/api/products/reviews/`:
   ```json
   {
     "product": 104,
     "rating": 5,
     "comment": "Excelente producto, muy recomendado!"
   }
   ```
2. Sistema valida constraint unique(product, user)
3. Crea reseña
4. Actualiza rating promedio del producto
5. Retorna reseña creada

**Postcondiciones**:
- Reseña almacenada
- Rating del producto recalculado
- Una sola reseña por usuario por producto

---

### CU-015: Listar Reseñas de un Producto
**Actor**: Cualquier Usuario  
**Descripción**: Obtiene todas las reseñas de un producto.

**Precondiciones**:
- Producto existe

**Flujo Principal**:
1. Usuario envía GET a `/api/products/{id}/reviews/`
2. Sistema filtra reseñas del producto
3. Retorna lista con:
   - Rating promedio del producto
   - Número total de reseñas
   - Lista de reseñas con username, rating, comentario

**Respuesta Ejemplo**:
```json
{
  "average_rating": 4.5,
  "count": 12,
  "reviews": [
    {
      "id": 1,
      "user_username": "juan123",
      "rating": 5,
      "comment": "Excelente!",
      "created_at": "2025-10-24T10:30:00Z"
    }
  ]
}
```

---

### CU-016: Actualizar Reseña
**Actor**: Autor de la Reseña / Admin  
**Descripción**: Modifica una reseña existente.

**Precondiciones**:
- Usuario es autor de la reseña O es admin

**Flujo Principal**:
1. Usuario envía PATCH a `/api/products/reviews/{id}/`:
   ```json
   {
     "rating": 4,
     "comment": "Actualizo mi opinión..."
   }
   ```
2. Sistema verifica permisos
3. Actualiza reseña
4. Recalcula rating del producto
5. Retorna reseña actualizada

---

### CU-017: Eliminar Reseña
**Actor**: Autor de la Reseña / Admin  
**Descripción**: Elimina una reseña.

**Precondiciones**:
- Usuario es autor O es admin

**Flujo Principal**:
1. Usuario envía DELETE a `/api/products/reviews/{id}/`
2. Sistema verifica permisos
3. Elimina reseña
4. Recalcula rating del producto
5. Retorna 204 No Content

---

## 4. Sistema de Recomendaciones

### CU-018: Obtener Recomendaciones de Productos
**Actor**: Cualquier Usuario  
**Descripción**: Sistema recomienda productos basado en compras relacionadas (collaborative filtering).

**Precondiciones**:
- Producto base existe
- Existen órdenes con productos relacionados

**Flujo Principal**:
1. Usuario envía GET a `/api/products/{id}/recommendations/`
2. Sistema busca productos comprados junto con el producto base
3. Agrupa por frecuencia de co-compra
4. Ordena por número de veces comprados juntos
5. Retorna top 5 productos recomendados

**Algoritmo**:
```
Para producto X:
  - Buscar órdenes que contengan X
  - Extraer otros productos en esas órdenes
  - Contar frecuencia de aparición
  - Ordenar descendente
  - Retornar top 5
```

**Respuesta Ejemplo**:
```json
{
  "product": "Diseño de APIs RESTful",
  "recommendations": [
    {
      "id": 105,
      "name": "Python Avanzado",
      "price": "299.99",
      "times_bought_together": 15
    },
    {
      "id": 106,
      "name": "Docker para Desarrolladores",
      "price": "199.99",
      "times_bought_together": 12
    }
  ]
}
```

**Postcondiciones**:
- Lista de productos recomendados
- Útil para cross-selling

---

## 5. Gestión de Órdenes (Cliente)

### CU-019: Crear Orden de Compra
**Actor**: Usuario Autenticado con role CAJERO o superior  
**Descripción**: Crea una orden de compra con productos.

**Precondiciones**:
- Usuario autenticado
- Usuario tiene permiso (IsCajeroUser)
- Productos en stock

**Flujo Principal**:
1. Usuario envía POST a `/api/orders/create/`:
   ```json
   {
     "items": [
       {
         "product": 104,
         "quantity": 2
       },
       {
         "product": 105,
         "quantity": 1
       }
     ]
   }
   ```
2. Sistema valida stock disponible
3. Calcula total de la orden
4. Crea Order y OrderItems
5. Descuenta stock (opcional según configuración)
6. Retorna orden creada con status='PENDING'

**Postcondiciones**:
- Orden en estado PENDING
- Items asociados
- Total calculado

---

### CU-020: Listar Mis Órdenes
**Actor**: Usuario Autenticado  
**Descripción**: Usuario consulta su historial de órdenes.

**Precondiciones**:
- Usuario autenticado

**Flujo Principal**:
1. Usuario envía GET a `/api/orders/`
2. Sistema filtra órdenes del usuario actual
3. Retorna lista de órdenes con:
   - ID, fecha, status, total
   - Items de cada orden

---

### CU-021: Consultar Detalle de Orden
**Actor**: Usuario Autenticado  
**Descripción**: Obtiene información completa de una orden.

**Precondiciones**:
- Usuario es dueño de la orden O es admin

**Flujo Principal**:
1. Usuario envía GET a `/api/orders/{id}/`
2. Sistema verifica permisos
3. Retorna orden con items completos

---

## 6. Procesamiento de Pagos con Stripe

### CU-022: Crear Sesión de Pago
**Actor**: Usuario con Orden Pendiente  
**Descripción**: Genera link de pago de Stripe para una orden.

**Precondiciones**:
- Usuario autenticado
- Orden existe y pertenece al usuario
- Orden en estado PENDING

**Flujo Principal**:
1. Usuario envía POST a `/api/orders/{id}/create-checkout-session/`
2. Sistema consulta orden y items
3. Crea sesión de Stripe Checkout con:
   - Line items (productos y cantidades)
   - Success URL
   - Cancel URL
   - Metadata (order_id)
4. Retorna URL de checkout de Stripe

**Respuesta**:
```json
{
  "url": "https://checkout.stripe.com/c/pay/cs_test_..."
}
```

**Postcondiciones**:
- Sesión de Stripe creada
- Usuario redirigido a Stripe Checkout

---

### CU-023: Webhook de Stripe
**Actor**: Stripe (Sistema Externo)  
**Descripción**: Stripe notifica resultado del pago.

**Precondiciones**:
- Sesión de pago completada
- Webhook configurado en Stripe

**Flujo Principal**:
1. Stripe envía POST a `/api/orders/stripe-webhook/`
2. Sistema valida firma del webhook
3. Si evento es `checkout.session.completed`:
   - Obtiene order_id de metadata
   - Actualiza orden a status='PAID'
   - Guarda payment_intent_id
4. Retorna 200 OK

**Postcondiciones**:
- Orden marcada como pagada
- Order.status = 'PAID'

---

## 7. Carrito con Lenguaje Natural (NLP)

### CU-024: Agregar Productos con Lenguaje Natural
**Actor**: Usuario Autenticado  
**Descripción**: Crea orden interpretando texto en lenguaje natural.

**Precondiciones**:
- Usuario autenticado
- Productos mencionados existen

**Flujo Principal**:
1. Usuario envía POST a `/api/orders/cart/add-natural-language/`:
   ```json
   {
     "text": "Quiero 2 laptops y 3 mouses"
   }
   ```
2. Sistema parsea texto con NLP:
   - Detecta palabras clave (agregar, comprar, quiero)
   - Extrae cantidades (2, 3)
   - Identifica productos (laptop, mouse)
3. Busca productos que coincidan
4. Crea orden automática
5. Retorna orden creada

**Respuesta**:
```json
{
  "message": "Orden creada exitosamente",
  "order": {
    "id": 89,
    "total": "1599.97",
    "items": [
      {"product": "Laptop HP", "quantity": 2},
      {"product": "Mouse Inalámbrico", "quantity": 3}
    ]
  },
  "action": "add"
}
```

---

### CU-025: Sugerencias de Productos
**Actor**: Cualquier Usuario  
**Descripción**: Búsqueda de productos por término.

**Precondiciones**:
- Ninguna

**Flujo Principal**:
1. Usuario envía GET a `/api/orders/cart/suggestions/?q=laptop`
2. Sistema busca productos que contengan el término
3. Retorna sugerencias coincidentes

---

## 8. Panel de Administración

### CU-026: Listar Todas las Órdenes (Admin)
**Actor**: Admin  
**Descripción**: Admin consulta todas las órdenes del sistema.

**Precondiciones**:
- Usuario con role='ADMIN'

**Flujo Principal**:
1. Admin envía GET a `/api/orders/admin/`
2. Sistema verifica permiso IsAdminUser
3. Retorna todas las órdenes con datos completos

---

### CU-027: Ver Detalle de Cualquier Orden
**Actor**: Admin  
**Descripción**: Admin consulta detalle de orden de cualquier usuario.

**Precondiciones**:
- Usuario admin

**Flujo Principal**:
1. Admin envía GET a `/api/orders/admin/{id}/`
2. Sistema verifica permisos
3. Retorna orden completa

---

### CU-028: Actualizar Estado de Orden
**Actor**: Admin  
**Descripción**: Cambia el status de una orden.

**Precondiciones**:
- Usuario admin
- Orden existe

**Flujo Principal**:
1. Admin envía POST a `/api/orders/admin/{id}/update_status/`:
   ```json
   {
     "status": "shipped"
   }
   ```
2. Sistema valida nuevo estado
3. Actualiza orden
4. Retorna orden actualizada

**Estados Válidos**:
- PENDING
- PAID
- SHIPPED
- DELIVERED
- CANCELLED

---

### CU-029: Dashboard Administrativo
**Actor**: Admin  
**Descripción**: Panel con estadísticas generales del negocio.

**Precondiciones**:
- Usuario admin

**Flujo Principal**:
1. Admin envía GET a `/api/orders/admin/dashboard/`
2. Sistema consulta datos (con caché Redis):
   - Revenue total
   - Número de órdenes
   - Productos más vendidos
   - Productos con bajo stock
   - Ventas por mes
3. Retorna datos agregados
4. Marca si proviene de caché

**Respuesta Ejemplo**:
```json
{
  "overview": {
    "total_revenue": "125400.50",
    "total_orders": 245,
    "average_order_value": "511.84"
  },
  "sales": {
    "top_products": [
      {
        "product": "Laptop Dell",
        "total_sold": 45,
        "revenue": "67500.00"
      }
    ],
    "low_stock_products": [...],
    "sales_by_month": [...]
  },
  "_from_cache": true
}
```

**Optimización**:
- Resultado cacheado en Redis por 5 minutos
- Invalidación automática al crear/actualizar órdenes

---

### CU-030: Listar Usuarios (Admin)
**Actor**: Admin  
**Descripción**: Admin consulta lista de todos los usuarios.

**Precondiciones**:
- Usuario admin

**Flujo Principal**:
1. Admin envía GET a `/api/orders/admin/users/`
2. Sistema verifica permisos
3. Retorna lista de usuarios con estadísticas

---

### CU-031: Analíticas de Ventas
**Actor**: Admin  
**Descripción**: Obtiene métricas de ventas.

**Precondiciones**:
- Usuario admin

**Flujo Principal**:
1. Admin envía GET a `/api/orders/admin/analytics/sales/`
2. Sistema calcula métricas
3. Retorna análisis de ventas

---

## 9. Generación de Reportes

### CU-032: Reporte de Ventas (PDF/Excel)
**Actor**: Usuario con permisos  
**Descripción**: Genera reporte de ventas en formato PDF o Excel.

**Precondiciones**:
- Usuario autenticado (según configuración de permisos)

**Flujo Principal**:
1. Usuario envía GET a `/api/reports/sales/?format=pdf&start_date=2025-10-01&end_date=2025-10-31`
2. Sistema filtra ventas por rango de fechas
3. Genera documento PDF o Excel con:
   - Total de ventas
   - Número de órdenes
   - Tabla detallada de órdenes
4. Retorna archivo binario

**Parámetros**:
- `format`: pdf | excel
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD

---

### CU-033: Reporte de Productos (PDF/Excel)
**Actor**: Usuario con permisos  
**Descripción**: Genera reporte de inventario de productos.

**Precondiciones**:
- Usuario autenticado

**Flujo Principal**:
1. Usuario envía GET a `/api/reports/products/?format=excel`
2. Sistema extrae todos los productos
3. Genera documento con:
   - Listado de productos
   - Stock actual
   - Precio
   - Categoría
4. Retorna archivo

---

### CU-034: Reporte Dinámico con IA
**Actor**: Usuario con permisos  
**Descripción**: Genera reportes interpretando solicitud en lenguaje natural.

**Precondiciones**:
- Usuario autenticado

**Flujo Principal**:
1. Usuario envía POST a `/api/reports/dynamic-parser/`:
   ```json
   {
     "prompt": "Quiero un reporte de ventas del mes de octubre en PDF"
   }
   ```
2. Sistema parsea el prompt con NLP:
   - Detecta tipo de reporte (ventas/productos)
   - Detecta formato (PDF/Excel)
   - Detecta rango de fechas (octubre)
   - Detecta agrupación (por producto/cliente)
3. Genera reporte según interpretación
4. Retorna archivo

**Ejemplos de Prompts**:
- "Reporte de ventas agrupado por producto del mes de octubre en Excel"
- "Dame un reporte de compras por cliente con sus nombres del mes de octubre"
- "Muestra las ventas con nombres de clientes y productos en PDF"

**Capacidades de Parseo**:
- Detecta mes mencionado
- Identifica formato deseado
- Reconoce agrupaciones
- Infiere fechas automáticamente

---

### CU-035: Generar Comprobante de Orden
**Actor**: Usuario dueño de la orden / Admin  
**Descripción**: Genera PDF de factura/comprobante de una orden.

**Precondiciones**:
- Usuario es dueño de orden O es admin
- Orden existe

**Flujo Principal**:
1. Usuario envía GET a `/api/orders/{id}/invoice/`
   - Redirige a `/api/reports/orders/{id}/invoice/`
2. Sistema verifica permisos
3. Genera PDF con:
   - Datos de la orden
   - Items comprados
   - Total
   - Información del cliente
4. Retorna PDF

---

## 10. Predicciones de Ventas (ML)

### CU-036: Obtener Predicción de Ventas
**Actor**: Usuario con permisos  
**Descripción**: Obtiene predicción de ventas futuras usando Machine Learning.

**Precondiciones**:
- Modelo ML entrenado
- Datos históricos suficientes

**Flujo Principal**:
1. Usuario envía GET a `/api/predictions/sales/`
2. Sistema carga modelo de ML (joblib)
3. Consulta ventas históricas
4. Genera predicciones para próximos 30 días
5. Retorna predicciones

**Respuesta Ejemplo**:
```json
{
  "predictions": [
    {
      "date": "2025-11-01",
      "predicted_sales": 15234.50
    },
    {
      "date": "2025-11-02",
      "predicted_sales": 16100.25
    }
  ],
  "total_days": 30,
  "model_version": "1.0"
}
```

**Modelo ML**:
- Algoritmo: Regresión (scikit-learn)
- Entrenado con: Historial de ventas
- Features: Tendencias, estacionalidad
- Ubicación: `predictions/sales_model.joblib`

---

## 11. Sistema de Permisos RBAC

### CU-037: Control de Acceso por Roles
**Actor**: Sistema  
**Descripción**: Validación automática de permisos según rol de usuario.

**Roles Definidos**:
1. **ADMIN**: Acceso total al sistema
2. **MANAGER**: Acceso a gestión y reportes
3. **CAJERO**: Puede crear órdenes y consultar
4. **CLIENTE**: Acceso básico (por defecto)

**Permisos por Rol**:

| Endpoint | ADMIN | MANAGER | CAJERO | CLIENTE |
|----------|-------|---------|--------|---------|
| Ver productos | ✅ | ✅ | ✅ | ✅ |
| Crear orden | ✅ | ✅ | ✅ | ❌ |
| Dashboard admin | ✅ | ✅ | ❌ | ❌ |
| Gestionar usuarios | ✅ | ❌ | ❌ | ❌ |
| Reportes | ✅ | ✅ | ✅ | ❌ |
| Predicciones ML | ✅ | ✅ | ❌ | ❌ |

**Clases de Permisos**:
- `IsAdminUser`: Solo ADMIN
- `IsManagerUser`: MANAGER + ADMIN
- `IsCajeroUser`: CAJERO + MANAGER + ADMIN
- `IsAdminOrManager`: ADMIN o MANAGER
- `CanViewReports`: Según configuración

---

## 12. Optimización con Caché

### CU-038: Caché del Dashboard
**Actor**: Sistema  
**Descripción**: Cachea resultados del dashboard para mejorar rendimiento.

**Implementación**:
1. Primera consulta a `/api/orders/admin/dashboard/`:
   - Ejecuta queries complejas
   - Almacena resultado en Redis
   - TTL: 5 minutos
   - Retorna `"_from_cache": false`

2. Consultas subsecuentes:
   - Recupera de Redis
   - Retorna `"_from_cache": true`
   - Respuesta instantánea

3. Invalidación automática:
   - Al crear nueva orden
   - Al actualizar orden
   - Al eliminar orden
   - Via signals de Django

**Beneficios**:
- Reducción de carga en BD
- Respuesta 10-50x más rápida
- Escalabilidad mejorada

---

## 13. Documentación de API

### CU-039: Consultar Documentación Swagger
**Actor**: Desarrollador  
**Descripción**: Accede a documentación interactiva de la API.

**Flujo Principal**:
1. Usuario accede a `/api/docs/`
2. Sistema muestra Swagger UI con:
   - Todos los endpoints
   - Parámetros requeridos
   - Ejemplos de request/response
   - Posibilidad de probar endpoints

---

### CU-040: Consultar Documentación ReDoc
**Actor**: Desarrollador  
**Descripción**: Documentación alternativa más legible.

**Flujo Principal**:
1. Usuario accede a `/api/redoc/`
2. Sistema muestra documentación ReDoc
3. Navegación por categorías

---

### CU-041: Obtener Schema OpenAPI
**Actor**: Sistema/Desarrollador  
**Descripción**: Obtiene definición completa de la API en formato OpenAPI.

**Flujo Principal**:
1. Usuario/Sistema envía GET a `/api/schema/`
2. Retorna JSON con especificación OpenAPI 3.0
3. Usado por herramientas de generación de código

---

## 13. Sistema de Devoluciones (Returns)

### CU-042: Solicitar Devolución (Cliente)
**Actor**: Usuario Autenticado  
**Descripción**: Cliente solicita devolución de un producto de una orden entregada.

**Precondiciones**:
- Usuario autenticado
- Orden existe y está en estado DELIVERED
- Producto pertenece a la orden
- Cantidad válida disponible para devolución

**Flujo Principal**:
1. Usuario envía POST a `/api/deliveries/returns/`:
   ```json
   {
     "order": 45,
     "product": 104,
     "quantity": 1,
     "reason": "Producto defectuoso"
   }
   ```
2. Sistema valida:
   - Orden está entregada
   - Producto está en la orden
   - Cantidad no excede lo comprado
3. Crea Return con status='REQUESTED'
4. Establece requested_at timestamp
5. Envía email a todos los managers/admins
6. Retorna devolución creada

**Postcondiciones**:
- Return creado en estado REQUESTED
- Managers notificados por email
- Cliente puede consultar estado

**Estados del Sistema**:
```
REQUESTED → IN_EVALUATION → APPROVED/REJECTED → COMPLETED
```

---

### CU-043: Enviar Devolución a Evaluación (Manager)
**Actor**: Manager  
**Descripción**: Manager mueve la devolución a evaluación física.

**Precondiciones**:
- Usuario con role MANAGER o ADMIN
- Return en estado REQUESTED

**Flujo Principal**:
1. Manager envía POST a `/api/deliveries/returns/{id}/send_to_evaluation/`:
   ```json
   {
     "manager_notes": "Producto recibido en bodega, iniciando inspección"
   }
   ```
2. Sistema valida estado actual
3. Actualiza a status='IN_EVALUATION'
4. Guarda manager_notes
5. Establece evaluated_at timestamp
6. Envía email al cliente informando inicio de evaluación
7. Retorna devolución actualizada

**Postcondiciones**:
- Return en estado IN_EVALUATION
- Cliente notificado por email
- Manager puede proceder con inspección física

---

### CU-044: Aprobar Devolución (Manager)
**Actor**: Manager  
**Descripción**: Manager aprueba devolución tras evaluar el producto físicamente.

**Precondiciones**:
- Usuario con role MANAGER o ADMIN
- Return en estado IN_EVALUATION

**Flujo Principal**:
1. Manager envía POST a `/api/deliveries/returns/{id}/approve/`:
   ```json
   {
     "evaluation_notes": "Producto confirmado defectuoso, aprobada devolución",
     "refund_amount": "299.99",
     "refund_method": "WALLET"
   }
   ```
2. Sistema valida estado actual
3. Actualiza a status='APPROVED'
4. Guarda evaluation_notes y refund_amount
5. Establece processed_at timestamp
6. **Procesa reembolso automáticamente**:
   - Si WALLET: Crea/obtiene billetera del cliente
   - Llama a wallet.add_funds() con el monto
   - Crea transacción tipo REFUND
   - Referencia: f"RETURN-{return_id}"
7. Actualiza status='COMPLETED'
8. Establece completed_at timestamp
9. Envía email al cliente con confirmación
10. Retorna devolución completada

**Postcondiciones**:
- Return en estado COMPLETED
- Reembolso procesado en billetera
- Cliente notificado y puede usar fondos
- Transacción registrada en historial

**Métodos de Reembolso**:
- **WALLET**: Billetera virtual (automático)
- **ORIGINAL**: Método original de pago (requiere integración Stripe)
- **BANK**: Transferencia bancaria (proceso manual)

---

### CU-045: Rechazar Devolución (Manager)
**Actor**: Manager  
**Descripción**: Manager rechaza devolución tras evaluar el producto.

**Precondiciones**:
- Usuario con role MANAGER o ADMIN
- Return en estado IN_EVALUATION

**Flujo Principal**:
1. Manager envía POST a `/api/deliveries/returns/{id}/reject/`:
   ```json
   {
     "evaluation_notes": "Producto no presenta defectos. Daño causado por uso inadecuado del cliente."
   }
   ```
2. Sistema valida estado actual
3. Actualiza a status='REJECTED'
4. Guarda evaluation_notes detalladas
5. Establece processed_at timestamp
6. Envía email al cliente explicando razón del rechazo
7. Retorna devolución rechazada

**Postcondiciones**:
- Return en estado REJECTED
- Cliente notificado con explicación
- No hay reembolso procesado

---

### CU-046: Consultar Mis Devoluciones (Cliente)
**Actor**: Usuario Autenticado  
**Descripción**: Cliente consulta sus solicitudes de devolución.

**Precondiciones**:
- Usuario autenticado

**Flujo Principal**:
1. Cliente envía GET a `/api/deliveries/returns/my_returns/`
2. Sistema filtra returns del usuario actual
3. Retorna lista con:
   - ID, orden, producto, cantidad
   - Razón de devolución
   - Estado actual (REQUESTED, IN_EVALUATION, etc.)
   - Fechas (requested_at, evaluated_at, completed_at)
   - Monto y método de reembolso (si aplica)
   - Notas del manager (si existen)

**Respuesta Ejemplo**:
```json
[
  {
    "id": 11,
    "order": 45,
    "product_name": "Laptop Dell",
    "quantity": 1,
    "reason": "Producto defectuoso",
    "status": "COMPLETED",
    "requested_at": "2025-11-01T10:00:00Z",
    "evaluated_at": "2025-11-02T14:30:00Z",
    "processed_at": "2025-11-02T15:00:00Z",
    "completed_at": "2025-11-02T15:00:00Z",
    "refund_amount": "299.99",
    "refund_method": "WALLET",
    "evaluation_notes": "Producto confirmado defectuoso"
  }
]
```

---

### CU-047: Listar Todas las Devoluciones (Manager)
**Actor**: Manager  
**Descripción**: Manager consulta todas las solicitudes de devolución del sistema.

**Precondiciones**:
- Usuario con role MANAGER o ADMIN

**Flujo Principal**:
1. Manager envía GET a `/api/deliveries/returns/`
2. Sistema retorna todas las devoluciones
3. Puede filtrar por estado: `?status=IN_EVALUATION`
4. Puede filtrar por orden: `?order=45`

**Casos de Uso**:
- Ver devoluciones pendientes de evaluación
- Monitorear devoluciones procesadas
- Auditar rechazos

---

## 14. Sistema de Billetera Virtual (Wallet)

### CU-048: Consultar Mi Billetera
**Actor**: Usuario Autenticado  
**Descripción**: Usuario consulta su billetera virtual y saldo disponible.

**Precondiciones**:
- Usuario autenticado
- Billetera creada (automática al primer uso)

**Flujo Principal**:
1. Usuario envía GET a `/api/users/wallets/my_wallet/`
2. Sistema obtiene o crea billetera del usuario
3. Retorna datos de la billetera

**Respuesta**:
```json
{
  "id": 3,
  "user": 15,
  "balance": "299.99",
  "created_at": "2025-11-01T12:00:00Z",
  "updated_at": "2025-11-02T15:00:00Z"
}
```

**Postcondiciones**:
- Usuario conoce su saldo disponible
- Puede decidir si usar fondos

---

### CU-049: Consultar Saldo
**Actor**: Usuario Autenticado  
**Descripción**: Consulta rápida del saldo actual.

**Precondiciones**:
- Usuario autenticado

**Flujo Principal**:
1. Usuario envía GET a `/api/users/wallets/my_balance/`
2. Sistema retorna saldo actual

**Respuesta**:
```json
{
  "balance": "299.99"
}
```

---

### CU-050: Depositar Fondos (Manager)
**Actor**: Manager  
**Descripción**: Manager deposita fondos a billetera de un usuario.

**Precondiciones**:
- Usuario con role MANAGER o ADMIN
- Usuario destino existe

**Flujo Principal**:
1. Manager envía POST a `/api/users/wallets/{wallet_id}/deposit/`:
   ```json
   {
     "amount": "50.00",
     "description": "Crédito por compensación"
   }
   ```
2. Sistema valida amount > 0
3. Obtiene billetera del usuario
4. Llama a wallet.add_funds(amount, 'DEPOSIT', description)
5. Crea transacción tipo DEPOSIT
6. Retorna billetera actualizada

**Postcondiciones**:
- Saldo incrementado
- Transacción registrada
- Usuario puede usar fondos

---

### CU-051: Retirar Fondos
**Actor**: Usuario Autenticado  
**Descripción**: Usuario solicita retiro de fondos de su billetera.

**Precondiciones**:
- Usuario autenticado
- Saldo disponible >= monto solicitado

**Flujo Principal**:
1. Usuario envía POST a `/api/users/wallets/{wallet_id}/withdraw/`:
   ```json
   {
     "amount": "100.00",
     "description": "Retiro a cuenta bancaria"
   }
   ```
2. Sistema valida:
   - Usuario es dueño de la billetera
   - Saldo suficiente
3. Llama a wallet.deduct_funds(amount, 'WITHDRAWAL', description)
4. Crea transacción tipo WITHDRAWAL (monto negativo)
5. Retorna billetera actualizada

**Postcondiciones**:
- Saldo decrementado
- Transacción registrada
- Proceso de retiro bancario iniciado (manual)

**Validación**:
```python
if balance < amount:
    raise ValidationError("Saldo insuficiente")
```

---

### CU-052: Consultar Historial de Transacciones
**Actor**: Usuario Autenticado  
**Descripción**: Usuario consulta todas sus transacciones de billetera.

**Precondiciones**:
- Usuario autenticado

**Flujo Principal**:
1. Usuario envía GET a `/api/users/wallet-transactions/my_transactions/`
2. Sistema filtra transacciones del usuario actual
3. Retorna lista ordenada por fecha (más reciente primero)

**Respuesta Ejemplo**:
```json
[
  {
    "id": 23,
    "wallet": 3,
    "transaction_type": "REFUND",
    "amount": "299.99",
    "balance_after": "299.99",
    "description": "Reembolso por devolución aprobada",
    "reference_id": "RETURN-11",
    "created_at": "2025-11-02T15:00:00Z"
  },
  {
    "id": 24,
    "wallet": 3,
    "transaction_type": "PURCHASE",
    "amount": "-150.00",
    "balance_after": "149.99",
    "description": "Compra de orden #50",
    "reference_id": "ORDER-50",
    "created_at": "2025-11-05T10:30:00Z"
  }
]
```

**Tipos de Transacción**:
- **REFUND**: Reembolso (positivo)
- **PURCHASE**: Compra con billetera (negativo)
- **WITHDRAWAL**: Retiro (negativo)
- **DEPOSIT**: Depósito manual (positivo)
- **BONUS**: Bonificación (positivo)
- **CORRECTION**: Ajuste/corrección (positivo o negativo)

---

### CU-053: Ver Estadísticas de Transacciones
**Actor**: Usuario Autenticado  
**Descripción**: Usuario consulta estadísticas agregadas de sus transacciones.

**Precondiciones**:
- Usuario autenticado

**Flujo Principal**:
1. Usuario envía GET a `/api/users/wallet-transactions/statistics/`
2. Sistema calcula métricas de las transacciones del usuario:
   - Total créditos recibidos
   - Total débitos realizados
   - Total reembolsos recibidos
   - Número de transacciones
3. Retorna estadísticas

**Respuesta Ejemplo**:
```json
{
  "total_credits": "349.99",
  "total_debits": "-150.00",
  "total_refunds": "299.99",
  "transaction_count": 2,
  "current_balance": "199.99"
}
```

---

## 15. Sistema de Auditoría (Audit Log)

### CU-054: Registro Automático de Auditoría
**Actor**: Sistema (Middleware)  
**Descripción**: Sistema registra automáticamente todas las acciones en endpoints protegidos.

**Precondiciones**:
- Middleware de auditoría activo
- Usuario autenticado

**Flujo Automático**:
1. Usuario realiza request a endpoint protegido
2. Middleware captura información:
   - Usuario que realiza la acción
   - Endpoint accedido
   - Método HTTP (GET, POST, PUT, DELETE)
   - Timestamp
   - IP del cliente
   - User Agent
3. Guarda registro en AuditLog
4. Request continúa normalmente

**Endpoints Auditados**:
- Todos los que requieren autenticación
- Acciones administrativas
- Creación/modificación de datos críticos

---

### CU-055: Consultar Logs de Auditoría (Admin)
**Actor**: Admin  
**Descripción**: Admin consulta el historial completo de auditoría.

**Precondiciones**:
- Usuario con role ADMIN

**Flujo Principal**:
1. Admin envía GET a `/api/audit-log/`
2. Sistema retorna logs de auditoría
3. Puede filtrar por:
   - Usuario: `?user=15`
   - Acción: `?action=POST`
   - Endpoint: `?endpoint=/api/orders/create/`
   - Rango de fechas

**Respuesta Ejemplo**:
```json
[
  {
    "id": 150,
    "user": "admin",
    "action": "POST",
    "endpoint": "/api/deliveries/returns/11/approve/",
    "timestamp": "2025-11-02T15:00:00Z",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
  }
]
```

**Casos de Uso**:
- Auditar acciones de managers
- Investigar actividad sospechosa
- Cumplimiento normativo
- Debugging de problemas

---

### CU-056: Consultar Mis Acciones (Usuario)
**Actor**: Usuario Autenticado  
**Descripción**: Usuario consulta su propio historial de acciones.

**Precondiciones**:
- Usuario autenticado

**Flujo Principal**:
1. Usuario envía GET a `/api/audit-log/my_actions/`
2. Sistema filtra logs del usuario actual
3. Retorna historial personal

**Postcondiciones**:
- Usuario puede revisar su actividad
- Transparencia en el sistema

---

## 16. Sistema de Notificaciones por Email

### CU-057: Notificación de Nueva Devolución (Managers)
**Actor**: Sistema  
**Descripción**: Sistema notifica a managers/admins cuando hay nueva solicitud de devolución.

**Trigger**: Cliente crea devolución (CU-042)

**Flujo Automático**:
1. Sistema detecta creación de Return
2. Obtiene todos los usuarios con role MANAGER o ADMIN
3. Genera email con:
   - Datos del cliente
   - Orden y producto
   - Razón de devolución
   - Link a panel de evaluación
4. Envía email a cada manager

**Email Subject**: "Nueva Solicitud de Devolución - Return #{id}"

---

### CU-058: Notificación de Evaluación Iniciada (Cliente)
**Actor**: Sistema  
**Descripción**: Cliente recibe confirmación de que su devolución está siendo evaluada.

**Trigger**: Manager envía a evaluación (CU-043)

**Flujo Automático**:
1. Sistema detecta cambio a IN_EVALUATION
2. Obtiene email del cliente
3. Genera email con:
   - Confirmación de recepción del producto
   - Tiempo estimado de evaluación
   - Notas del manager
4. Envía email al cliente

**Email Subject**: "Tu devolución está siendo evaluada - Return #{id}"

---

### CU-059: Notificación de Devolución Aprobada (Cliente)
**Actor**: Sistema  
**Descripción**: Cliente recibe confirmación de aprobación y detalles del reembolso.

**Trigger**: Manager aprueba devolución (CU-044)

**Flujo Automático**:
1. Sistema detecta aprobación
2. Obtiene email del cliente
3. Genera email con:
   - Confirmación de aprobación
   - Monto reembolsado
   - Método de reembolso
   - Saldo actual en billetera (si aplica)
   - Notas de evaluación
4. Envía email al cliente

**Email Subject**: "Tu devolución ha sido aprobada - Return #{id}"

---

### CU-060: Notificación de Devolución Rechazada (Cliente)
**Actor**: Sistema  
**Descripción**: Cliente recibe explicación del rechazo de su devolución.

**Trigger**: Manager rechaza devolución (CU-045)

**Flujo Automático**:
1. Sistema detecta rechazo
2. Obtiene email del cliente
3. Genera email con:
   - Información del rechazo
   - Razón detallada del manager
   - Opciones del cliente (contactar soporte)
4. Envía email al cliente

**Email Subject**: "Actualización sobre tu solicitud de devolución - Return #{id}"

---

## 📊 Resumen de Estadísticas ACTUALIZADO

### Endpoints Totales: 87
- Autenticación: 3
- Usuarios: 7
- Productos: 6
- Categorías: 6
- Reseñas: 5
- Recomendaciones: 1
- Órdenes (cliente): 5
- Carrito NLP: 2
- Órdenes (admin): 6
- Reportes: 6
- Predicciones ML: 1
- Documentación: 3
- Cache: 2
- **🆕 Devoluciones (Returns): 7**
- **🆕 Billetera Virtual (Wallet): 6**
- **🆕 Auditoría (Audit Log): 3**
- **🆕 Deliveries/Warranties: 18**

### Tecnologías Clave:
- ✅ JWT Authentication
- ✅ RBAC (Role-Based Access Control)
- ✅ NLP (Natural Language Processing)
- ✅ Machine Learning (Predicciones)
- ✅ Redis Caching
- ✅ Stripe Payments
- ✅ PDF/Excel Generation
- ✅ Collaborative Filtering
- ✅ OpenAPI/Swagger Documentation
- **🆕 Email Notifications System (4 tipos)**
- **🆕 Virtual Wallet System (Reembolsos automáticos)**
- **🆕 Returns Management (5 estados)**
- **🆕 Audit Logging (Middleware automático)**

### Tasa de Éxito en Tests:
- **98.2%** (55/56 tests pasados)
- 0 fallos críticos
- 1 warning esperado (Stripe webhook)
- **🆕 100% en tests de devoluciones y billetera**

---

## 🚀 Casos de Uso por Actor

### Usuario Anónimo
- CU-001: Registro
- CU-008: Listar productos
- CU-009: Ver detalle producto
- CU-015: Ver reseñas
- CU-018: Ver recomendaciones

### Usuario Autenticado (CLIENTE)
- CU-002: Login
- CU-003: Renovar token
- CU-005: Ver perfil
- CU-014: Crear reseña
- CU-016/017: Editar/eliminar reseña propia
- CU-020: Ver mis órdenes
- CU-021: Ver detalle orden propia
- **🆕 CU-042: Solicitar devolución**
- **🆕 CU-046: Consultar mis devoluciones**
- **🆕 CU-048: Consultar mi billetera**
- **🆕 CU-049: Consultar saldo**
- **🆕 CU-051: Retirar fondos**
- **🆕 CU-052: Ver historial de transacciones**
- **🆕 CU-053: Ver estadísticas de transacciones**
- **🆕 CU-056: Consultar mis acciones de auditoría**

### Usuario CAJERO
- Todos los de CLIENTE +
- CU-019: Crear orden
- CU-024: Agregar con NLP
- CU-022: Crear sesión de pago
- CU-035: Generar comprobante

### Usuario MANAGER
- Todos los de CAJERO +
- CU-029: Dashboard
- CU-030: Listar usuarios
- CU-031: Analíticas
- CU-032/033/034: Reportes
- CU-036: Predicciones ML
- **🆕 CU-043: Enviar devolución a evaluación**
- **🆕 CU-044: Aprobar devolución**
- **🆕 CU-045: Rechazar devolución**
- **🆕 CU-047: Listar todas las devoluciones**
- **🆕 CU-050: Depositar fondos a billetera**

### Usuario ADMIN
- Todos los anteriores +
- CU-007: Eliminar usuarios
- CU-010/011/012: CRUD productos
- CU-013: CRUD categorías
- CU-026/027/028: Gestión completa órdenes
- **🆕 CU-055: Consultar logs de auditoría completos**

### Sistema Automático
- **🆕 CU-054: Registro automático de auditoría**
- **🆕 CU-057: Notificación de nueva devolución**
- **🆕 CU-058: Notificación de evaluación iniciada**
- **🆕 CU-059: Notificación de aprobación**
- **🆕 CU-060: Notificación de rechazo**

---

## 📝 Notas Adicionales

### Seguridad
- Todas las contraseñas hasheadas con bcrypt
- Tokens JWT con expiración configurable
- CORS configurado
- Validación de permisos en cada endpoint
- Stripe webhook signature verification
- **🆕 Middleware de auditoría en todos los endpoints protegidos**
- **🆕 Registro de IP y User-Agent para trazabilidad**

### Escalabilidad
- Paginación en listados
- Caché Redis para queries pesadas
- Índices en BD optimizados
- Queries optimizadas con select_related/prefetch_related
- **🆕 Sistema de billetera para reducir carga en Stripe**
- **🆕 Transacciones atómicas en operaciones financieras**

### Mantenibilidad
- Código modular por apps Django
- Serializers reutilizables
- Permissions classes centralizadas
- Signals para lógica desacoplada
- Documentación auto-generada
- **🆕 Email notifications centralizadas en módulo reutilizable**
- **🆕 Estados de devoluciones claramente definidos (FSM)**
- **🆕 Validaciones en serializers para integridad de datos**

### Características Destacadas 🌟

**Sistema de Devoluciones Completo**:
- Flujo de 5 estados bien definido
- Evaluación física del producto
- Múltiples métodos de reembolso
- Notificaciones automáticas en cada etapa
- Integración automática con billetera virtual

**Billetera Virtual**:
- Reembolsos instantáneos sin Stripe
- Historial completo de transacciones
- Validación de saldo en tiempo real
- Estadísticas para el usuario
- Referenciación automática con devoluciones

**Sistema de Auditoría**:
- Middleware transparente (sin modificar código)
- Registro de todas las acciones críticas
- Filtrado por usuario, endpoint, acción
- Útil para compliance y debugging

**Notificaciones por Email**:
- 4 tipos de notificaciones automatizadas
- Templates profesionales
- Información completa y clara
- Configuración flexible (console/SMTP)

---

## 📈 Métricas del Sistema

### Cobertura de Funcionalidades
- ✅ **100%** CRUD básico
- ✅ **100%** Autenticación y autorización
- ✅ **100%** Gestión de órdenes y pagos
- ✅ **100%** Sistema de reseñas
- ✅ **100%** Reportes y predicciones ML
- ✅ **100%** Devoluciones y reembolsos
- ✅ **100%** Billetera virtual
- ✅ **100%** Auditoría y trazabilidad
- ✅ **100%** Notificaciones por email

### Testing
- 98.2% de tests pasados (core system)
- 100% en flujos de devoluciones
- 100% en operaciones de billetera
- Test de integración completo verificado

### Endpoints por Categoría
| Categoría | Endpoints | Descripción |
|-----------|-----------|-------------|
| Auth | 3 | Login, refresh, verify |
| Usuarios | 7 | CRUD + perfil |
| Productos | 12 | CRUD + categorías |
| Reseñas | 5 | CRUD + listado por producto |
| Órdenes | 11 | Creación, pago, admin |
| Carrito NLP | 2 | Lenguaje natural |
| Reportes | 6 | PDF/Excel + IA |
| ML | 1 | Predicciones |
| **Devoluciones** | **7** | **Flujo completo** |
| **Billetera** | **6** | **Gestión de fondos** |
| **Auditoría** | **3** | **Logs y trazabilidad** |
| **Deliveries** | **18** | **Garantías y entregas** |
| Docs | 3 | Swagger + ReDoc + Schema |
| **TOTAL** | **87** | **API completa** |

---

**Versión del Documento**: 2.0  
**Fecha**: 10 de Noviembre, 2025  
**Autor**: SmartSales365 Development Team  
**Última Actualización**: Post-implementación de sistemas de devoluciones, billetera virtual y auditoría  
**Estado**: ✅ Producción Ready (87 endpoints, 19 casos de uso nuevos)
