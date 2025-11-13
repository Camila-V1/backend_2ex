# 📱 Guía: Payment Intent para App Móvil Flutter

Esta guía explica cómo implementar pagos con Stripe en tu app Flutter usando el nuevo endpoint de Payment Intent.

---

## 🎯 Resumen

**Backend Django** ahora soporta pagos tanto para:
- 🌐 **Web**: Checkout Session → Redirige a página de Stripe
- 📱 **Móvil**: Payment Intent → Payment Sheet nativo en la app

---

## 🔧 Cambios en el Backend

### 1. Nuevo Endpoint: `/api/orders/create-payment-intent/`

**URL**: `POST https://backend-2ex-ecommerce.onrender.com/api/orders/create-payment-intent/`

**Request**:
```json
{
    "order_id": 123,
    "currency": "usd"  // Opcional, por defecto "usd"
}
```

**Response**:
```json
{
    "client_secret": "pi_xxx_secret_xxx",
    "publishable_key": "pk_test_xxx",
    "order_id": 123,
    "amount": 5999,  // En centavos (59.99 USD)
    "currency": "usd"
}
```

**Validaciones**:
- ✅ Usuario autenticado (token JWT requerido)
- ✅ La orden debe existir y pertenecer al usuario
- ✅ La orden debe estar en estado `PENDING`
- ✅ El monto debe ser mayor a 0

---

### 2. Webhook Actualizado

El webhook ahora maneja **dos tipos de eventos**:

| Evento | Origen | Descripción |
|--------|--------|-------------|
| `checkout.session.completed` | Web | Checkout Session completada |
| `payment_intent.succeeded` | Móvil | Payment Intent exitoso |

Ambos eventos:
1. Verifican el `order_id` en metadata
2. Reducen el stock de productos
3. Cambian el estado de la orden a `PAID`

---

## 📱 Implementación en Flutter

### Paso 1: Instalar Dependencias

En tu `pubspec.yaml`:

```yaml
dependencies:
  flutter_stripe: ^10.1.0
  http: ^1.1.0
```

Ejecuta:
```bash
flutter pub get
```

---

### Paso 2: Inicializar Stripe

En tu `main.dart`:

```dart
import 'package:flutter_stripe/flutter_stripe.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // ⚠️ IMPORTANTE: Usa la clave pública que devuelve el endpoint
  // O configúrala aquí directamente
  Stripe.publishableKey = 'pk_test_TU_CLAVE_PUBLICA';
  
  runApp(MyApp());
}
```

---

### Paso 3: Crear Servicio de Pago

Crea un archivo `services/payment_service.dart`:

```dart
import 'package:flutter_stripe/flutter_stripe.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class PaymentService {
  final String baseUrl = 'https://backend-2ex-ecommerce.onrender.com/api';
  
  /// Procesa el pago de una orden usando Stripe Payment Intent
  Future<bool> processPayment({
    required int orderId,
    required String accessToken,
    String currency = 'usd',
  }) async {
    try {
      // 1️⃣ Obtener el client_secret desde tu backend
      print('📡 Creando Payment Intent para orden $orderId...');
      final paymentIntentResponse = await http.post(
        Uri.parse('$baseUrl/orders/create-payment-intent/'),
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'order_id': orderId,
          'currency': currency,
        }),
      );

      if (paymentIntentResponse.statusCode != 200) {
        final error = json.decode(paymentIntentResponse.body);
        print('❌ Error al crear Payment Intent: ${error['error']}');
        throw Exception(error['error'] ?? 'Error desconocido');
      }

      final paymentIntentData = json.decode(paymentIntentResponse.body);
      final clientSecret = paymentIntentData['client_secret'];
      
      print('✅ Payment Intent creado: ${clientSecret.substring(0, 20)}...');

      // 2️⃣ Inicializar el Payment Sheet
      print('🎨 Inicializando Payment Sheet...');
      await Stripe.instance.initPaymentSheet(
        paymentSheetParameters: SetupPaymentSheetParameters(
          paymentIntentClientSecret: clientSecret,
          merchantDisplayName: 'Tu Tienda',
          style: ThemeMode.light, // o ThemeMode.dark
        ),
      );

      print('✅ Payment Sheet inicializado');

      // 3️⃣ Mostrar el Payment Sheet al usuario
      print('📱 Presentando Payment Sheet...');
      await Stripe.instance.presentPaymentSheet();

      print('✅ ¡Pago completado exitosamente!');
      return true;

    } on StripeException catch (e) {
      print('❌ Error de Stripe: ${e.error.message}');
      
      // Manejar diferentes tipos de errores
      if (e.error.code == FailureCode.Canceled) {
        print('ℹ️ Usuario canceló el pago');
      } else {
        print('⚠️ Error: ${e.error.localizedMessage}');
      }
      return false;
      
    } catch (e) {
      print('❌ Error general: $e');
      return false;
    }
  }
}
```

---

### Paso 4: Usar en tu Widget

Ejemplo de uso en un botón de pago:

```dart
import 'package:flutter/material.dart';
import '../services/payment_service.dart';

class CheckoutScreen extends StatefulWidget {
  final int orderId;
  final String accessToken;

  const CheckoutScreen({
    required this.orderId,
    required this.accessToken,
  });

  @override
  _CheckoutScreenState createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends State<CheckoutScreen> {
  final PaymentService _paymentService = PaymentService();
  bool _isProcessing = false;

  Future<void> _handlePayment() async {
    setState(() => _isProcessing = true);

    try {
      final success = await _paymentService.processPayment(
        orderId: widget.orderId,
        accessToken: widget.accessToken,
        currency: 'usd',
      );

      if (success) {
        // ✅ Pago exitoso
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✅ ¡Pago completado exitosamente!'),
            backgroundColor: Colors.green,
          ),
        );

        // Redirigir a pantalla de éxito
        Navigator.pushReplacementNamed(
          context,
          '/payment-success',
          arguments: widget.orderId,
        );
      } else {
        // ❌ Pago cancelado o fallido
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Pago cancelado o fallido'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('❌ Error: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() => _isProcessing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Checkout')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('Orden #${widget.orderId}'),
            SizedBox(height: 20),
            
            ElevatedButton.icon(
              onPressed: _isProcessing ? null : _handlePayment,
              icon: _isProcessing 
                ? SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : Icon(Icons.credit_card),
              label: Text(_isProcessing ? 'Procesando...' : 'Pagar con Tarjeta'),
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## 🔄 Flujo Completo

```
📱 APP FLUTTER
│
├─ 1. Usuario crea orden
│     POST /api/orders/create/
│     Respuesta: { "id": 123, "total_price": "59.99", ... }
│
├─ 2. Usuario presiona "Pagar"
│     Llamar a payment_service.processPayment()
│
├─ 3. App solicita Payment Intent
│     POST /api/orders/create-payment-intent/
│     Body: { "order_id": 123 }
│     Respuesta: { "client_secret": "pi_xxx...", ... }
│
├─ 4. App inicializa Payment Sheet
│     Stripe.instance.initPaymentSheet(
│       paymentIntentClientSecret: clientSecret
│     )
│
├─ 5. Usuario ingresa datos de tarjeta
│     Stripe.instance.presentPaymentSheet()
│     [Sheet nativo de Stripe se muestra]
│
├─ 6. Stripe procesa el pago
│     [Comunicación directa: Stripe ↔ Banco]
│
├─ 7. ✅ Pago exitoso
│     Stripe envía evento a webhook
│
└─ 8. Backend actualiza orden
      🌐 Webhook recibe: payment_intent.succeeded
      ✅ Reduce stock de productos
      ✅ Cambia estado a PAID
      ✅ Usuario puede ver orden completada
```

---

## 🧪 Testing

### Tarjetas de Prueba de Stripe

Para probar en modo test, usa estas tarjetas:

| Tarjeta | Comportamiento |
|---------|----------------|
| `4242 4242 4242 4242` | ✅ Pago exitoso |
| `4000 0000 0000 9995` | ❌ Pago declinado (fondos insuficientes) |
| `4000 0000 0000 9987` | ❌ Pago declinado (tarjeta perdida) |
| `4000 0025 0000 3155` | 🔐 Requiere autenticación 3D Secure |

**Detalles adicionales** (cualquier valor válido):
- **Fecha de expiración**: Cualquier fecha futura (ej: 12/34)
- **CVC**: Cualquier 3 dígitos (ej: 123)
- **ZIP Code**: Cualquier código postal (ej: 12345)

---

## 🔒 Seguridad

### ✅ Buenas Prácticas Implementadas

1. **Autenticación JWT**: Solo usuarios autenticados pueden crear Payment Intents
2. **Validación de propiedad**: Solo el dueño de la orden puede pagar
3. **Verificación de estado**: Solo órdenes `PENDING` pueden ser pagadas
4. **Webhook firmado**: Stripe valida que los eventos son legítimos
5. **Idempotencia**: No se procesa la misma orden dos veces

### ⚠️ Consideraciones

- **No almacenes** el `client_secret` permanentemente
- **No expongas** tu `STRIPE_SECRET_KEY` en el frontend
- **Valida siempre** en el webhook antes de actualizar la orden
- **Usa HTTPS** en producción (Render ya lo tiene configurado)

---

## 🐛 Troubleshooting

### Error: "Missing Stripe signature header"

**Causa**: El webhook no está recibiendo la firma de Stripe

**Solución**:
1. Verifica que el webhook esté configurado en Stripe Dashboard
2. URL: `https://backend-2ex-ecommerce.onrender.com/api/orders/stripe-webhook/`
3. Evento: `payment_intent.succeeded`

---

### Error: "Orden no encontrada o ya ha sido procesada"

**Causa**: La orden no existe, no pertenece al usuario, o ya fue pagada

**Solución**:
- Verifica que `order_id` sea correcto
- Verifica que el token JWT sea válido
- Verifica que la orden esté en estado `PENDING`

---

### Payment Sheet no se muestra

**Causa**: `initPaymentSheet` falló

**Solución**:
1. Verifica que `Stripe.publishableKey` esté configurado
2. Verifica que `client_secret` sea válido
3. Revisa los logs de consola para más detalles

---

### Pago exitoso pero orden no se actualiza

**Causa**: Webhook no está configurado o falló

**Solución**:
1. Verifica en Stripe Dashboard → Webhooks → Eventos
2. Verifica que el evento `payment_intent.succeeded` se esté enviando
3. Revisa los logs del servidor de Render

---

## 📊 Configuración en Stripe Dashboard

### 1. Crear Webhook

1. Ir a: https://dashboard.stripe.com/test/webhooks
2. Click en **"Add endpoint"**
3. **Endpoint URL**: `https://backend-2ex-ecommerce.onrender.com/api/orders/stripe-webhook/`
4. **Eventos a escuchar**:
   - ✅ `checkout.session.completed` (para web)
   - ✅ `payment_intent.succeeded` (para móvil)
5. Copiar el **Signing secret** (`whsec_xxx`)
6. Actualizar en Render: Variable de entorno `STRIPE_WEBHOOK_SECRET`

---

### 2. Verificar Claves

En: https://dashboard.stripe.com/test/apikeys

**Claves necesarias**:
- 🔑 **Publishable key** (`pk_test_xxx`): Para Flutter/Frontend
- 🔐 **Secret key** (`sk_test_xxx`): Para Django Backend
- 📝 **Webhook secret** (`whsec_xxx`): Para validar webhooks

---

## 🚀 Deployment Checklist

- [x] **Backend Django**: Endpoint `/api/orders/create-payment-intent/` creado
- [x] **Webhook**: Actualizado para manejar `payment_intent.succeeded`
- [ ] **Stripe Dashboard**: Webhook configurado con URL correcta
- [ ] **Variables de entorno**: `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
- [ ] **Flutter**: Dependencia `flutter_stripe` instalada
- [ ] **Flutter**: `PaymentService` implementado
- [ ] **Flutter**: UI de checkout creada
- [ ] **Testing**: Probar con tarjetas de prueba

---

## 📚 Recursos Adicionales

- **Stripe Docs Flutter**: https://stripe.com/docs/payments/accept-a-payment?platform=flutter
- **flutter_stripe Package**: https://pub.dev/packages/flutter_stripe
- **Stripe Test Cards**: https://stripe.com/docs/testing#cards
- **Webhook Testing**: https://stripe.com/docs/webhooks/test

---

## 🎯 Próximos Pasos

1. **Deploy del Backend**:
   ```bash
   git add .
   git commit -m "feat: agregar endpoint Payment Intent para app móvil"
   git push origin main
   ```

2. **Configurar Webhook en Stripe** (ver sección arriba)

3. **Implementar en Flutter** usando el código de ejemplo

4. **Testing completo** con tarjetas de prueba

5. **Producción**: Cambiar a claves de producción cuando esté listo

---

**Última actualización**: 12 de noviembre de 2025  
**Endpoint**: `POST /api/orders/create-payment-intent/`  
**Webhook**: Maneja `checkout.session.completed` y `payment_intent.succeeded`  
**Estado**: ✅ Listo para usar
