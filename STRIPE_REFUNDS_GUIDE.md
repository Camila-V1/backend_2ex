# 💳 Sistema de Reembolsos con Stripe

## 📋 Descripción General

Sistema completo de reembolsos integrado con Stripe para procesar devoluciones de dinero a los clientes de forma automática cuando se aprueban sus solicitudes de devolución de productos.

## 🏗️ Arquitectura

### Componentes Principales

1. **Modelos de Datos** (`shop_orders/payment_models.py`):
   - `Payment`: Almacena información de pagos procesados
   - `Refund`: Rastrea todos los reembolsos realizados

2. **Servicio de Stripe** (`shop_orders/stripe_refund_service.py`):
   - `StripeRefundService`: Clase para interactuar con Stripe API
   - `process_return_refund_to_stripe()`: Función principal para procesar reembolsos

3. **Integración en Devoluciones** (`deliveries/views.py`):
   - `_process_refund()`: Método que maneja 3 tipos de reembolso
   - `approve()`: Acción que trigger el proceso de reembolso

## 📊 Modelos de Datos

### Payment Model

```python
class Payment(models.Model):
    order = models.OneToOneField(Order)  # Relación 1:1 con Order
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    stripe_charge_id = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(choices=PaymentStatus.choices)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    # Información adicional
    customer_email = models.EmailField(null=True, blank=True)
    payment_method_type = models.CharField(max_length=50, null=True)
    last4 = models.CharField(max_length=4, null=True)
```

**Estados del Payment:**
- `PENDING`: Pago pendiente
- `COMPLETED`: Pago completado exitosamente
- `FAILED`: Pago fallido
- `REFUNDED`: Completamente reembolsado
- `PARTIALLY_REFUNDED`: Parcialmente reembolsado

### Refund Model

```python
class Refund(models.Model):
    payment = models.ForeignKey(Payment, related_name='refunds')
    return_obj = models.ForeignKey('deliveries.Return', null=True)
    stripe_refund_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    reason = models.TextField(null=True, blank=True)
    status = models.CharField(choices=RefundStatus.choices)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    initiated_by = models.ForeignKey(User, null=True)
```

**Estados del Refund:**
- `PENDING`: Reembolso pendiente
- `PROCESSING`: En proceso
- `SUCCEEDED`: Exitoso
- `FAILED`: Fallido
- `CANCELLED`: Cancelado

## 🔄 Flujo de Reembolso

### 1. Cliente Solicita Devolución

```
POST /api/deliveries/returns/
{
  "order": 45,
  "product": 104,
  "quantity": 1,
  "reason": "Producto defectuoso"
}
```

**Estado**: `REQUESTED`

### 2. Manager Envía a Evaluación

```
POST /api/deliveries/returns/{id}/send_to_evaluation/
{
  "manager_notes": "Producto recibido en bodega"
}
```

**Estado**: `IN_EVALUATION`

### 3. Manager Aprueba Devolución

```
POST /api/deliveries/returns/{id}/approve/
{
  "evaluation_notes": "Producto confirmado defectuoso",
  "refund_amount": "299.99",
  "refund_method": "ORIGINAL"  // WALLET, ORIGINAL o BANK
}
```

**Estado**: `APPROVED` → `COMPLETED`

**Proceso Automático**:

#### Si refund_method = "ORIGINAL" (Stripe):

1. **Buscar Payment**: Se obtiene el `Payment` asociado a la orden
2. **Validar Payment**: Verifica que esté en estado `COMPLETED`
3. **Llamar a Stripe API**:
   ```python
   stripe.Refund.create(
       payment_intent='pi_xxx',
       amount=29999,  # En centavos
       reason='requested_by_customer',
       metadata={
           'return_id': 11,
           'order_id': 45,
           'product_id': 104,
           'customer_id': 15,
           'approved_by': 3
       }
   )
   ```
4. **Guardar Refund**: Crea registro en BD con:
   - `stripe_refund_id`
   - `amount`
   - `status` (mapeado de Stripe)
   - `initiated_by` (manager)
5. **Actualizar Payment**: Cambia estado a `REFUNDED` o `PARTIALLY_REFUNDED`
6. **Marcar Return**: Estado → `COMPLETED`
7. **Enviar Email**: Notifica al cliente

#### Si refund_method = "WALLET":

1. **Obtener/Crear Wallet**: `Wallet.objects.get_or_create(user=...)`
2. **Agregar Fondos**: `wallet.add_funds(amount, type='REFUND', ...)`
3. **Crear Transaction**: Registro en `WalletTransaction`
4. **Marcar Return**: Estado → `COMPLETED`
5. **Enviar Email**: Notifica al cliente

#### Si refund_method = "BANK":

1. **Registrar para Procesamiento Manual**: Marca para que finanzas procese
2. **Marcar Return**: Estado → `COMPLETED`
3. **Enviar Email**: Notifica que se procesará en 3-5 días hábiles

## 🔧 StripeRefundService

### Métodos Principales

#### 1. create_refund()

```python
result = StripeRefundService.create_refund(
    payment_intent_id='pi_xxx',
    amount=Decimal('299.99'),
    reason='requested_by_customer',
    metadata={'return_id': 11}
)
```

**Retorna**:
```python
{
    'success': True,
    'refund_id': 're_xxx',
    'amount': Decimal('299.99'),
    'status': 'succeeded',
    'charge_id': 'ch_xxx',
    'currency': 'usd',
    'created': 1699999999,
    'reason': 'requested_by_customer',
    'metadata': {...}
}
```

**Manejo de Errores**:
- `InvalidRequestError`: Payment intent no existe
- `CardError`: Problema con la tarjeta
- `AuthenticationError`: Error de API key
- `StripeError`: Error general

#### 2. retrieve_refund()

```python
result = StripeRefundService.retrieve_refund('re_xxx')
```

Obtiene información de un reembolso existente.

#### 3. cancel_refund()

```python
result = StripeRefundService.cancel_refund('re_xxx')
```

Cancela un reembolso pendiente (solo si no ha sido procesado).

#### 4. list_refunds()

```python
result = StripeRefundService.list_refunds(
    payment_intent_id='pi_xxx',
    limit=10
)
```

Lista todos los reembolsos de un payment intent.

## 🎯 Estados y Transiciones

### Payment Status Flow

```
PENDING → COMPLETED → PARTIALLY_REFUNDED → REFUNDED
           ↓
        FAILED
```

### Refund Status Flow

```
PENDING → PROCESSING → SUCCEEDED
           ↓              ↓
        FAILED      CANCELLED
```

## 📊 Admin Interface

### Payment Admin

**Lista**: Muestra pagos con filtros por estado, moneda, método
**Búsqueda**: Por order ID, email, stripe_payment_intent_id
**Campos readonly**: IDs de Stripe, timestamps

### Refund Admin

**Lista**: Muestra reembolsos con filtros por estado, moneda
**Búsqueda**: Por stripe_refund_id, order ID, return ID
**Permisos**: No permite crear reembolsos manualmente (solo vía API)

## 🔐 Seguridad y Validaciones

### Validaciones Pre-Refund

1. **Payment Existe**: Verifica que hay un `Payment` para la orden
2. **Payment Completado**: Solo reembolsa payments en estado `COMPLETED`
3. **Monto Válido**: `refund_amount <= payment.amount`
4. **Manager Autorizado**: Solo managers/admins pueden aprobar
5. **Estado Correcto**: Return debe estar en `IN_EVALUATION`

### Configuración Stripe

```python
# settings.py
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
```

### Variables de Entorno

```bash
# .env
STRIPE_SECRET_KEY=sk_test_[YOUR_SECRET_KEY_HERE]
STRIPE_PUBLISHABLE_KEY=pk_test_[YOUR_PUBLISHABLE_KEY_HERE]
STRIPE_WEBHOOK_SECRET=whsec_[YOUR_WEBHOOK_SECRET_HERE]
```

**Nota**: Obtén tus claves reales desde el [Stripe Dashboard](https://dashboard.stripe.com/apikeys)

## 📧 Notificaciones

### Email de Aprobación con Stripe

```
Asunto: Tu devolución ha sido aprobada - Return #11

Hola Juan,

¡Buenas noticias! Tu solicitud de devolución #11 ha sido aprobada.

Detalles del Reembolso:
- Monto: $299.99
- Método: Tarjeta original (terminada en 4242)
- Tiempo estimado: 5-10 días hábiles

El dinero será devuelto automáticamente a tu tarjeta.

Gracias por tu preferencia.
```

## 🧪 Testing

### Test de Refund Exitoso

```python
def test_stripe_refund_success():
    # 1. Crear Payment con stripe_payment_intent_id
    payment = Payment.objects.create(
        order=order,
        stripe_payment_intent_id='pi_test_xxx',
        amount=Decimal('299.99'),
        status='COMPLETED'
    )
    
    # 2. Aprobar return con método ORIGINAL
    response = client.post(
        f'/api/deliveries/returns/{return_id}/approve/',
        {
            'evaluation_notes': 'Aprobado',
            'refund_amount': '299.99',
            'refund_method': 'ORIGINAL'
        }
    )
    
    # 3. Verificar respuesta
    assert response.status_code == 200
    assert response.data['refund_status'] == 'success'
    
    # 4. Verificar Refund creado
    refund = Refund.objects.filter(payment=payment).first()
    assert refund is not None
    assert refund.status == 'SUCCEEDED'
    assert refund.amount == Decimal('299.99')
    
    # 5. Verificar Payment actualizado
    payment.refresh_from_db()
    assert payment.status == 'REFUNDED'
```

### Mock de Stripe para Testing

```python
from unittest.mock import patch

@patch('stripe.Refund.create')
def test_stripe_refund_mock(mock_create):
    # Mock respuesta de Stripe
    mock_create.return_value = {
        'id': 're_test_xxx',
        'amount': 29999,
        'status': 'succeeded',
        'charge': 'ch_test_xxx',
        'currency': 'usd',
        'created': 1699999999,
        'reason': 'requested_by_customer',
        'metadata': {}
    }
    
    # Ejecutar test...
```

## 📈 Métricas y Monitoreo

### Consultas SQL Útiles

```sql
-- Total reembolsado por mes
SELECT 
    DATE_TRUNC('month', created_at) as month,
    SUM(amount) as total_refunded,
    COUNT(*) as refund_count
FROM shop_orders_refund
WHERE status = 'SUCCEEDED'
GROUP BY month
ORDER BY month DESC;

-- Tasa de reembolsos por método
SELECT 
    r.refund_method,
    COUNT(*) as total_returns,
    SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
    SUM(r.refund_amount) as total_amount
FROM deliveries_return r
WHERE r.refund_method IS NOT NULL
GROUP BY r.refund_method;
```

### Dashboard Metrics

- **Total Reembolsado**: Suma de todos los refunds exitosos
- **Tiempo Promedio de Procesamiento**: Desde REQUESTED hasta COMPLETED
- **Tasa de Aprobación**: % de returns aprobados vs rechazados
- **Método Preferido**: WALLET vs ORIGINAL vs BANK

## 🚨 Troubleshooting

### Error: "Payment not found for order"

**Causa**: La orden no tiene un `Payment` asociado  
**Solución**: Crear manualmente el Payment o usar método WALLET

### Error: "Payment intent not found" (Stripe)

**Causa**: El `stripe_payment_intent_id` no existe en Stripe  
**Solución**: Verificar que el payment intent es válido y de la misma cuenta

### Error: "Charge already refunded"

**Causa**: Ya se procesó un reembolso completo para ese pago  
**Solución**: Verificar estado del Payment y Refunds existentes

### Refund en estado PENDING por mucho tiempo

**Causa**: Stripe está procesando el reembolso  
**Solución**: Webhooks de Stripe actualizarán el estado automáticamente

## 🔮 Próximas Mejoras

1. **Webhooks de Stripe**: Escuchar eventos `refund.updated`, `refund.succeeded`, `refund.failed`
2. **Reembolsos Parciales**: Permitir devolver solo parte del monto
3. **Dashboard de Finanzas**: Panel con métricas de reembolsos
4. **Notificaciones en Tiempo Real**: WebSockets para notificar managers
5. **Generación de Comprobantes**: PDF de reembolso para el cliente
6. **Integración con Contabilidad**: Export a QuickBooks/Xero

## 📚 Recursos

- [Stripe Refunds API Documentation](https://stripe.com/docs/api/refunds)
- [Best Practices for Refunds](https://stripe.com/docs/refunds)
- [Testing Refunds](https://stripe.com/docs/testing)

---

**Última Actualización**: 10 de Noviembre, 2025  
**Versión**: 1.0  
**Estado**: ✅ Producción Ready
