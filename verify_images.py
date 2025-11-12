import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from products.models import Product

# Verificar algunos productos
productos_muestra = [
    "PlayStation 5",
    "iPhone 15 Pro", 
    "MacBook Air M2",
    "Smart TV Samsung 55\"",
    "AirPods Pro 2"
]

print("\n🔍 VERIFICACIÓN DE PRODUCTOS CON IMÁGENES\n" + "="*60)

for nombre in productos_muestra:
    p = Product.objects.filter(name=nombre).first()
    if p:
        print(f"\n✅ {p.name}")
        print(f"   📷 Imagen: {p.image_url[:60]}...")
        print(f"   💰 Precio: ${p.price}")
        print(f"   📦 Stock: {p.stock}")
    else:
        print(f"❌ No encontrado: {nombre}")

print("\n" + "="*60)
total = Product.objects.count()
with_images = Product.objects.exclude(image_url__isnull=True).exclude(image_url='').count()
print(f"📊 Total: {total} productos | Con imágenes: {with_images} ({(with_images/total)*100:.0f}%)")
print("="*60 + "\n")
