# � CARGAR ÓRDENES DELIVERED EN PRODUCCIÓN (Sin Shell de Render)

## 🎯 Objetivo

Crear órdenes en estado `DELIVERED` directamente en la base de datos de **producción en Render** desde tu computadora local, sin necesidad de usar el shell de Render (no disponible en plan gratuito).

---

## ✅ Solución: Script con Conexión Remota

### 🚀 MÉTODO: Ejecutar script localmente con conexión remota

El script `create_delivered_orders.py` ya está configurado para conectarse directamente a tu base de datos de producción en Render.

**Comando:**

```powershell
# Crear 10 órdenes DELIVERED en producción
python create_delivered_orders.py --production

# Crear más órdenes (ejemplo: 20)
python create_delivered_orders.py --production --num=20
```

---

## 📋 Lo que hace el script

```python
# El script automáticamente:
from shop_orders.models import Order, OrderItem
from products.models import Product
from users.models import CustomUser
import random

# Limpiar órdenes vacías
Order.objects.filter(total_price=0).delete()

# Crear órdenes con items
user = CustomUser.objects.get(username='admin')
products = list(Product.objects.all()[:10])
statuses = ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED']

for i in range(5):
    status = statuses[i % len(statuses)]
    order = Order.objects.create(user=user, status=status, total_price=0)
    
    num_items = random.randint(2, 4)
    total = 0
    
    for j in range(num_items):
        product = random.choice(products)
        quantity = random.randint(1, 3)
        price = product.price
        
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=price
        )
        
        total += price * quantity
    
    order.total_price = total
    order.save()
    print(f'✅ Orden #{order.id} - {order.status} - ${order.total_price}')

    order.total_price = total
    order.save()
    print(f'✅ Orden #{order.id} creada')

print('\n🎉 ¡Completado!')
```

---

## 📊 Ejemplo de Salida

```
🌐 Conectando a la base de datos de PRODUCCIÓN (Render)...
⚠️  ADVERTENCIA: Estás modificando la base de datos de PRODUCCIÓN
   Presiona ENTER para continuar o Ctrl+C para cancelar...

🚀 Creando órdenes DELIVERED para pruebas de devoluciones...

✅ Encontrados 14 usuarios
✅ Encontrados 76 productos activos

✅ Orden #668 creada:
   Usuario: juan@email.com
   Estado: DELIVERED
   Total: $4999.99
   Items: 1
   Fecha: 2025-11-07 02:17

...

🎉 ¡Completado! Se crearon 10 órdenes DELIVERED

📋 Resumen:
   - Total de órdenes: 10
   - Estado: DELIVERED (listas para devolución)
   - IDs de órdenes: [668, 669, 670, 671, 672, 673, 674, 675, 676, 677]
```

---

## ⚠️ IMPORTANTE

### **La base de datos es PERSISTENTE**
- ✅ Los datos NO se borran con cada deploy
- ✅ Las órdenes creadas permanecerán en la base de datos
- ✅ Puedes ejecutar el script cuantas veces quieras

### **Configuración del Script**

El script se conecta automáticamente a:
```
postgresql://ecommerce_db_k9tb_user:FTotph4caKAGtFwPAXSKVOtkXmJvg91E@dpg-d49llop5pdvs73d0dka0-a.oregon-postgres.render.com/ecommerce_db_k9tb
```

---

## 🧪 Probar el Sistema de Devoluciones

1. **Ve a tu frontend**: `https://web-2ex.vercel.app`
2. **Inicia sesión** con: `juan@email.com` (o cualquier usuario)
3. **Ve a "Mis Órdenes"**
4. **Busca órdenes DELIVERED**
5. **Haz clic en "Solicitar Devolución"**

---

## 🔄 Ejecutar Múltiples Veces

```powershell
# Crear 5 órdenes más
python create_delivered_orders.py --production --num=5

# Crear 15 órdenes más
python create_delivered_orders.py --production --num=15
```

---

## 🆘 Solución de Problemas

### **Error: "No module named 'django'"**
```powershell
pip install -r requirements.txt
```

### **Error: "could not connect to server"**
Verifica tu conexión a internet.

### **Error: "No hay usuarios"**
Primero crea usuarios:
```powershell
python seed_data.py
```

---

## ✅ Verificar Datos Creados

```powershell
# Ver total de órdenes DELIVERED
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings'); os.environ['DATABASE_URL'] = 'postgresql://ecommerce_db_k9tb_user:FTotph4caKAGtFwPAXSKVOtkXmJvg91E@dpg-d49llop5pdvs73d0dka0-a.oregon-postgres.render.com/ecommerce_db_k9tb'; django.setup(); from shop_orders.models import Order; print(f'Total DELIVERED: {Order.objects.filter(status=\"DELIVERED\").count()}')"
```
