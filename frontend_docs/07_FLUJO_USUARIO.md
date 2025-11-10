# 🔄 07. FLUJOS DE USUARIO

## 📝 Descripción

Esta sección muestra los flujos completos de usuario desde la perspectiva del **Cliente** y del **Manager**.

---

## 👤 FLUJO DEL CLIENTE

### 🎯 Flujo Completo: De la Compra a la Devolución

```
┌─────────────────────────────────────────────────────────────────┐
│                       FLUJO DEL CLIENTE                         │
└─────────────────────────────────────────────────────────────────┘

📱 PASO 1: LOGIN
┌─────────────────┐
│  Login Page     │
│  - Username     │──► juan_cliente / password123
│  - Password     │
└─────────────────┘
        │
        ├─► ✅ Login Exitoso
        │   ├─► Token guardado en localStorage
        │   ├─► User profile cargado
        │   └─► Redirigir a /products
        │
        └─► ❌ Login Fallido
            └─► Mostrar error


🛍️ PASO 2: VER PRODUCTOS
┌─────────────────────────────────────────┐
│  Products Page                          │
│  GET /api/products/                     │
│                                         │
│  ┌───────────┐  ┌───────────┐         │
│  │ Tablet    │  │ Laptop    │  ...    │
│  │ $5,999.99 │  │ $12,999   │         │
│  └───────────┘  └───────────┘         │
└─────────────────────────────────────────┘
        │
        └─► Seleccionar producto


💳 PASO 3: CREAR ORDEN
┌─────────────────────────────────────────┐
│  Checkout                               │
│  POST /api/orders/                      │
│                                         │
│  Body:                                  │
│  {                                      │
│    items: [{                            │
│      product: 1,                        │
│      quantity: 1,                       │
│      price: 5999.99                     │
│    }],                                  │
│    payment_method: "CREDIT_CARD"        │
│  }                                      │
└─────────────────────────────────────────┘
        │
        ├─► ✅ Orden Creada
        │   ├─► Estado: PENDING
        │   ├─► Mostrar confirmación
        │   └─► Ver en "Mis Órdenes"
        │
        └─► ❌ Error
            └─► Stock insuficiente / Error de pago


📦 PASO 4: ESPERAR ENTREGA
┌─────────────────────────────────────────┐
│  My Orders Page                         │
│  GET /api/orders/my_orders/             │
│                                         │
│  Orden #62                              │
│  ┌─────────────────────────────────┐   │
│  │ Estado: PENDING    ➜ IN_TRANSIT │   │
│  │              ➜ DELIVERED         │   │
│  └─────────────────────────────────┘   │
│                                         │
│  (Actualizar estado manualmente        │
│   o automáticamente)                   │
└─────────────────────────────────────────┘
        │
        └─► Cuando estado = DELIVERED


↩️ PASO 5: SOLICITAR DEVOLUCIÓN
┌─────────────────────────────────────────┐
│  Request Return Page                    │
│  POST /api/deliveries/returns/          │
│                                         │
│  1. Seleccionar orden entregada         │
│  2. Escribir razón                      │
│  3. Elegir método de reembolso:         │
│     ○ Billetera Virtual (recomendado)   │
│     ○ Método original                   │
│                                         │
│  Body:                                  │
│  {                                      │
│    order: 62,                           │
│    product: 1,                          │
│    reason: "Producto defectuoso",       │
│    refund_method: "WALLET"              │
│  }                                      │
└─────────────────────────────────────────┘
        │
        ├─► ✅ Devolución Creada
        │   ├─► ID: #17
        │   ├─► Estado: REQUESTED
        │   ├─► 📧 Email a 6 managers
        │   └─► Mostrar confirmación
        │
        └─► ❌ Error
            ├─► Orden no entregada
            ├─► Fuera de plazo (>30 días)
            └─► Ya existe devolución


📋 PASO 6: VER MIS DEVOLUCIONES
┌─────────────────────────────────────────┐
│  My Returns Page                        │
│  GET /api/deliveries/returns/           │
│                                         │
│  Devolución #17                         │
│  ┌─────────────────────────────────┐   │
│  │ Estado: REQUESTED               │   │
│  │ Producto: Tablet iPad Air       │   │
│  │ Razón: Producto defectuoso      │   │
│  │ Método: Billetera Virtual       │   │
│  │ Fecha: 10/11/2025              │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Actualizar cada 30 segundos o         │
│  con botón "Refrescar"                 │
└─────────────────────────────────────────┘
        │
        └─► Esperar respuesta del manager


⏳ PASO 7: MANAGER PROCESA
┌─────────────────────────────────────────┐
│  Estados Posibles:                      │
│                                         │
│  1️⃣ REQUESTED                           │
│     ↓                                   │
│  2️⃣ IN_EVALUATION (manager acepta)      │
│     ↓                                   │
│  3️⃣ APPROVED (manager aprueba)          │
│     └─► 💰 Reembolso procesado          │
│                                         │
│  O BIEN:                                │
│                                         │
│  2️⃣ IN_EVALUATION                       │
│     ↓                                   │
│  3️⃣ REJECTED (manager rechaza)          │
│     └─► ❌ Sin reembolso                │
└─────────────────────────────────────────┘


💰 PASO 8: RECIBIR REEMBOLSO
┌─────────────────────────────────────────┐
│  Si APROBADO y método = WALLET:         │
│                                         │
│  1. Billetera creada automáticamente    │
│     GET /api/users/wallets/my_balance/  │
│                                         │
│  2. Saldo actualizado                   │
│     Balance: $5,999.99                  │
│                                         │
│  3. Transacción registrada              │
│     GET /api/users/wallet-transactions/ │
│                                         │
│     Transacción:                        │
│     - Tipo: REFUND                      │
│     - Monto: $5,999.99                  │
│     - Descripción: Reembolso #17        │
└─────────────────────────────────────────┘


🎉 PASO 9: USAR SALDO
┌─────────────────────────────────────────┐
│  En futuras compras:                    │
│                                         │
│  Checkout:                              │
│  - Total: $3,000.00                     │
│  - Saldo disponible: $5,999.99          │
│                                         │
│  ✅ Usar billetera                      │
│  ○ Tarjeta de crédito                   │
│                                         │
│  POST /api/orders/                      │
│  {                                      │
│    payment_method: "WALLET"             │
│  }                                      │
│                                         │
│  Saldo después: $2,999.99               │
└─────────────────────────────────────────┘
```

---

## 👔 FLUJO DEL MANAGER

### 🎯 Flujo Completo: Gestión de Devoluciones

```
┌─────────────────────────────────────────────────────────────────┐
│                       FLUJO DEL MANAGER                         │
└─────────────────────────────────────────────────────────────────┘

📱 PASO 1: LOGIN
┌─────────────────┐
│  Login Page     │
│  - Username     │──► carlos_manager / manager123
│  - Password     │
└─────────────────┘
        │
        └─► Redirigir a /manager/returns


📧 PASO 2: RECIBIR NOTIFICACIÓN
┌─────────────────────────────────────────┐
│  Email Recibido:                        │
│                                         │
│  De: sistema@ecommerce.com              │
│  Para: carlos_manager@example.com       │
│                                         │
│  Asunto: 🔔 Nueva solicitud de         │
│          devolución - Tablet iPad Air   │
│                                         │
│  Contenido:                             │
│  - ID: #17                              │
│  - Cliente: Juan Cliente                │
│  - Producto: Tablet iPad Air            │
│  - Razón: Producto defectuoso           │
│  - Método: Billetera Virtual            │
└─────────────────────────────────────────┘
        │
        └─► Acceder al sistema


📋 PASO 3: VER PANEL DE DEVOLUCIONES
┌─────────────────────────────────────────┐
│  Manager Panel                          │
│  GET /api/deliveries/returns/           │
│                                         │
│  Filtros:                               │
│  [Todas] [Solicitadas] [En Evaluación] │
│  [Aprobadas] [Rechazadas]               │
│                                         │
│  Lista de devoluciones:                 │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ Devolución #17                    │ │
│  │ ● REQUESTED                       │ │
│  │                                   │ │
│  │ Cliente: Juan Cliente             │ │
│  │ Producto: Tablet iPad Air         │ │
│  │ Precio: $5,999.99                 │ │
│  │ Razón: Producto defectuoso        │ │
│  │ Método: Billetera Virtual         │ │
│  │                                   │ │
│  │ [📦 Enviar a Evaluación]          │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘


📦 PASO 4: ENVIAR A EVALUACIÓN
┌─────────────────────────────────────────┐
│  POST /api/deliveries/returns/17/       │
│       send_to_evaluation/               │
│                                         │
│  Sin body requerido                     │
└─────────────────────────────────────────┘
        │
        ├─► ✅ Enviado a evaluación
        │   ├─► Estado: IN_EVALUATION
        │   ├─► 📧 Email enviado a managers
        │   └─► Botones cambian
        │
        └─► ❌ Error
            └─► Ya está en evaluación


🔍 PASO 5: EVALUAR PRODUCTO
┌─────────────────────────────────────────┐
│  (Proceso fuera del sistema)            │
│                                         │
│  - Revisar producto físicamente         │
│  - Verificar condición                  │
│  - Confirmar defecto                    │
│  - Decidir: ¿Aprobar o rechazar?        │
└─────────────────────────────────────────┘


✅ PASO 6A: APROBAR DEVOLUCIÓN
┌─────────────────────────────────────────┐
│  POST /api/deliveries/returns/17/       │
│       approve/                          │
│                                         │
│  Sin body requerido                     │
└─────────────────────────────────────────┘
        │
        └─► ✅ Aprobado
            ├─► Estado: APPROVED
            ├─► 💰 Reembolso procesado:
            │   ├─► Si WALLET: crear/actualizar billetera
            │   └─► Si ORIGINAL: procesar con Stripe
            ├─► 📧 Email a managers
            └─► Mostrar confirmación


❌ PASO 6B: RECHAZAR DEVOLUCIÓN
┌─────────────────────────────────────────┐
│  POST /api/deliveries/returns/17/       │
│       reject/                           │
│                                         │
│  Body:                                  │
│  {                                      │
│    "rejection_reason": "El producto    │
│     está en perfectas condiciones"      │
│  }                                      │
└─────────────────────────────────────────┘
        │
        └─► ❌ Rechazado
            ├─► Estado: REJECTED
            ├─► Sin reembolso
            ├─► 📧 Email a managers
            └─► Mostrar confirmación


📊 PASO 7: VER ESTADÍSTICAS
┌─────────────────────────────────────────┐
│  Dashboard (opcional)                   │
│                                         │
│  Total devoluciones: 22                 │
│  ├─► Solicitadas: 5                     │
│  ├─► En evaluación: 3                   │
│  ├─► Aprobadas: 10                      │
│  └─► Rechazadas: 4                      │
│                                         │
│  Monto total reembolsado: $59,999.90    │
└─────────────────────────────────────────┘
```

---

## 🔄 DIAGRAMA DE ESTADOS

### Estados de una Devolución

```
                    ┌─────────────┐
                    │   CLIENTE   │
                    │   solicita  │
                    │  devolución │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  REQUESTED  │◄──── 📧 Email a managers
                    └──────┬──────┘
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
         ┌─────────────┐      ┌─────────────┐
         │  REJECTED   │      │     IN_     │
         │             │      │ EVALUATION  │◄──── 📧 Email a managers
         └─────────────┘      └──────┬──────┘
                │                     │
                │              ┌──────┴──────┐
                │              │             │
                │              ▼             ▼
                │       ┌─────────────┐ ┌─────────────┐
                │       │  APPROVED   │ │  REJECTED   │
                │       └──────┬──────┘ └─────────────┘
                │              │
                │              ▼
                │       ┌─────────────┐
                │       │ 💰 REEMBOLSO│
                │       │   procesado │
                │       └─────────────┘
                │
                └──────► FIN (sin reembolso)


Leyenda:
========
● REQUESTED     - Cliente solicita devolución
● IN_EVALUATION - Manager acepta revisar
● APPROVED      - Manager aprueba (con reembolso)
● REJECTED      - Manager rechaza (sin reembolso)
```

---

## 📱 PANTALLAS RECOMENDADAS

### Para el Cliente:

1. **Login** (`/login`)
2. **Dashboard** (`/dashboard`)
3. **Productos** (`/products`)
4. **Mis Órdenes** (`/orders`)
5. **Solicitar Devolución** (`/returns/new`)
6. **Mis Devoluciones** (`/returns`)
7. **Mi Billetera** (`/wallet`)
8. **Historial de Transacciones** (`/wallet/transactions`)

### Para el Manager:

1. **Login** (`/login`)
2. **Panel de Devoluciones** (`/manager/returns`)
3. **Detalle de Devolución** (`/manager/returns/:id`)
4. **Estadísticas** (`/manager/stats`) [opcional]

---

## ⏱️ Tiempos Esperados

| Acción | Tiempo Esperado |
|--------|-----------------|
| Login | < 1 segundo |
| Listar productos | < 2 segundos |
| Crear orden | < 2 segundos |
| Solicitar devolución | < 3 segundos |
| Listar devoluciones | < 2 segundos |
| Enviar a evaluación | < 1 segundo |
| Aprobar/Rechazar | < 3 segundos |
| Ver billetera | < 1 segundo |
| Listar transacciones | < 2 segundos |
| Envío de emails | Asíncrono (no bloquea) |

---

## 🎨 Estados Visuales Recomendados

### Colores por Estado:

- **REQUESTED** → 🟡 Amarillo (#FFC107)
- **IN_EVALUATION** → 🔵 Azul (#2196F3)
- **APPROVED** → 🟢 Verde (#4CAF50)
- **REJECTED** → 🔴 Rojo (#F44336)

### Iconos Recomendados:

- Devolución solicitada: 📤
- En evaluación: 🔍
- Aprobada: ✅
- Rechazada: ❌
- Billetera: 💰
- Transacción: 💳
- Email: 📧
- Producto: 📦

---

**Siguiente:** Ver `08_ESTADOS_Y_VALIDACIONES.md` para reglas de negocio
