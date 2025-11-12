"""
Script para completar los 18 productos restantes sin imágenes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from products.models import Product

# Imágenes para los productos restantes
REMAINING_IMAGES = {
    # Juguetes (5)
    "Pista Hot Wheels": "https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=500",
    "Dron con Cámara HD": "https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=500",
    "Monopoly Edición Clásica": "https://images.unsplash.com/photo-1611891487253-0a3c98f5d703?w=500",
    "Cubo Rubik Original": "https://images.unsplash.com/photo-1591991731833-b8b2c09d93e9?w=500",
    "LEGO Star Wars Millennium Falcon": "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=500",
    
    # Libros (5)
    "1984 - George Orwell": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500",
    "Python Crash Course": "https://images.unsplash.com/photo-1526243741027-444d633d7365?w=500",
    "Atomic Habits": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500",
    "El Principito": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=500",
    "Clean Code - Robert Martin": "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=500",
    
    # Moda (4)
    "Billetera de Cuero": "https://images.unsplash.com/photo-1627123424574-724758594e93?w=500",
    "Mochila Deportiva Under Armour": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500",
    "Gafas de Sol Ray-Ban": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=500",
    "Reloj Casio G-Shock": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=500",
    
    # Oficina (4)
    "Organizador Escritorio": "https://images.unsplash.com/photo-1611269154421-4e27233ac5c7?w=500",
    "Lámpara LED Escritorio": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=500",
    "Escritorio Ajustable": "https://images.unsplash.com/photo-1595515106969-1ce29566ff1c?w=500",
    "Silla Ergonómica Oficina": "https://images.unsplash.com/photo-1580480055273-228ff5388ef8?w=500",
}

def update_remaining():
    """Actualiza los productos restantes"""
    print("\n" + "="*70)
    print("🖼️  COMPLETANDO IMÁGENES DE PRODUCTOS RESTANTES")
    print("="*70)
    
    updated_count = 0
    not_found = []
    
    for product_name, image_url in REMAINING_IMAGES.items():
        try:
            product = Product.objects.get(name=product_name)
            product.image_url = image_url
            product.save()
            print(f"✅ {product_name}")
            updated_count += 1
        except Product.DoesNotExist:
            not_found.append(product_name)
            print(f"❌ No encontrado: {product_name}")
    
    print("\n" + "="*70)
    print(f"✅ Productos actualizados: {updated_count}")
    print(f"❌ Productos no encontrados: {len(not_found)}")
    
    # Verificar productos sin imagen
    products_without_image = Product.objects.filter(image_url__isnull=True) | Product.objects.filter(image_url='')
    print(f"\n📋 Productos TOTALES sin imagen ahora: {products_without_image.count()}")
    
    # Estadísticas totales
    total_products = Product.objects.count()
    products_with_image = Product.objects.exclude(image_url__isnull=True).exclude(image_url='').count()
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   Total productos: {total_products}")
    print(f"   Con imagen: {products_with_image}")
    print(f"   Sin imagen: {total_products - products_with_image}")
    print(f"   Porcentaje completado: {(products_with_image/total_products)*100:.1f}%")
    print("="*70)

if __name__ == "__main__":
    update_remaining()
