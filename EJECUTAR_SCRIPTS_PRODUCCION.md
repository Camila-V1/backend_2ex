# 🚀 EJECUTAR SCRIPTS EN PRODUCCIÓN (RENDER)

## 📋 Instrucciones

### Paso 1: Abrir Shell en Render

1. Ve a https://dashboard.render.com/
2. Selecciona tu servicio **backend-2ex-ecommerce**
3. Click en el tab **"Shell"** (esquina superior derecha)
4. Se abrirá una terminal en el servidor

### Paso 2: Ejecutar Script de Imágenes

En la terminal de Render, ejecuta:

```bash
# Script con los 56 productos principales
python update_product_images_complete.py --production

# Script con los 18 productos restantes
python update_remaining_images.py
```

### Paso 3: Verificar

Ejecuta este comando en tu máquina local:

```bash
python check_production_full.py
```

Deberías ver: **76/76 productos con imágenes** ✅

---

## 🔄 Opción 2: Agregar al Deploy Script (Automático)

Si quieres que se ejecute automáticamente en cada deploy:

### Editar `build.sh` (si existe) o crear uno:

```bash
#!/usr/bin/env bash
# build.sh

set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Poblar imágenes de productos (solo si no existen)
python update_product_images_complete.py --production
python update_remaining_images.py

# Colectar archivos estáticos
python manage.py collectstatic --no-input
```

### Configurar en Render:

1. Dashboard de Render → Tu servicio
2. Settings → Build & Deploy
3. **Build Command**: `./build.sh`
4. Guarda cambios

---

## ⚡ Opción 3: API Endpoint (Más Fácil)

Puedes crear un endpoint admin-only para poblar imágenes:

```python
# products/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([IsAdminUser])
def populate_images(request):
    """Endpoint para poblar imágenes - solo admins"""
    
    # Diccionario de imágenes (copiar de update_product_images_complete.py)
    PRODUCT_IMAGES = {
        # ... todos los productos ...
    }
    
    updated = 0
    for product_name, image_url in PRODUCT_IMAGES.items():
        try:
            product = Product.objects.get(name=product_name)
            product.image_url = image_url
            product.save()
            updated += 1
        except Product.DoesNotExist:
            pass
    
    return Response({
        'message': 'Imágenes pobladas exitosamente',
        'updated': updated,
        'total': len(PRODUCT_IMAGES)
    })
```

Luego llamar desde tu máquina:

```bash
curl -X POST https://backend-2ex-ecommerce.onrender.com/api/products/populate-images/ \
  -H "Authorization: Bearer TU_TOKEN_ADMIN"
```

---

## 🎯 Recomendación

**Usa la Opción 1** (Shell de Render) - Es la más rápida y directa:

1. Abre Shell en Render
2. Ejecuta los 2 scripts
3. ¡Listo! 76 productos con imágenes

**Tiempo estimado:** 2 minutos ⏱️

---

## ✅ Verificación Final

Después de ejecutar, verifica con:

```bash
python check_production_full.py
```

Deberías ver:
```
✅ Con imagen: 76/76
📈 Porcentaje: 100.0%
🎉 ¡TODOS LOS PRODUCTOS TIENEN IMÁGENES!
```
