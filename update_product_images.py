"""
Script para agregar URLs de imágenes a los productos
Puedes editar este archivo y pegar las URLs que encuentres
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from products.models import Product


# 📝 INSTRUCCIONES:
# 1. Busca imágenes en Google Images, Unsplash, Pexels, etc.
# 2. Copia la URL de la imagen (botón derecho > Copiar dirección de imagen)
# 3. Pega la URL en el diccionario abajo
# 4. Ejecuta este script: python update_product_images.py

PRODUCT_IMAGES = {
    # ELECTRÓNICA
    "Smart TV Samsung 55\"": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=500",
    "Smart TV LG 43\"": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=500",
    "Tablet iPad Air": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=500",
    
    # COMPUTADORAS
    "Laptop Dell Inspiron 15": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500",
    "Laptop HP Pavilion": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500",
    "MacBook Air M2": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500",
    "Monitor LG 27\"": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500",
    "Teclado Mecánico RGB": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500",
    "Mouse Logitech MX Master": "https://images.unsplash.com/photo-1527814050087-3793815479db?w=500",
    
    # CELULARES
    "iPhone 15 Pro": "https://images.unsplash.com/photo-1592286927505-2fd22c0ce9b6?w=500",
    "Samsung Galaxy S24": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500",
    "Xiaomi Redmi Note 13": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500",
    
    # AUDIO
    "AirPods Pro 2": "https://images.unsplash.com/photo-1606841837239-c5a1a4a07af7?w=500",
    "Sony WH-1000XM5": "https://images.unsplash.com/photo-1545127398-14699f92334b?w=500",
    "JBL Flip 6": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=500",
    "Bose SoundLink Mini": "https://images.unsplash.com/photo-1589492477829-5e65395b66cc?w=500",
    
    # GAMING
    "PlayStation 5": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=500",
    "Xbox Series X": "https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=500",
    "Nintendo Switch OLED": "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=500",
    
    # FOTOGRAFÍA
    "Cámara Canon EOS R6": "https://images.unsplash.com/photo-1606853080792-dbc2c2fcf9f4?w=500",
    "Nikon Z5": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=500",
    
    # DEPORTES
    "Smartwatch Deportivo": "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500",
    
    # MODA
    "Zapatillas Nike Air Max": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500",
    "Zapatillas Adidas Ultraboost": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=500",
    
    # Si quieres agregar más productos, sigue este formato:
    # "Nombre exacto del producto": "URL_de_la_imagen",
}


def update_images(production=False):
    """
    Actualiza las URLs de imágenes de los productos
    """
    if production:
        print("\n⚠️  ADVERTENCIA: Modificarás la base de datos de PRODUCCIÓN")
        input("Presiona ENTER para continuar o Ctrl+C para cancelar...")
    
    print("\n" + "="*70)
    print("🖼️  ACTUALIZANDO IMÁGENES DE PRODUCTOS")
    print("="*70)
    
    updated_count = 0
    not_found = []
    
    for product_name, image_url in PRODUCT_IMAGES.items():
        try:
            product = Product.objects.get(name=product_name)
            product.image_url = image_url
            product.save()
            print(f"✅ {product_name[:50]:50s} -> Imagen actualizada")
            updated_count += 1
        except Product.DoesNotExist:
            not_found.append(product_name)
            print(f"❌ {product_name[:50]:50s} -> Producto no encontrado")
    
    print("\n" + "="*70)
    print("📊 RESUMEN")
    print("="*70)
    print(f"✅ Productos actualizados: {updated_count}")
    print(f"❌ Productos no encontrados: {len(not_found)}")
    
    if not_found:
        print("\n⚠️  Productos que no se encontraron en la BD:")
        for name in not_found:
            print(f"   - {name}")
    
    # Mostrar productos sin imagen
    products_without_image = Product.objects.filter(image_url__isnull=True) | Product.objects.filter(image_url='')
    if products_without_image.exists():
        print(f"\n📋 Productos que aún NO tienen imagen: {products_without_image.count()}")
        for p in products_without_image[:10]:
            print(f"   - {p.name}")
        if products_without_image.count() > 10:
            print(f"   ... y {products_without_image.count() - 10} más")
    
    print("\n✅ Actualización completada")


if __name__ == '__main__':
    import sys
    
    production = '--production' in sys.argv
    
    try:
        update_images(production=production)
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
