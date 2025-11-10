# 🔄 Flujo Completo: Garantías y Delivery

## 📋 Resumen

Este documento explica cómo funciona el **sistema automático** de entregas y garantías que se integra completamente con el flujo de órdenes.

---

## 🎯 Problema Original (ANTES)

### ❌ Lo que estaba mal:

```
Cliente compra → Paga → ... ¿Y luego qué?

• NO se creaban deliveries automáticamente
• NO se creaban garantías automáticamente  
• El manager tenía que crear todo manualmente
• Flujo desconectado y propenso a errores
```

---

## ✅ Solución Implementada (AHORA)

### **Sistema Automático con Django Signals**

Los signals escuchan cambios en las órdenes y disparan acciones automáticamente:

```python
# deliveries/signals.py

@receiver(post_save, sender=Order)
def create_delivery_on_paid_order(...):
    """Cuando orden = PAID → Crear Delivery automáticamente"""
    
@receiver(post_save, sender=Order)
def create_warranties_on_delivered_order(...):
    """Cuando orden = DELIVERED → Crear Garantías automáticamente"""
```

---

## 🔄 Flujo Completo Paso a Paso

### **1️⃣ Cliente Crea Orden**
```
POST /api/orders/
{
  "items": [
    {"product_id": 1, "quantity": 2},
    {"product_id": 5, "quantity": 1}
  ]
}

Estado: PENDING
✅ Orden creada
❌ Sin delivery todavía
❌ Sin garantías todavía
```

### **2️⃣ Cliente Paga con Stripe**
```
POST /api/orders/123/stripe-checkout/

→ Usuario redirigido a Stripe
→ Usuario paga
→ Stripe envía webhook
→ Backend actualiza: orden.status = 'PAID'

🚀 TRIGGER: Signal create_delivery_on_paid_order()
```

**✨ QUÉ PASA AUTOMÁTICAMENTE:**
```python
# Signal detecta: orden.status == 'PAID'

1. Se crea Delivery:
   - order: orden actual
   - delivery_address: dirección del usuario
   - customer_phone: teléfono del usuario
   - status: 'PENDING'
   - notes: "Delivery creado automáticamente..."

2. Delivery queda listo para que manager asigne repartidor
```

**Resultado:**
```
Estado: PAID
✅ Orden pagada
✅ Delivery creado automáticamente (PENDING)
❌ Sin garantías todavía (aún no entregado)
```

---

### **3️⃣ Manager Asigna Repartidor**
```
POST /api/deliveries/deliveries/1/assign_delivery/
{
  "delivery_person_id": 5
}

✅ Delivery.status = 'ASSIGNED'
✅ DeliveryProfile.status = 'BUSY'
✅ Repartidor recibe notificación (futuro)
```

---

### **4️⃣ Repartidor Actualiza Estados**

**4a. Repartidor recoge paquete:**
```
POST /api/deliveries/deliveries/1/update_delivery_status/
{
  "status": "PICKED_UP"
}

✅ Delivery.status = 'PICKED_UP'
✅ Delivery.picked_up_at = ahora
```

**4b. Repartidor sale a entregar:**
```
POST /api/deliveries/deliveries/1/update_delivery_status/
{
  "status": "IN_TRANSIT"
}

✅ Delivery.status = 'IN_TRANSIT'
```

**4c. Repartidor entrega al cliente:**
```
POST /api/deliveries/deliveries/1/update_delivery_status/
{
  "status": "DELIVERED"
}

✅ Delivery.status = 'DELIVERED'
✅ Delivery.delivered_at = ahora
✅ DeliveryProfile.status = 'AVAILABLE' (liberado)
✅ Order.status = 'DELIVERED' (actualizado)

🚀 TRIGGER: Signal create_warranties_on_delivered_order()
```

---

### **5️⃣ Sistema Crea Garantías Automáticamente**

**✨ QUÉ PASA AUTOMÁTICAMENTE:**
```python
# Signal detecta: orden.status == 'DELIVERED'

Para cada producto en la orden:
  1. Extraer duración de warranty_info:
     - "1 año de garantía" → 365 días
     - "2 años de garantía" → 730 días
     - "6 meses de garantía" → 180 días
  
  2. Crear Warranty:
     - order: orden actual
     - product: producto del item
     - start_date: hoy
     - end_date: hoy + duración
     - status: 'ACTIVE'
     - terms: "Garantía del fabricante..."
```

**Resultado Final:**
```
Estado: DELIVERED
✅ Orden entregada
✅ Delivery completado
✅ Garantías creadas automáticamente (ACTIVE)
```

---

## 📊 Diagrama del Flujo

```
┌─────────────┐
│ 1. PENDING  │  Usuario crea orden
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   2. PAID   │  Stripe confirma pago
└──────┬──────┘
       │
       ▼ 🚀 SIGNAL: create_delivery_on_paid_order()
       │
┌─────────────────────────┐
│ Delivery Creado (AUTO)  │
│ Status: PENDING         │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Manager Asigna          │
│ Status: ASSIGNED        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Repartidor Recoge       │
│ Status: PICKED_UP       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Repartidor En Camino    │
│ Status: IN_TRANSIT      │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Repartidor Entrega      │
│ Status: DELIVERED       │
└────────┬────────────────┘
         │
         ▼ 🚀 SIGNAL: create_warranties_on_delivered_order()
         │
┌─────────────────────────┐
│ Garantías Creadas (AUTO)│
│ Status: ACTIVE          │
│ - 1 por cada producto   │
│ - Duración según info   │
└─────────────────────────┘
```

---

## 🧪 Probar el Flujo Completo

### **Opción 1: Script Automatizado**
```bash
python test_flujo_completo.py
```

Este script:
- ✅ Crea una orden
- ✅ La marca como PAID
- ✅ Verifica que se crea Delivery automáticamente
- ✅ Simula el proceso de entrega
- ✅ Verifica que se crean Garantías automáticamente
- ✅ Muestra resumen completo

### **Opción 2: Manualmente con API**

```bash
# 1. Login
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 2. Crear orden
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"product_id": 1, "quantity": 2}
    ]
  }'

# 3. Simular pago (marcar como PAID)
# En producción: Stripe hace esto automáticamente
curl -X PATCH http://localhost:8000/api/orders/1/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"status": "PAID"}'

# 4. Verificar que se creó delivery
curl -X GET http://localhost:8000/api/deliveries/deliveries/1/ \
  -H "Authorization: Bearer {token}"

# 5. Asignar repartidor
curl -X POST http://localhost:8000/api/deliveries/deliveries/1/assign_delivery/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"delivery_person_id": 1}'

# 6. Actualizar a DELIVERED
curl -X POST http://localhost:8000/api/deliveries/deliveries/1/update_delivery_status/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"status": "DELIVERED"}'

# 7. Verificar garantías creadas
curl -X GET "http://localhost:8000/api/deliveries/warranties/?order=1" \
  -H "Authorization: Bearer {token}"
```

---

## 🔍 Verificaciones

### **Verificar Delivery creado automáticamente:**
```python
# En Django shell
from shop_orders.models import Order
orden = Order.objects.get(id=1)

if hasattr(orden, 'delivery'):
    print("✅ Delivery existe!")
    print(f"Estado: {orden.delivery.status}")
else:
    print("❌ No se creó delivery")
```

### **Verificar Garantías creadas automáticamente:**
```python
# En Django shell
from shop_orders.models import Order
orden = Order.objects.get(id=1)

warranties = orden.warranties.all()
print(f"Garantías: {warranties.count()}")

for w in warranties:
    print(f"- {w.product.name}: hasta {w.end_date}")
```

---

## 📝 Archivos Modificados/Creados

### **Nuevos Archivos:**
```
deliveries/signals.py          ← Signals automáticos (NUEVO)
test_flujo_completo.py         ← Script de prueba (NUEVO)
FLUJO_GARANTIAS_DELIVERY.md    ← Este archivo (NUEVO)
```

### **Archivos Modificados:**
```
deliveries/apps.py             ← Agregado ready() para importar signals
```

---

## ✅ Ventajas del Sistema Automático

### **1. Sin Errores Humanos**
```
❌ Antes: Manager olvida crear delivery
✅ Ahora: Se crea automáticamente
```

### **2. Sin Pasos Manuales**
```
❌ Antes: Manager debe crear garantías manualmente
✅ Ahora: Se crean automáticamente al entregar
```

### **3. Consistencia Total**
```
❌ Antes: Algunas órdenes con garantía, otras sin
✅ Ahora: TODAS las órdenes entregadas tienen garantías
```

### **4. Escalabilidad**
```
❌ Antes: No escalable (trabajo manual)
✅ Ahora: Funciona con 1 o 10,000 órdenes/día
```

### **5. Auditoría Completa**
```
✅ Cada garantía tiene:
   - Fecha exacta de inicio/fin
   - Producto vinculado
   - Orden vinculada
   - Términos y condiciones
```

---

## 🎯 Casos de Uso Cubiertos

### **CU-16: Gestionar Delivery de Compras**
✅ Creación automática de delivery al pagar
✅ Asignación de repartidor
✅ Seguimiento en tiempo real
✅ Actualización de estados

### **CU-13: Gestionar Garantías de Productos**
✅ Creación automática al entregar
✅ Duración según especificaciones del producto
✅ Estados: ACTIVE, CLAIMED, EXPIRED, VOID
✅ Reclamación de garantías

### **CU-14: Gestionar Devoluciones**
✅ Vinculadas a garantías
✅ Aprobación de manager
✅ Cálculo de reembolso

### **CU-15: Gestionar Reparaciones**
✅ Vinculadas a garantías
✅ Con costo o sin costo (según garantía)
✅ Seguimiento de estado

---

## 🚀 Próximos Pasos (Opcional)

### **Mejoras Futuras:**
- [ ] Notificaciones push al cliente
- [ ] Tracking en tiempo real con GPS
- [ ] Estimación automática de tiempo de entrega
- [ ] Alertas de garantías por vencer
- [ ] Reporte de garantías por producto
- [ ] Dashboard de deliveries en tiempo real

---

## 📞 Troubleshooting

### **Problema: Delivery no se crea automáticamente**

**Solución:**
1. Verificar que signals están importados:
   ```python
   # deliveries/apps.py debe tener:
   def ready(self):
       import deliveries.signals
   ```

2. Verificar que la app está en INSTALLED_APPS:
   ```python
   # settings.py
   INSTALLED_APPS = [
       ...
       'deliveries',
       ...
   ]
   ```

3. Reiniciar servidor:
   ```bash
   python manage.py runserver
   ```

### **Problema: Garantías no se crean automáticamente**

**Solución:**
1. Verificar que orden tiene estado DELIVERED:
   ```python
   orden.status == 'DELIVERED'
   ```

2. Verificar que productos tienen warranty_info:
   ```python
   product.warranty_info  # Debe tener texto como "1 año de garantía"
   ```

3. Verificar en logs:
   ```
   ✅ Garantías creadas automáticamente para orden #123
   ```

---

## 🎉 Conclusión

El sistema de garantías y delivery está **COMPLETAMENTE INTEGRADO** y funciona de manera **100% AUTOMÁTICA**.

**No requiere intervención manual** para:
- ✅ Crear deliveries al pagar
- ✅ Crear garantías al entregar
- ✅ Actualizar estados
- ✅ Liberar repartidores

**El flujo está probado y funcional** end-to-end.

---

**Autor**: Sistema SmartSales365  
**Fecha**: Noviembre 2025  
**Estado**: ✅ COMPLETADO Y FUNCIONAL
