# 🐛 Problemas Identificados: NLP y Flujo de Órdenes

## 📋 Resumen de Problemas

### ❌ Problema 1: NLP no reconoce productos
**Logs:**
```
POST /api/orders/cart/add-natural-language/ → 400 Bad Request
```

### ❌ Problema 2: Crea órdenes sin pagar
**Comportamiento:** El sistema crea la orden y reduce stock sin requerir pago.

---

## 🔍 Problema 1: NLP No Reconoce Lenguaje Común

### Causa Raíz
El servicio `CartNLPService` busca productos por coincidencia de texto, pero:

1. **Productos reales tienen nombres específicos:**
   - "Smart TV Samsung 55\""
   - "iPhone 15 Pro"
   - "Laptop Dell Inspiron 15"
   - "AirPods Pro 2"

2. **Usuario dice comandos genéricos:**
   - "agrega 2 laptops" ❌ No encuentra "Laptop Dell Inspiron 15"
   - "quiero 1 iphone" ❌ No encuentra "iPhone 15 Pro"
   - "añade smart tv" ✅ Podría funcionar parcialmente

### Código Problemático
```python
# shop_orders/nlp_service.py línea 160
@staticmethod
def _find_product(search_term, category=None):
    # Busca por coincidencia exacta (case-insensitive)
    product = Product.objects.filter(
        name__icontains=search_term,  # ← Problema aquí
        is_active=True
    ).first()
```

**Ejemplo:**
- Usuario: "agrega 2 laptops"
- NLP extrae: `search_term = "laptops"`
- Busca: `name__icontains="laptops"` 
- Resultado: NO encuentra "Laptop Dell Inspiron 15" (singular vs plural)

### Soluciones

#### Opción 1: Mejorar el Fuzzy Search (Recomendado)
```python
@staticmethod
def _find_product(search_term, category=None):
    """Búsqueda mejorada con singulares/plurales y sinónimos"""
    
    # Normalizar búsqueda (quitar plurales)
    search_normalized = search_term.rstrip('s').lower()
    
    # Buscar por palabras clave
    keywords = search_normalized.split()
    
    for keyword in keywords:
        if len(keyword) > 2:
            # Buscar en nombre
            product = Product.objects.filter(
                name__icontains=keyword,
                is_active=True
            ).first()
            
            if product:
                return product
            
            # Buscar en descripción
            product = Product.objects.filter(
                description__icontains=keyword,
                is_active=True
            ).first()
            
            if product:
                return product
    
    return None
```

#### Opción 2: Agregar Aliases a Productos
Agregar campo `keywords` al modelo Product:

```python
# products/models.py
class Product(models.Model):
    # ... campos existentes
    keywords = models.CharField(
        max_length=500,
        blank=True,
        help_text="Palabras clave separadas por comas para búsqueda NLP"
    )
    # Ejemplo: "laptop, computadora, portatil, notebook"
```

#### Opción 3: Sugerencias al Usuario
Si no se encuentra el producto, mostrar sugerencias:

```python
if not product:
    # Buscar productos similares
    suggestions = Product.objects.filter(
        name__icontains=keywords[0] if keywords else search_term[:4]
    )[:3]
    
    return Response({
        'error': f'No se encontró "{search_term}". ¿Quisiste decir?',
        'suggestions': [p.name for p in suggestions]
    })
```

---

## 🚨 Problema 2: Crea Órdenes Sin Pagar (CRÍTICO)

### ⚠️ Riesgo de Seguridad
El código actual:
1. ✅ Crea orden con status `PENDING`
2. ❌ **Reduce stock INMEDIATAMENTE** (línea 511)
3. ❌ NO requiere pago
4. ❌ Orden queda como completada sin transacción

### Código Problemático
```python
# shop_orders/views.py línea 511
for item in result['items']:
    product = Product.objects.get(id=item['product_id'])
    
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=item['quantity'],
        price=product.price
    )
    
    # ❌ PROBLEMA: Reduce stock sin pagar
    product.stock -= item['quantity']
    product.save()
```

### Consecuencias
1. **Fraude:** Usuario puede crear órdenes y no pagar, agotando stock
2. **Inventario incorrecto:** Stock reducido pero no hay venta real
3. **Pérdida de ventas:** Productos marcados como agotados sin haberse vendido

### Flujo Correcto vs Flujo Actual

#### ❌ Flujo Actual (INCORRECTO)
```
1. Usuario: "agrega 2 iphones"
2. Backend: Crea orden PENDING
3. Backend: Reduce stock (-2 iphones) ← PROBLEMA
4. Usuario: Cierra navegador sin pagar
5. Resultado: Stock reducido, orden sin pagar, pérdida de inventario
```

#### ✅ Flujo Correcto (DEBE SER)
```
1. Usuario: "agrega 2 iphones"
2. Backend: Crea orden PENDING
3. Backend: NO reduce stock todavía
4. Backend: Redirige a Stripe para pagar
5. Usuario: Paga con tarjeta
6. Stripe Webhook: Confirma pago
7. Backend: Cambia orden a PAID
8. Backend: Reduce stock (-2 iphones) ← AQUÍ
```

### Solución: Modificar CartNaturalLanguageView

```python
# shop_orders/views.py
class CartNaturalLanguageView(APIView):
    def post(self, request):
        # ... código existente ...
        
        if result['action'] == 'add' and result['items']:
            try:
                with transaction.atomic():
                    # ✅ 1. Validar stock (NO reducir todavía)
                    for item in result['items']:
                        product = Product.objects.get(id=item['product_id'])
                        if product.stock < item['quantity']:
                            return Response({
                                'error': f'Stock insuficiente para "{product.name}"'
                            }, status=400)
                    
                    # ✅ 2. Crear orden PENDING
                    order = Order.objects.create(
                        user=request.user,
                        status='PENDING'  # ← Sin pagar
                    )
                    
                    # ✅ 3. Crear items SIN reducir stock
                    total_price = 0
                    for item in result['items']:
                        product = Product.objects.get(id=item['product_id'])
                        
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=item['quantity'],
                            price=product.price
                        )
                        
                        # ❌ ELIMINAR ESTO:
                        # product.stock -= item['quantity']
                        # product.save()
                        
                        total_price += product.price * item['quantity']
                    
                    order.total_price = total_price
                    order.save()
                    
                    # ✅ 4. Crear sesión de Stripe
                    stripe_session = create_stripe_checkout_session(
                        order=order,
                        line_items=[...],
                        success_url=f"{FRONTEND_URL}/orders/{order.id}/success",
                        cancel_url=f"{FRONTEND_URL}/cart"
                    )
                    
                    # ✅ 5. Retornar URL de pago
                    return Response({
                        'success': True,
                        'message': 'Orden creada. Procede a pagar.',
                        'order_id': order.id,
                        'total': str(order.total_price),
                        'status': 'PENDING',
                        'payment_url': stripe_session.url,  # ← Usuario debe pagar aquí
                        'items': result['items']
                    }, status=201)
                    
            except Exception as e:
                return Response({'error': str(e)}, status=400)
```

### Dónde Reducir el Stock

**En el Webhook de Stripe cuando se confirma el pago:**

```python
# shop_orders/views.py - stripe_webhook()
@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook(request):
    # ... verificación del webhook ...
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session['metadata']['order_id']
        
        try:
            order = Order.objects.get(id=order_id)
            
            # Solo procesar si está PENDING
            if order.status == Order.OrderStatus.PENDING:
                # ✅ Reducir stock SOLO cuando se confirma el pago
                for item in order.items.all():
                    product = item.product
                    if product:
                        product.stock -= item.quantity
                        product.save()
                
                # Cambiar estado a PAID
                order.status = Order.OrderStatus.PAID
                order.save()
                
        except Order.DoesNotExist:
            return Response({'error': 'Orden no encontrada'}, status=404)
    
    return Response(status=200)
```

---

## 📊 Comparación de Flujos

| Acción | ❌ Actual (Incorrecto) | ✅ Correcto |
|--------|------------------------|-------------|
| Usuario crea orden NLP | Crea orden PENDING | Crea orden PENDING |
| Stock se reduce | ❌ Inmediatamente | ❌ NO todavía |
| Redirige a pago | ❌ NO (problema) | ✅ Sí, Stripe |
| Usuario paga | ❌ NO requerido | ✅ Requerido |
| Stripe confirma pago | ❌ No aplica | ✅ Webhook ejecuta |
| Stock se reduce | ❌ Ya reducido sin pago | ✅ Ahora SÍ reduce |
| Estado de orden | PENDING (sin pagar) | PAID (pagado) |

---

## 🎯 Recomendaciones Prioritarias

### 🔴 URGENTE (Problema 2 - Seguridad)
**Prioridad:** CRÍTICA
**Impacto:** Fraude, pérdida de inventario
**Solución:**
1. Modificar `CartNaturalLanguageView.post()` para NO reducir stock
2. Agregar integración con Stripe en respuesta NLP
3. Reducir stock solo en webhook cuando se confirma pago
4. **Tiempo estimado:** 2-3 horas

### 🟡 MEDIO (Problema 1 - UX)
**Prioridad:** MEDIA
**Impacto:** Usuario frustrado, conversión baja
**Solución:**
1. Mejorar fuzzy search con normalización de plurales
2. Agregar campo `keywords` al modelo Product
3. Poblar keywords en seed_data.py
4. Mostrar sugerencias si no se encuentra producto
5. **Tiempo estimado:** 3-4 horas

---

## 🧪 Testing

### Test 1: NLP Mejorado
```bash
POST /api/orders/cart/add-natural-language/
{
  "prompt": "agrega 2 laptops"
}

✅ Esperado: Encuentra "Laptop Dell Inspiron 15"
```

### Test 2: Flujo de Pago Correcto
```bash
# 1. Crear orden NLP
POST /api/orders/cart/add-natural-language/
{"prompt": "quiero 1 iphone"}

✅ Respuesta debe incluir: "payment_url"
✅ Stock NO debe reducirse todavía

# 2. Simular pago en Stripe
# 3. Webhook confirma pago
# 4. Verificar que stock ahora SÍ se redujo
GET /api/products/{iphone_id}/
✅ stock debe ser (stock_anterior - 1)
```

---

## 📁 Archivos a Modificar

1. **shop_orders/views.py** (líneas 460-540)
   - Modificar `CartNaturalLanguageView.post()`
   - Agregar integración con Stripe
   - NO reducir stock hasta webhook

2. **shop_orders/views.py** (líneas 190-220)
   - Modificar `stripe_webhook()`
   - Agregar reducción de stock aquí

3. **shop_orders/nlp_service.py** (líneas 150-180)
   - Mejorar `_find_product()`
   - Agregar normalización de plurales
   - Agregar búsqueda por keywords

4. **products/models.py**
   - Agregar campo `keywords` (opcional)

5. **seed_data.py**
   - Agregar keywords a productos (opcional)

---

## ✅ Checklist de Implementación

### Problema 2 (URGENTE):
- [ ] Eliminar reducción de stock en `CartNaturalLanguageView`
- [ ] Agregar creación de sesión Stripe en respuesta NLP
- [ ] Modificar webhook para reducir stock al confirmar pago
- [ ] Probar flujo completo: NLP → Stripe → Pago → Stock reducido
- [ ] Verificar que órdenes PENDING no afecten inventario

### Problema 1:
- [ ] Mejorar fuzzy search con plurales/singulares
- [ ] Agregar campo keywords a Product (opcional)
- [ ] Poblar keywords en productos existentes (opcional)
- [ ] Agregar sugerencias cuando no se encuentra producto
- [ ] Probar con comandos comunes: "laptops", "celulares", "audífonos"

---

**Nota:** El Problema 2 es CRÍTICO y debe resolverse antes de producción para evitar fraude y pérdida de inventario.
