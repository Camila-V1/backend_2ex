# 🎭 Funcionalidades del Sistema por Rol

Este documento describe todas las funcionalidades disponibles en el sistema, organizadas por rol de usuario.

---

## 📋 Índice
- [🔐 Jerarquía de Roles](#-jerarquía-de-roles)
- [👤 CLIENTE](#-cliente)
- [👔 MANAGER](#-manager)
- [⚙️ ADMIN](#️-admin)
- [📊 Tabla Comparativa](#-tabla-comparativa)
- [🔄 Flujos de Trabajo](#-flujos-de-trabajo)
- [🔒 Restricciones de Seguridad](#-restricciones-de-seguridad)

---

## 🔐 Jerarquía de Roles

```
ADMIN (Máximo poder)
  ↓
MANAGER (Gestión de devoluciones)
  ↓
CLIENTE (Usuario básico)
```

**Herencia de permisos**: Cada rol superior tiene **todos** los permisos de los roles inferiores más sus propias funcionalidades exclusivas.

---

## 👤 CLIENTE

### 🎯 Rol: Usuario Básico del E-commerce

**Credenciales de ejemplo**:
- Usuario: `juan_cliente`
- Contraseña: `password123`

### 📌 Funcionalidades Disponibles

#### 1️⃣ **Autenticación**

| Funcionalidad | Endpoint | Método | Descripción |
|---------------|----------|--------|-------------|
| 🔓 Iniciar sesión | `/api/users/login/` | POST | Login con username/password |
| 🔄 Refrescar token | `/api/users/refresh/` | POST | Obtener nuevo access token |
| 👤 Ver mi perfil | `/api/users/me/` | GET | Información del usuario logueado |
| 🚪 Cerrar sesión | Frontend | - | Eliminar tokens locales |

**Ejemplo de uso**:
```bash
POST /api/users/login/
{
    "username": "juan_cliente",
    "password": "password123"
}
# Respuesta: { "access": "...", "refresh": "...", "user": {...} }
```

---

#### 2️⃣ **Productos y Categorías**

| Funcionalidad | Endpoint | Método | Descripción |
|---------------|----------|--------|-------------|
| 📦 Ver catálogo | `/api/products/` | GET | Listado completo de productos |
| 🔍 Ver detalle | `/api/products/{id}/` | GET | Información detallada del producto |
| 🏷️ Ver categorías | `/api/categories/` | GET | Listado de categorías |
| 🔎 Filtrar productos | `/api/products/?category=X` | GET | Productos por categoría |
| 💰 Ordenar por precio | `/api/products/?ordering=price` | GET | Orden ascendente/descendente |

**Ejemplo de uso**:
```bash
GET /api/products/
# Ver productos de Smartphones
GET /api/products/?category=3

# Ver producto específico
GET /api/products/5/
```

---

#### 3️⃣ **Gestión de Órdenes**

| Funcionalidad | Endpoint | Método | Descripción |
|---------------|----------|--------|-------------|
| 🛒 Crear orden | `/api/orders/` | POST | Nueva orden de compra |
| 📋 Ver mis órdenes | `/api/orders/my_orders/` | GET | Historial de compras |
| 📄 Detalle de orden | `/api/orders/{id}/` | GET | Información completa de una orden |
| 🔍 Filtrar órdenes | `/api/orders/my_orders/?status=DELIVERED` | GET | Por estado |

**Ejemplo de uso**:
```bash
# Crear nueva orden
POST /api/orders/
{
    "items": [
        {"product_id": 5, "quantity": 1},
        {"product_id": 8, "quantity": 2}
    ]
}

# Ver mis órdenes
GET /api/orders/my_orders/
Authorization: Bearer <token>
```

**Estados de Orden**:
- 🟡 `PENDING` - Pendiente de pago
- 🟢 `PAID` - Pagada
- 🚚 `SHIPPED` - Enviada
- ✅ `DELIVERED` - Entregada (puede solicitar devolución)
- ❌ `CANCELLED` - Cancelada

---

#### 4️⃣ **Sistema de Devoluciones** ⭐

| Funcionalidad | Endpoint | Método | Descripción |
|---------------|----------|--------|-------------|
| 📝 Solicitar devolución | `/api/returns/` | POST | Crear nueva solicitud |
| 📋 Ver mis devoluciones | `/api/returns/my_returns/` | GET | Mis solicitudes de devolución |
| 🔍 Ver detalle | `/api/returns/{id}/` | GET | Estado y detalles |
| ❌ Cancelar solicitud | `/api/returns/{id}/cancel/` | POST | Cancelar antes de aprobación |

**Ejemplo de uso**:
```bash
# Solicitar devolución
POST /api/returns/
Authorization: Bearer <token>
{
    "order_id": 15,
    "product_id": 8,
    "reason": "DEFECTIVE",
    "description": "El producto llegó con defectos de fábrica",
    "refund_method": "WALLET"
}

# Ver mis devoluciones
GET /api/returns/my_returns/
```

**Validaciones automáticas**:
- ✅ La orden debe estar en estado `DELIVERED`
- ✅ No han pasado más de 30 días desde la entrega
- ✅ El producto pertenece a la orden
- ✅ No existe devolución previa para ese producto
- ✅ El usuario es dueño de la orden

**Razones de devolución disponibles**:
- `DEFECTIVE` - Producto defectuoso
- `WRONG_ITEM` - Producto incorrecto
- `NOT_AS_DESCRIBED` - No coincide con descripción
- `CHANGED_MIND` - Cambió de opinión
- `OTHER` - Otra razón

**Métodos de reembolso**:
- `WALLET` - A billetera virtual (instantáneo)
- `ORIGINAL` - Al método de pago original
- `BANK` - Transferencia bancaria

---

#### 5️⃣ **Billetera Virtual** 💰

| Funcionalidad | Endpoint | Método | Descripción |
|---------------|----------|--------|-------------|
| 💵 Ver saldo | `/api/wallet/balance/` | GET | Saldo actual disponible |
| 📜 Ver transacciones | `/api/wallet/transactions/` | GET | Historial completo |
| 📊 Ver estadísticas | `/api/wallet/statistics/` | GET | Ingresos, egresos, total |
| 💸 Retirar fondos | `/api/wallet/withdraw/` | POST | Solicitar retiro |

**Ejemplo de uso**:
```bash
# Ver saldo
GET /api/wallet/balance/
Authorization: Bearer <token>
# Respuesta: { "balance": "5499.99", "currency": "MXN" }

# Ver transacciones
GET /api/wallet/transactions/
# Lista de: REFUND, DEPOSIT, WITHDRAWAL, PURCHASE

# Estadísticas
GET /api/wallet/statistics/
# Total ingresos, egresos, transacciones
```

**Tipos de transacciones**:
- ✅ `REFUND` - Reembolso de devolución aprobada
- 💰 `DEPOSIT` - Depósito manual
- 💸 `WITHDRAWAL` - Retiro de fondos
- 🛒 `PURCHASE` - Compra con billetera

---

#### 6️⃣ **Garantías**

| Funcionalidad | Endpoint | Método | Descripción |
|---------------|----------|--------|-------------|
| 🛡️ Ver garantías | `/api/warranties/` | GET | Garantías de productos entregados |
| 📄 Detalle garantía | `/api/warranties/{id}/` | GET | Info de garantía específica |

**Ejemplo de uso**:
```bash
GET /api/warranties/
Authorization: Bearer <token>
```

**Nota**: Las garantías se crean automáticamente cuando una orden es marcada como `DELIVERED`.

---

### 🚫 Funcionalidades NO Disponibles

❌ Ver devoluciones de otros usuarios  
❌ Aprobar/rechazar devoluciones  
❌ Solicitar evaluación física  
❌ Acceder al panel de administración  
❌ Gestionar usuarios  
❌ Modificar productos o categorías  
❌ Ver órdenes de otros clientes  

---

## 👔 MANAGER

### 🎯 Rol: Gestor de Devoluciones y Operaciones

**Credenciales de ejemplo**:
- Usuario: `carlos_manager`
- Contraseña: `manager123`

### 📌 Funcionalidades Adicionales

#### ✅ **Hereda TODO de CLIENTE** +

---

#### 1️⃣ **Gestión Avanzada de Devoluciones**

| Funcionalidad | Endpoint | Método | Descripción |
|---------------|----------|--------|-------------|
| 📋 Ver TODAS las devoluciones | `/api/returns/` | GET | Sin filtro de usuario |
| ✅ Aprobar devolución | `/api/returns/{id}/approve/` | POST | Autorizar reembolso |
| ❌ Rechazar devolución | `/api/returns/{id}/reject/` | POST | Denegar solicitud |
| 🔍 Solicitar evaluación | `/api/returns/{id}/request_physical_evaluation/` | POST | Inspección física |

**Ejemplo de uso**:
```bash
# Ver TODAS las devoluciones del sistema
GET /api/returns/
Authorization: Bearer <token_manager>

# Aprobar devolución
POST /api/returns/24/approve/
{
    "comments": "Producto verificado como defectuoso. Aprobado para reembolso."
}

# Rechazar devolución
POST /api/returns/25/reject/
{
    "comments": "El producto está en perfectas condiciones. No procede."
}

# Solicitar evaluación física
POST /api/returns/26/request_physical_evaluation/
{
    "comments": "Se requiere inspección técnica para verificar el defecto reportado."
}
```

**Estados que puede gestionar**:
- 📝 `REQUESTED` → ✅ `APPROVED` / ❌ `REJECTED` / 🔍 `IN_EVALUATION`
- 🔍 `IN_EVALUATION` → ✅ `APPROVED` / ❌ `REJECTED`

**Acciones y efectos**:

| Acción | Estado Final | Efecto Automático |
|--------|--------------|-------------------|
| ✅ Aprobar | `APPROVED` | 💰 Reembolso a billetera/método original |
| ❌ Rechazar | `REJECTED` | ✉️ Notificación al cliente |
| 🔍 Evaluar | `IN_EVALUATION` | ⏳ Espera de inspección física |

---

#### 2️⃣ **Notificaciones por Email** ✉️

Los managers reciben emails automáticos cuando:
- 📧 Un cliente crea una nueva devolución
- 📧 Se solicita evaluación física
- 📧 Hay actualizaciones importantes

**Managers que reciben notificaciones** (configurado en `EMAIL_SETUP_GUIDE.md`):
1. carlos_manager@example.com
2. ana_manager@example.com
3. luis_manager@example.com
4. sofia_manager@example.com
5. miguel_manager@example.com
6. laura_manager@example.com

---

#### 3️⃣ **Panel de Control**

| Funcionalidad | Endpoint | Método | Descripción |
|---------------|----------|--------|-------------|
| 📊 Dashboard | `/api/returns/?status=REQUESTED` | GET | Devoluciones pendientes |
| 🔍 Filtrar por estado | `/api/returns/?status=X` | GET | REQUESTED, APPROVED, etc. |
| 📅 Filtrar por fecha | `/api/returns/?created_at__gte=2024-01-01` | GET | Rango de fechas |
| 👤 Filtrar por cliente | `/api/returns/?user__username=juan` | GET | Por usuario |

**Ejemplo de uso**:
```bash
# Ver devoluciones pendientes de acción
GET /api/returns/?status=REQUESTED

# Ver devoluciones en evaluación
GET /api/returns/?status=IN_EVALUATION

# Ver devoluciones aprobadas hoy
GET /api/returns/?status=APPROVED&created_at__gte=2025-11-10
```

---

### 🚫 Funcionalidades NO Disponibles

❌ Acceder al panel de Django Admin  
❌ Crear/modificar usuarios  
❌ Modificar productos o categorías  
❌ Eliminar devoluciones  
❌ Modificar órdenes de otros usuarios  
❌ Cambiar roles de usuarios  

---

## ⚙️ ADMIN

### 🎯 Rol: Administrador del Sistema

**Credenciales de ejemplo**:
- Usuario: `admin`
- Contraseña: `admin123`

### 📌 Funcionalidades Totales

#### ✅ **Hereda TODO de CLIENTE + MANAGER** +

---

#### 1️⃣ **Panel de Administración Django**

| Funcionalidad | URL | Descripción |
|---------------|-----|-------------|
| 🏠 Dashboard | `/admin/` | Panel principal |
| 👥 Gestión de usuarios | `/admin/users/customuser/` | CRUD completo de usuarios |
| 📦 Gestión de productos | `/admin/products/product/` | CRUD de productos |
| 🏷️ Gestión de categorías | `/admin/products/category/` | CRUD de categorías |
| 🛒 Gestión de órdenes | `/admin/shop_orders/order/` | Ver/editar todas las órdenes |
| 🔄 Gestión de devoluciones | `/admin/deliveries/return/` | Ver/editar todas las devoluciones |
| 💰 Gestión de billeteras | `/admin/users/wallet/` | Ver/modificar saldos |
| 📊 Gestión de transacciones | `/admin/users/wallettransaction/` | Historial completo |
| 🛡️ Gestión de garantías | `/admin/deliveries/warranty/` | CRUD de garantías |
| 📜 Logs de auditoría | `/admin/audit_log/auditlog/` | Registro de acciones |

**Ejemplo de uso**:
```bash
# Acceder al panel
http://localhost:8000/admin/

# Crear nuevo usuario
http://localhost:8000/admin/users/customuser/add/

# Ver todas las órdenes
http://localhost:8000/admin/shop_orders/order/
```

---

#### 2️⃣ **Gestión Avanzada de Usuarios**

| Funcionalidad | Endpoint | Método | Descripción |
|---------------|----------|--------|-------------|
| 👥 Listar usuarios | `/admin/users/customuser/` | GET | Todos los usuarios |
| ➕ Crear usuario | `/admin/users/customuser/add/` | POST | Nuevo usuario |
| ✏️ Editar usuario | `/admin/users/customuser/{id}/change/` | POST | Modificar datos |
| ❌ Eliminar usuario | `/admin/users/customuser/{id}/delete/` | POST | Borrar usuario |
| 🔑 Cambiar contraseña | `/admin/users/customuser/{id}/password/` | POST | Reset password |
| 🎭 Cambiar rol | Panel Admin | - | Modificar CLIENTE/MANAGER/ADMIN |

---

#### 3️⃣ **Gestión de Productos y Categorías**

| Funcionalidad | Capacidad |
|---------------|-----------|
| ➕ Crear productos | ✅ Sí |
| ✏️ Modificar precios | ✅ Sí |
| 📦 Actualizar stock | ✅ Sí |
| ❌ Eliminar productos | ✅ Sí |
| 🏷️ Crear categorías | ✅ Sí |
| 🔄 Reasignar categorías | ✅ Sí |
| 📸 Subir imágenes | ✅ Sí |

---

#### 4️⃣ **Operaciones Especiales**

| Funcionalidad | Capacidad | Descripción |
|---------------|-----------|-------------|
| 💰 Ajustar saldo de billetera | ✅ Sí | Modificar balance directamente |
| 🔄 Forzar cambio de estado | ✅ Sí | Cambiar estado de orden/devolución |
| 📊 Generar reportes | ✅ Sí | Exportar datos |
| 🗑️ Eliminar registros | ✅ Sí | Borrar órdenes/devoluciones |
| 🔧 Acceder a configuración | ✅ Sí | Variables del sistema |
| 📜 Ver logs de auditoría | ✅ Sí | Historial de acciones |

---

#### 5️⃣ **Sistema de Auditoría**

| Funcionalidad | Endpoint | Descripción |
|---------------|----------|-------------|
| 📜 Ver logs | `/api/audit/logs/` | Historial de acciones |
| 🔍 Filtrar por usuario | `/api/audit/logs/?user=X` | Acciones de un usuario |
| 📅 Filtrar por fecha | `/api/audit/logs/?date=X` | Logs de una fecha |
| 🎯 Filtrar por acción | `/api/audit/logs/?action=CREATE` | Tipo de acción |

**Acciones registradas**:
- 📝 `CREATE` - Creación de registros
- ✏️ `UPDATE` - Modificaciones
- ❌ `DELETE` - Eliminaciones
- 👁️ `VIEW` - Consultas importantes

---

### ✅ Funcionalidades Ilimitadas

✅ Acceso total al sistema  
✅ Modificar cualquier dato  
✅ Eliminar cualquier registro  
✅ Crear/modificar/eliminar usuarios  
✅ Cambiar roles y permisos  
✅ Acceder a logs de auditoría  
✅ Modificar configuración del sistema  
✅ Exportar/importar datos  
✅ Ejecutar comandos de Django  
✅ Acceso a base de datos  

---

## 📊 Tabla Comparativa

| Funcionalidad | CLIENTE | MANAGER | ADMIN |
|---------------|---------|---------|-------|
| 🔓 Login | ✅ | ✅ | ✅ |
| 📦 Ver productos | ✅ | ✅ | ✅ |
| 🛒 Crear órdenes | ✅ | ✅ | ✅ |
| 📋 Ver mis órdenes | ✅ | ✅ | ✅ |
| 📝 Solicitar devolución | ✅ | ✅ | ✅ |
| 👁️ Ver mis devoluciones | ✅ | ✅ | ✅ |
| 💰 Ver mi billetera | ✅ | ✅ | ✅ |
| 🛡️ Ver mis garantías | ✅ | ✅ | ✅ |
| | | | |
| 👁️ Ver TODAS las devoluciones | ❌ | ✅ | ✅ |
| ✅ Aprobar devoluciones | ❌ | ✅ | ✅ |
| ❌ Rechazar devoluciones | ❌ | ✅ | ✅ |
| 🔍 Solicitar evaluación física | ❌ | ✅ | ✅ |
| ✉️ Recibir notificaciones email | ❌ | ✅ | ✅ |
| | | | |
| 🏠 Acceder a Django Admin | ❌ | ❌ | ✅ |
| 👥 Gestionar usuarios | ❌ | ❌ | ✅ |
| 📦 Crear/modificar productos | ❌ | ❌ | ✅ |
| 🏷️ Crear/modificar categorías | ❌ | ❌ | ✅ |
| 💰 Ajustar saldos billetera | ❌ | ❌ | ✅ |
| 🔄 Forzar cambios de estado | ❌ | ❌ | ✅ |
| 📜 Ver logs de auditoría | ❌ | ❌ | ✅ |
| 🔧 Modificar configuración | ❌ | ❌ | ✅ |
| 🗑️ Eliminar cualquier registro | ❌ | ❌ | ✅ |

---

## 🔄 Flujos de Trabajo

### 📦 Flujo Completo de Compra y Devolución

```
👤 CLIENTE
├── 1. Login (/api/users/login/)
├── 2. Ver productos (/api/products/)
├── 3. Crear orden (/api/orders/)
│   └── Estado: PENDING → PAID → SHIPPED → DELIVERED
├── 4. Espera entrega (automático)
│   └── ✅ Se crea garantía automática
├── 5. Solicitar devolución (/api/returns/)
│   ├── Validaciones automáticas:
│   │   ✅ Orden DELIVERED
│   │   ✅ Dentro de 30 días
│   │   ✅ Producto válido
│   └── Estado: REQUESTED
│
👔 MANAGER recibe email de notificación
├── 6. Ver devolución (/api/returns/{id}/)
├── 7. Decisión:
│   ├── Opción A: Aprobar (/approve/)
│   │   └── 💰 Reembolso automático a billetera
│   ├── Opción B: Rechazar (/reject/)
│   │   └── ✉️ Notificación al cliente
│   └── Opción C: Evaluar (/request_physical_evaluation/)
│       └── ⏳ Estado: IN_EVALUATION
│           └── Luego: Aprobar o Rechazar
│
👤 CLIENTE
└── 8. Ver saldo actualizado (/api/wallet/balance/)
    └── 💵 Usar para nuevas compras
```

---

### 🛠️ Flujo de Gestión (MANAGER)

```
👔 MANAGER
├── Login (/api/users/login/)
├── Dashboard de devoluciones
│   ├── Ver pendientes (/api/returns/?status=REQUESTED)
│   ├── Ver en evaluación (/api/returns/?status=IN_EVALUATION)
│   └── Ver histórico (/api/returns/)
│
├── Para cada devolución:
│   ├── Ver detalle completo (/api/returns/{id}/)
│   │   ├── Info del producto
│   │   ├── Razón de devolución
│   │   ├── Descripción del cliente
│   │   └── Historial de estados
│   │
│   └── Tomar acción:
│       ├── ✅ APROBAR
│       │   └── Reembolso instantáneo
│       ├── ❌ RECHAZAR
│       │   └── Con comentarios
│       └── 🔍 EVALUAR
│           └── Solicitar inspección
│
└── Recibir emails de nuevas solicitudes
```

---

### ⚙️ Flujo Administrativo (ADMIN)

```
⚙️ ADMIN
├── Login Django Admin (/admin/)
│
├── Gestión de usuarios
│   ├── Crear nuevos usuarios
│   ├── Cambiar roles (CLIENTE → MANAGER)
│   ├── Resetear contraseñas
│   └── Desactivar cuentas
│
├── Gestión de productos
│   ├── Crear/editar productos
│   ├── Actualizar precios y stock
│   ├── Subir imágenes
│   └── Organizar en categorías
│
├── Supervisión de operaciones
│   ├── Ver todas las órdenes
│   ├── Monitorear devoluciones
│   ├── Revisar transacciones
│   └── Verificar garantías
│
└── Auditoría y reportes
    ├── Ver logs de auditoría
    ├── Generar reportes
    ├── Exportar datos
    └── Analizar métricas
```

---

## 🔒 Restricciones de Seguridad

### 🔐 Autenticación y Autorización

```python
# Validación automática por rol
@permission_classes([IsAuthenticated])
def my_orders(request):
    # Solo puede ver sus propias órdenes
    return Order.objects.filter(user=request.user)

@permission_classes([IsAuthenticated, IsManager])
def approve_return(request, pk):
    # Solo managers pueden aprobar
    return return_obj.approve()

@permission_classes([IsAdminUser])
def admin_panel(request):
    # Solo admins pueden acceder
    return render('admin/index.html')
```

---

### 🛡️ Protecciones Implementadas

| Protección | CLIENTE | MANAGER | ADMIN |
|------------|---------|---------|-------|
| Solo ver propios datos | ✅ | ❌ | ❌ |
| Token JWT requerido | ✅ | ✅ | ✅ |
| Validación de propiedad | ✅ | ✅ | ❌ |
| Rate limiting | ✅ | ✅ | ✅ |
| CORS configurado | ✅ | ✅ | ✅ |
| Validaciones de negocio | ✅ | ✅ | ✅ |
| Logs de auditoría | ❌ | ⚠️ | ✅ |

---

### 🚨 Validaciones Críticas

**Para CLIENTES**:
- ✅ No puede ver órdenes de otros usuarios
- ✅ No puede solicitar devolución de órdenes ajenas
- ✅ No puede ver devoluciones de otros
- ✅ No puede acceder a billeteras de otros
- ✅ No puede aprobar sus propias devoluciones

**Para MANAGERS**:
- ✅ No puede modificar usuarios
- ✅ No puede cambiar productos/precios
- ✅ No puede acceder a Django Admin
- ✅ No puede eliminar registros
- ✅ Solo puede gestionar devoluciones

**Para ADMINS**:
- ⚠️ Poder total - Usar con responsabilidad
- ⚠️ Todas las acciones quedan registradas
- ⚠️ Cambios permanentes en BD

---

## 📚 Documentación Relacionada

- **Credenciales**: `CREDENCIALES_SISTEMA.md`
- **Autenticación Frontend**: `frontend_docs/01_AUTENTICACION.md`
- **Sistema de Devoluciones**: `frontend_docs/03_DEVOLUCIONES.md`
- **Billetera Virtual**: `frontend_docs/04_BILLETERA_VIRTUAL.md`
- **Configuración Email**: `EMAIL_SETUP_GUIDE.md`
- **Esquema API Completo**: `API_SCHEMA.md`

---

## 🎯 Testing por Rol

### 🧪 Test CLIENTE

```bash
# 1. Login
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "juan_cliente", "password": "password123"}'

# 2. Ver productos
curl http://localhost:8000/api/products/ \
  -H "Authorization: Bearer <token>"

# 3. Crear orden
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"items": [{"product_id": 5, "quantity": 1}]}'

# 4. Solicitar devolución
curl -X POST http://localhost:8000/api/returns/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "product_id": 5,
    "reason": "DEFECTIVE",
    "description": "No funciona",
    "refund_method": "WALLET"
  }'

# 5. Ver billetera
curl http://localhost:8000/api/wallet/balance/ \
  -H "Authorization: Bearer <token>"
```

---

### 🧪 Test MANAGER

```bash
# 1. Login
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "carlos_manager", "password": "manager123"}'

# 2. Ver TODAS las devoluciones
curl http://localhost:8000/api/returns/ \
  -H "Authorization: Bearer <token>"

# 3. Aprobar devolución
curl -X POST http://localhost:8000/api/returns/24/approve/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"comments": "Aprobado"}'

# 4. Rechazar devolución
curl -X POST http://localhost:8000/api/returns/25/reject/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"comments": "No procede"}'
```

---

### 🧪 Test ADMIN

```bash
# 1. Login Django Admin
http://localhost:8000/admin/
Usuario: admin
Contraseña: admin123

# 2. Gestionar usuarios
http://localhost:8000/admin/users/customuser/

# 3. Ver logs
http://localhost:8000/admin/audit_log/auditlog/
```

---

## 🎓 Mejores Prácticas

### Para CLIENTES:
1. ✅ Verifica el estado de tu orden antes de solicitar devolución
2. ✅ Lee la política de 30 días
3. ✅ Proporciona descripción detallada en devoluciones
4. ✅ Revisa tu billetera regularmente

### Para MANAGERS:
1. ✅ Revisa la descripción completa antes de aprobar/rechazar
2. ✅ Usa evaluación física cuando haya dudas
3. ✅ Añade comentarios explicativos en cada acción
4. ✅ Responde rápido a las notificaciones por email

### Para ADMINS:
1. ⚠️ No modifiques datos sin razón justificada
2. ⚠️ Todas tus acciones quedan registradas
3. ⚠️ Usa el panel admin solo cuando sea necesario
4. ⚠️ Mantén contraseñas seguras y únicas

---

**Última actualización**: 10 de noviembre de 2025  
**Sistema**: E-commerce con Devoluciones y Billetera Virtual  
**Versión**: 1.0  
**Commit**: `a730e73`
