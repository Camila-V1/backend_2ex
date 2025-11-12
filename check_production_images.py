import requests
import json

# Verificar varios productos en producción
PRODUCTOS_MUESTRA = [410, 411, 412, 413, 414]  # PlayStation 5, iPhone, MacBook, etc.

print("\n🔍 VERIFICANDO IMÁGENES EN PRODUCCIÓN (Render)\n" + "="*60)

for product_id in PRODUCTOS_MUESTRA:
    try:
        url = f"https://backend-2ex-ecommerce.onrender.com/api/products/{product_id}/"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            image_status = "✅ SÍ" if data.get('image_url') else "❌ NO"
            
            print(f"\n{image_status} | ID: {product_id} | {data['name']}")
            if data.get('image_url'):
                print(f"      📷 {data['image_url'][:70]}...")
            print(f"      💰 ${data['price']}")
        else:
            print(f"\n❌ | ID: {product_id} | Error {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ | ID: {product_id} | Error: {str(e)}")

print("\n" + "="*60)
print("🔄 Si NO tienen imágenes, Render aún está desplegando...")
print("⏱️  Espera 5-10 minutos y vuelve a ejecutar este script")
print("="*60 + "\n")
