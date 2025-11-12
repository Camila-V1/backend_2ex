# 🖼️ Poblar Imágenes en Producción - Sin Acceso a Shell

## ✅ Solución Implementada

Como NO tienes acceso al shell de Render, creamos un **endpoint API admin** que ejecuta la población desde tu máquina local.

---

## 📋 Cambios Realizados

### 1. Nuevo Endpoint API (Admin-Only)
**Archivo**: `products/populate_images_view.py`
- **URL**: `POST /api/products/populate-images/`
- **Permisos**: Solo administradores (`IsAdminUser`)
- **Función**: Actualiza los 76 productos con sus URLs de imágenes

### 2. Ruta Agregada
**Archivo**: `products/urls.py`
```python
path('populate-images/', populate_product_images, name='populate-images')
```

### 3. Script de Ejecución Local
**Archivo**: `populate_production_images.py`
- Solicita tu token de admin
- Llama al endpoint en producción
- Muestra estadísticas completas

---

## 🚀 Pasos para Ejecutar

### Paso 1: Deploy de Código a Render

```powershell
git add products/populate_images_view.py products/urls.py populate_production_images.py GUIA_POBLAR_IMAGENES_PRODUCCION.md
git commit -m "Add admin endpoint to populate product images in production"
git push origin main
```

**⏳ Espera 5-10 minutos** a que Render termine el deploy.

---

### Paso 2: Obtener Token de Admin

#### Opción A: Si ya tienes el token
- Búscalo en `CREDENCIALES_SISTEMA.md`
- O en tu respuesta de login previa

#### Opción B: Generar nuevo token

```powershell
# Crear script temporal
$loginScript = @'
import requests
import json

url = "https://backend-2ex-ecommerce.onrender.com/api/users/login/"
data = {
    "email": "admin@ecommerce.com",
    "password": "admin123"
}

response = requests.post(url, json=data)
if response.status_code == 200:
    tokens = response.json()
    print(f"Access Token: {tokens['access']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
'@

# Guardar y ejecutar
$loginScript | Out-File -FilePath "get_admin_token.py" -Encoding utf8
python get_admin_token.py
```

**Copia el Access Token** que aparece.

---

### Paso 3: Ejecutar Script de Población

```powershell
python populate_production_images.py
```

**El script te pedirá:**
1. Token de administrador (pegar el que copiaste)
2. Presionar Enter

**Salida esperada:**
```
======================================================================
🖼️  POBLADOR DE IMÁGENES EN PRODUCCIÓN
======================================================================

📝 Ingresa tu token de administrador:
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

🌐 Conectando a: https://backend-2ex-ecommerce.onrender.com/api/products/populate-images/
⏳ Enviando solicitud POST...

📡 Status Code: 200

======================================================================
✅ ÉXITO - IMÁGENES POBLADAS
======================================================================

📊 ESTADÍSTICAS:
   Total de productos:      76
   ✅ Con imagen:            76
   ❌ Sin imagen:            0
   📈 Porcentaje:            100.0%

📦 DETALLES DE ACTUALIZACIÓN:
   Actualizados:  76
   No encontrados: 0
   Errores:        0

🖼️  PRIMEROS PRODUCTOS ACTUALIZADOS:
   ✓ AirPods Pro 2
     URL: https://th.bing.com/th/id/OIP.SQCaci7ao_omgIOO1BCrRwHaMQ?w=500...
   ✓ Sony WH-1000XM5
     URL: https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=500...
   ...

======================================================================
🎉 PROCESO COMPLETADO
======================================================================

💡 Verifica con: python check_production_full.py
```

---

### Paso 4: Verificar Resultados

```powershell
python check_production_full.py
```

**Resultado esperado:**
```
📊 Total de productos: 76
✅ Con imagen: 76/76
📈 Porcentaje: 100.0%

✅ TODOS LOS PRODUCTOS TIENEN IMÁGENES
```

---

## 🔧 Solución de Problemas

### ❌ Error 401: Token inválido
**Causa**: Token expirado (duran 60 minutos)

**Solución**: Genera un nuevo token (Paso 2 - Opción B)

---

### ❌ Error 403: Sin permisos
**Causa**: El usuario no es administrador

**Solución**: Verifica credenciales en `CREDENCIALES_SISTEMA.md`
```
Email: admin@ecommerce.com
Password: admin123
```

---

### ⏱️ Timeout (60 segundos)
**Causa**: Render tardó mucho procesando

**Solución**: 
1. Espera 2-3 minutos
2. Ejecuta `python check_production_full.py`
3. Si aún salen 0 imágenes, vuelve a ejecutar el script

---

### 🌐 Connection Error
**Causa**: Sin internet o servidor caído

**Solución**:
1. Verifica tu conexión
2. Verifica que Render esté activo: https://backend-2ex-ecommerce.onrender.com/api/products/
3. Si Render está dormido, espera 2 minutos y reintenta

---

## 📊 Imágenes Incluidas

El endpoint poblará **76 productos** en estas categorías:

- **Audio**: 4 productos (AirPods, Sony WH-1000XM5, JBL, Bose)
- **Celulares**: 5 productos (iPhone 15, Samsung S24, Xiaomi, accesorios)
- **Computadoras**: 11 productos (MacBook, HP, Dell, monitores, periféricos)
- **Deportes**: 6 productos (smartwatch, bicicleta, mancuernas, caminadora)
- **Electrónica**: 7 productos (Smart TVs, tablets, Amazon Echo, Google Nest)
- **Fotografía**: 7 productos (Canon, Nikon, lentes, trípodes)
- **Gaming**: 8 productos (PS5, Xbox, Switch, controles, sillas)
- **Hogar**: 8 productos (aspiradora robot, cafetera, microondas)
- **Juguetes**: 5 productos (Hot Wheels, dron, Monopoly, LEGO)
- **Libros**: 5 productos (1984, Python, Atomic Habits)
- **Moda**: 4 productos (billetera, mochila, gafas, reloj)
- **Oficina**: 4 productos (organizador, lámpara, escritorio, silla)

**Total**: 76 productos con URLs de Bing Images y Unsplash

---

## ✅ Ventajas de Esta Solución

1. **No requiere acceso a Render Shell**
2. **Ejecutas desde tu máquina local**
3. **Protegido** (solo admins pueden usar el endpoint)
4. **Estadísticas completas** de la operación
5. **Reintentable** si algo falla
6. **Verificable** con script de chequeo

---

## 🎯 Resumen Rápido

```powershell
# 1. Deploy
git add products/populate_images_view.py products/urls.py populate_production_images.py GUIA_POBLAR_IMAGENES_PRODUCCION.md
git commit -m "Add admin endpoint to populate product images"
git push origin main

# 2. Esperar 5-10 minutos

# 3. Obtener token (si no lo tienes)
python get_admin_token.py

# 4. Poblar imágenes
python populate_production_images.py
# (Pegar token cuando lo solicite)

# 5. Verificar
python check_production_full.py
```

**Tiempo total**: ~15 minutos (incluyendo deploy)

---

## 📞 Notas Importantes

- **El endpoint es seguro**: Solo usuarios admin pueden usarlo
- **Es idempotente**: Puedes ejecutarlo múltiples veces sin problemas
- **No afecta otros datos**: Solo actualiza el campo `image_url`
- **Timeout de 60s**: Si tarda mucho, verifica manualmente después
- **Token expira en 60 min**: Si falla con 401, genera nuevo token

---

## ✨ Después de Completar

Tu API de productos devolverá:

```json
{
  "id": 1,
  "name": "PlayStation 5",
  "price": "10999.99",
  "image_url": "https://th.bing.com/th/id/OIP._GUSIeQTU3y4FgNi2pvlwgHaHa?w=500",
  "stock": 15,
  ...
}
```

**Frontend automáticamente mostrará las imágenes** 🎉
