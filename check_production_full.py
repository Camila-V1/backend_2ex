import requests
import json

print("\n🔍 VERIFICANDO PRODUCTOS EN PRODUCCIÓN\n" + "="*60)

try:
    # Obtener lista de productos
    url = "https://backend-2ex-ecommerce.onrender.com/api/products/"
    response = requests.get(url, timeout=15)
    
    if response.status_code == 200:
        products = response.json()
        
        print(f"\n📊 Total de productos: {len(products)}")
        print("\n🖼️  VERIFICANDO IMÁGENES:")
        print("-" * 60)
        
        with_images = 0
        without_images = 0
        
        # Mostrar primeros 10 productos
        for i, product in enumerate(products[:10]):
            has_image = bool(product.get('image_url'))
            if has_image:
                with_images += 1
                status = "✅"
            else:
                without_images += 1
                status = "❌"
            
            print(f"\n{status} ID: {product['id']:3d} | {product['name'][:40]}")
            if has_image:
                print(f"    📷 {product['image_url'][:65]}...")
            print(f"    💰 ${product['price']}")
        
        # Contar todas las imágenes
        total_with_images = sum(1 for p in products if p.get('image_url'))
        total_without_images = len(products) - total_with_images
        
        print("\n" + "="*60)
        print(f"📊 ESTADÍSTICAS TOTALES:")
        print(f"   ✅ Con imagen: {total_with_images}/{len(products)}")
        print(f"   ❌ Sin imagen: {total_without_images}/{len(products)}")
        print(f"   📈 Porcentaje: {(total_with_images/len(products)*100):.1f}%")
        
        if total_with_images == len(products):
            print("\n🎉 ¡TODOS LOS PRODUCTOS TIENEN IMÁGENES!")
        elif total_with_images > 0:
            print("\n⚠️  Algunos productos tienen imágenes. Render puede estar desplegando...")
        else:
            print("\n❌ NO HAY PRODUCTOS CON IMÁGENES")
            print("   🔄 Render aún está aplicando las migraciones y datos")
            print("   ⏱️  Espera 5-10 minutos más")
        
        print("="*60 + "\n")
        
    else:
        print(f"❌ Error al obtener productos: {response.status_code}")
        print(f"   Respuesta: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Error de conexión: {str(e)}")
    print("\n⚠️  Posibles causas:")
    print("   - Render está reiniciando")
    print("   - Problemas de red")
    print("   - Servicio temporalmente no disponible")
