# Sistema de Entregas, Garantías, Devoluciones y Reparaciones

## 📋 Descripción General

Este módulo implementa un sistema completo para gestionar:
- **Entregas (Deliveries)**: Asignación y seguimiento de entregas de órdenes
- **Garantías (Warranties)**: Gestión de garantías de productos
- **Devoluciones (Returns)**: Proceso de devoluciones y reembolsos
- **Reparaciones (Repairs)**: Seguimiento de reparaciones de productos

## 🚀 Casos de Uso Implementados

### CU-13: Gestionar Garantías de Productos
- Crear garantías automáticamente al completar una orden
- Consultar estado de garantía (activa, reclamada, expirada, anulada)
- Reclamar garantía
- Ver términos y condiciones

### CU-14: Gestionar Devoluciones
- Solicitar devolución de producto
- Aprobar/rechazar devoluciones (Manager/Admin)
- Calcular reembolso
- Seguimiento de estado (solicitada, aprobada, rechazada, en tránsito, completada)

### CU-15: Gestionar Arreglos/Reparaciones
- Solicitar reparación de producto
- Vincular con garantía (si aplica)
- Estimar y calcular costos
- Seguimiento de reparación (solicitada, en progreso, completada, entregada)

### CU-16: Gestionar Delivery de Compras
- Crear perfil de repartidor con zona asignada
- Asignar entrega a repartidor disponible
- Seguimiento en tiempo real (pendiente, asignada, recogida, en tránsito, entregada)
- Actualización de estado por repartidor

### CU-17: Verificar Estado de Delivery
- Consultar estado actual de entrega
- Ver información del repartidor asignado
- Historial de entregas
- Estadísticas de entregas por zona

## 🏗️ Arquitectura

### Modelos Principales

#### 1. DeliveryZone
Zonas geográficas para delivery (Norte, Sur, Este, Oeste, Centro)

```python
{
    "id": 1,
    "name": "Zona Norte",
    "description": "Incluye distritos del norte",
    "is_active": true
}
```

#### 2. DeliveryProfile
Perfil extendido para usuarios con rol DELIVERY

```python
{
    "id": 1,
    "user": {...},
    "zone": 1,
    "status": "AVAILABLE",  # AVAILABLE, BUSY, OFFLINE
    "vehicle_type": "Moto",
    "license_plate": "ABC-123",
    "phone": "+51 999 888 777"
}
```

#### 3. Delivery
Seguimiento de entregas de órdenes

```python
{
    "id": 1,
    "order": 123,
    "delivery_person": 5,
    "zone": 1,
    "status": "IN_TRANSIT",  # PENDING, ASSIGNED, PICKED_UP, IN_TRANSIT, DELIVERED, FAILED
    "delivery_address": "Av. Lima 123",
    "customer_phone": "+51 999 111 222",
    "assigned_at": "2024-01-15T10:00:00Z",
    "delivered_at": null
}
```

#### 4. Warranty
Garantías de productos

```python
{
    "id": 1,
    "order": 123,
    "product": 45,
    "start_date": "2024-01-01",
    "end_date": "2025-01-01",
    "status": "ACTIVE",  # ACTIVE, CLAIMED, EXPIRED, VOID
    "warranty_terms": "Garantía de 1 año contra defectos de fábrica"
}
```

#### 5. Return
Devoluciones de productos

```python
{
    "id": 1,
    "order": 123,
    "product": 45,
    "quantity": 1,
    "reason": "DEFECTIVE",  # DEFECTIVE, WRONG_ITEM, NOT_AS_DESCRIBED, CHANGED_MIND, OTHER
    "status": "APPROVED",  # REQUESTED, APPROVED, REJECTED, IN_TRANSIT, COMPLETED
    "refund_amount": 99.99,
    "requested_at": "2024-01-15T10:00:00Z"
}
```

#### 6. Repair
Reparaciones de productos

```python
{
    "id": 1,
    "warranty": 1,
    "order": 123,
    "product": 45,
    "description": "Pantalla rota",
    "status": "IN_PROGRESS",  # REQUESTED, IN_PROGRESS, COMPLETED, DELIVERED, CANCELLED
    "estimated_cost": 50.00,
    "final_cost": 45.00,
    "is_under_warranty": true
}
```

## 🔐 Permisos y Roles

### Nuevo Rol: DELIVERY (Repartidor)
```python
class CustomUser:
    DELIVERY = 'DELIVERY', 'Repartidor'
```

### Matriz de Permisos

| Endpoint | ADMIN | MANAGER | DELIVERY | CAJERO | CLIENTE |
|----------|-------|---------|----------|--------|---------|
| Ver zonas | ✅ | ✅ | ❌ | ❌ | ❌ |
| Crear zona | ✅ | ✅ | ❌ | ❌ | ❌ |
| Ver perfiles delivery | ✅ | ✅ | ❌ | ❌ | ❌ |
| Actualizar estado propio | ✅ | ✅ | ✅ | ❌ | ❌ |
| Asignar delivery | ✅ | ✅ | ❌ | ❌ | ❌ |
| Ver mis entregas | ✅ | ✅ | ✅ | ❌ | ❌ |
| Actualizar estado entrega | ✅ | ✅ | ✅ | ❌ | ❌ |
| Gestionar garantías | ✅ | ✅ | ❌ | ❌ | ❌ |
| Solicitar devolución | ✅ | ✅ | ❌ | ❌ | ✅ |
| Aprobar/rechazar devolución | ✅ | ✅ | ❌ | ❌ | ❌ |
| Solicitar reparación | ✅ | ✅ | ❌ | ❌ | ✅ |
| Actualizar reparación | ✅ | ✅ | ❌ | ❌ | ❌ |

## 📡 API Endpoints

### Base URL: `/api/deliveries/`

### Zonas de Delivery

#### Listar zonas
```bash
GET /api/deliveries/zones/
```

#### Crear zona
```bash
POST /api/deliveries/zones/
{
    "name": "Zona Norte",
    "description": "Incluye distritos del norte",
    "is_active": true
}
```

### Perfiles de Delivery

#### Listar perfiles
```bash
GET /api/deliveries/profiles/
# Filtros: ?zone=1&status=AVAILABLE
```

#### Obtener repartidores disponibles
```bash
GET /api/deliveries/profiles/available/
# Filtros: ?zone=1
```

#### Actualizar mi estado
```bash
POST /api/deliveries/profiles/{id}/update_status/
{
    "status": "BUSY"
}
```

### Entregas

#### Listar entregas
```bash
GET /api/deliveries/deliveries/
# Filtros: ?status=IN_TRANSIT&zone=1
```

#### Ver mis entregas (Delivery)
```bash
GET /api/deliveries/deliveries/my_deliveries/
# Filtros: ?status=ASSIGNED
```

#### Asignar delivery a orden
```bash
POST /api/deliveries/deliveries/{id}/assign_delivery/
{
    "delivery_person_id": 5
}
```

#### Actualizar estado de entrega
```bash
POST /api/deliveries/deliveries/{id}/update_delivery_status/
{
    "status": "PICKED_UP",
    "notes": "Paquete recogido del almacén"
}
```

### Garantías

#### Listar garantías
```bash
GET /api/deliveries/warranties/
# Filtros: ?status=ACTIVE&product=45
```

#### Obtener garantías activas
```bash
GET /api/deliveries/warranties/active/
```

#### Reclamar garantía
```bash
POST /api/deliveries/warranties/{id}/claim/
{
    "notes": "Producto presenta defecto de fábrica"
}
```

### Devoluciones

#### Solicitar devolución
```bash
POST /api/deliveries/returns/
{
    "order": 123,
    "product": 45,
    "quantity": 1,
    "reason": "DEFECTIVE",
    "description": "El producto llegó dañado"
}
```

#### Aprobar devolución
```bash
POST /api/deliveries/returns/{id}/approve/
{
    "refund_amount": 99.99,
    "manager_notes": "Devolución aprobada"
}
```

#### Rechazar devolución
```bash
POST /api/deliveries/returns/{id}/reject/
{
    "manager_notes": "No cumple con los términos de devolución"
}
```

### Reparaciones

#### Solicitar reparación
```bash
POST /api/deliveries/repairs/
{
    "order": 123,
    "product": 45,
    "warranty": 1,
    "description": "Pantalla rota",
    "is_under_warranty": true
}
```

#### Actualizar estado de reparación
```bash
POST /api/deliveries/repairs/{id}/update_status/
{
    "status": "IN_PROGRESS",
    "technician_notes": "Reparación iniciada",
    "final_cost": 45.00
}
```

## 🔄 Flujos de Trabajo

### Flujo de Entrega (Delivery)

1. **Cliente realiza pedido** → Orden creada con estado `PENDING`
2. **Cliente paga** → Orden cambia a `PAID`
3. **Manager crea entrega** → Delivery con estado `PENDING`
4. **Manager asigna repartidor** → 
   - Delivery cambia a `ASSIGNED`
   - DeliveryProfile cambia a `BUSY`
   - Se guarda `assigned_at`
5. **Repartidor recoge paquete** → 
   - Delivery cambia a `PICKED_UP`
   - Se guarda `picked_up_at`
6. **Repartidor en camino** → Delivery cambia a `IN_TRANSIT`
7. **Entrega completada** → 
   - Delivery cambia a `DELIVERED`
   - Orden cambia a `DELIVERED`
   - DeliveryProfile cambia a `AVAILABLE`
   - Se guarda `delivered_at`

### Flujo de Devolución

1. **Cliente solicita devolución** → Return con estado `REQUESTED`
2. **Manager revisa** → 
   - **Aprueba**: Return cambia a `APPROVED`, se calcula `refund_amount`
   - **Rechaza**: Return cambia a `REJECTED` con notas
3. **Producto en tránsito** → Return cambia a `IN_TRANSIT`
4. **Producto recibido** → Return cambia a `COMPLETED`

### Flujo de Reparación

1. **Cliente solicita reparación** → Repair con estado `REQUESTED`
2. **Técnico revisa** → 
   - Repair cambia a `IN_PROGRESS`
   - Se estima `estimated_cost`
3. **Reparación completada** → 
   - Repair cambia a `COMPLETED`
   - Se registra `final_cost`
   - Se guarda `completed_at`
4. **Producto entregado** → Repair cambia a `DELIVERED`

## 🧪 Testing

### Crear Datos de Prueba

```bash
python create_delivery_test_data.py
```

Esto crea:
- 5 zonas de delivery
- Usuario `delivery1` con contraseña `delivery123`
- Perfil de delivery asignado a Zona Norte

### Casos de Prueba

#### 1. Asignar Delivery

```bash
# Login como Manager
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "manager", "password": "manager123"}'

# Crear delivery para orden
curl -X POST http://localhost:8000/api/deliveries/deliveries/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "order": 1,
    "delivery_address": "Av. Lima 123",
    "customer_phone": "+51 999 111 222",
    "zone": 1
  }'

# Asignar repartidor
curl -X POST http://localhost:8000/api/deliveries/deliveries/1/assign_delivery/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"delivery_person_id": 1}'
```

#### 2. Actualizar Estado (como Delivery)

```bash
# Login como delivery1
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "delivery1", "password": "delivery123"}'

# Ver mis entregas
curl -X GET http://localhost:8000/api/deliveries/deliveries/my_deliveries/ \
  -H "Authorization: Bearer {token}"

# Actualizar a PICKED_UP
curl -X POST http://localhost:8000/api/deliveries/deliveries/1/update_delivery_status/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"status": "PICKED_UP"}'

# Actualizar a IN_TRANSIT
curl -X POST http://localhost:8000/api/deliveries/deliveries/1/update_delivery_status/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"status": "IN_TRANSIT"}'

# Marcar como entregado
curl -X POST http://localhost:8000/api/deliveries/deliveries/1/update_delivery_status/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"status": "DELIVERED"}'
```

## 🔧 Administración

Todos los modelos están registrados en el panel de administración de Django:

```
http://localhost:8000/admin/
```

### Acciones Masivas Disponibles

#### DeliveryProfile
- Marcar como disponible
- Marcar como ocupado
- Marcar como desconectado

#### Delivery
- Marcar como recogido
- Marcar como en tránsito
- Marcar como entregado

#### Warranty
- Marcar como activa
- Marcar como expirada
- Anular garantía

#### Return
- Aprobar devoluciones
- Rechazar devoluciones
- Marcar como en tránsito
- Marcar como completada

#### Repair
- Marcar como en progreso
- Marcar como completada
- Marcar como entregada

## 📊 Estadísticas y Reportes

### Entregas por Zona

```python
from deliveries.models import Delivery, DeliveryZone
from django.db.models import Count

stats = Delivery.objects.values('zone__name').annotate(
    total=Count('id'),
    completed=Count('id', filter=Q(status='DELIVERED'))
)
```

### Repartidores Disponibles

```python
from deliveries.models import DeliveryProfile

available = DeliveryProfile.objects.filter(
    status='AVAILABLE'
).count()
```

### Garantías Activas

```python
from deliveries.models import Warranty
from django.utils import timezone

active = Warranty.objects.filter(
    status='ACTIVE',
    end_date__gte=timezone.now().date()
).count()
```

## 🚀 Próximas Mejoras

- [ ] Notificaciones push para cambios de estado
- [ ] Geolocalización en tiempo real
- [ ] Optimización de rutas
- [ ] Integración con servicios de mensajería (WhatsApp)
- [ ] Dashboard de métricas en tiempo real
- [ ] Historial completo de entregas
- [ ] Calificación de repartidores
- [ ] Cálculo automático de tiempo estimado de entrega

## 📝 Notas de Migración

### Cambios en Modelos Existentes

#### Order Model
Se agregó nuevo estado:
```python
DELIVERED = 'DELIVERED', 'Entregado'
```

### Nuevas Tablas Creadas

- `deliveries_deliveryzone`
- `deliveries_deliveryprofile`
- `deliveries_delivery`
- `deliveries_warranty`
- `deliveries_return`
- `deliveries_repair`

### Aplicar Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

## 🤝 Contribución

Para agregar nuevas funcionalidades:

1. Crear modelos en `deliveries/models.py`
2. Crear serializers en `deliveries/serializers.py`
3. Crear views en `deliveries/views.py`
4. Agregar URLs en `deliveries/urls.py`
5. Registrar en admin en `deliveries/admin.py`
6. Crear migraciones: `python manage.py makemigrations`
7. Aplicar migraciones: `python manage.py migrate`
8. Actualizar documentación

## 📄 Licencia

Este módulo es parte del sistema de e-commerce y sigue la misma licencia del proyecto principal.
