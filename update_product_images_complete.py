"""
Script para agregar URLs de imágenes a TODOS los productos usando links de Bing
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from products.models import Product

PRODUCT_IMAGES = {
    # Audio (4)
    "AirPods Pro 2": "https://th.bing.com/th/id/OIP.SQCaci7ao_omgIOO1BCrRwHaMQ?w=500",
    "Sony WH-1000XM5": "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=500",
    "JBL Flip 6": "https://th.bing.com/th/id/OIP.R8rQgk5mnPmmVevzSE6cwwHaHa?w=500",
    "Bose SoundLink Mini": "https://th.bing.com/th/id/OIP.pX3hHLiur11lTdWrF8MOgQHaGT?w=500",
    
    # Celulares (5)
    "iPhone 15 Pro": "https://th.bing.com/th?q=iPhone+15+Pro+Azul+Oscuro&w=500",
    "Samsung Galaxy S24": "https://th.bing.com/th/id/OIP.6s8d317ufjfqV3hvFRs7dwHaJW?w=500",
    "Xiaomi Redmi Note 13": "https://th.bing.com/th/id/OIP.fxAQwWZc4PjdI30JyiyHPgHaHa?w=500",
    "Funda iPhone Protectora": "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=500",
    "Cargador Rápido 65W": "https://th.bing.com/th/id/OIP.RoixjZcbXZaoTu6x1aWEwgHaHD?w=500",
    
    # Computadoras (11)
    "MacBook Air M2": "https://th.bing.com/th/id/OIP.z0ATztHK_koH9KGMP3A_PAHaE8?w=500",
    "Laptop HP Pavilion": "https://th.bing.com/th/id/OIP.KFUvmuY519ADxrYvi1hcJgHaFc?w=500",
    "Laptop Dell Inspiron 15": "https://th.bing.com/th/id/OIP.pj9jvsYQZZOg2DUwQsv7twHaHa?w=500",
    "Monitor LG 27\"": "https://th.bing.com/th/id/OIP.fdXZHGay2PpwEiDeWEDRywHaFy?w=500",
    "Teclado Mecánico RGB": "https://th.bing.com/th/id/OIP.bPl3R1qP-Agt5mcttILp1QHaEK?w=500",
    "Mouse Logitech MX Master": "https://th.bing.com/th/id/OIP.GHwTewiM6uJB99b5iS3NaQHaHa?w=500",
    "SSD Samsung 1TB": "https://th.bing.com/th/id/OIP.QLHmuImekQzL1stKT8rHZgHaHa?w=500",
    "Disco Duro Externo 2TB": "https://th.bing.com/th/id/OIP.hn1gS7jwdEI8H7f5_BFXRAHaHa?w=500",
    "Webcam Logitech C920": "https://th.bing.com/th/id/OIP.14YYiVGZ5VzWTIP-WOwdoQHaGX?w=500",
    "Hub USB-C 7 en 1": "https://th.bing.com/th/id/OIP.8nzN9qDfr5XWoHnE9puiqgHaHa?w=500",
    "Alfombrilla RGB XXL": "https://th.bing.com/th/id/OIP.CYsIbQzknBbAOGlElLijfwHaHa?w=500",
    
    # Deportes (6)
    "Smartwatch Deportivo": "https://th.bing.com/th/id/OIP.aTN2znhBzYISrTBfCNJ0WgHaH5?w=500",
    "Bicicleta Estática": "https://th.bing.com/th/id/OIP.1iJkLNj1jGCYXvZXOzW1KgHaHa?w=500",
    "Mancuernas Ajustables": "https://th.bing.com/th/id/OIP.2ylRdpXZPHXSMyf4pYMzggHaHa?w=500",
    "Banda Elástica Set": "https://th.bing.com/th/id/OIP.RnK-1BLlyM1NDRnTS0VwKgHaE8?w=500",
    "Caminadora Profesional": "https://th.bing.com/th/id/OIP.jbkmvnoQ99ZhsprP-fZGQQHaGE?w=500",
    "Pelota de Yoga": "https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=500",
    
    # Electrónica (7)
    "Smart TV Samsung 55\"": "https://th.bing.com/th/id/OIP.sZFVfVuZ4GyjW9ao6OCtwwHaHa?w=500",
    "Smart TV LG 43\"": "https://th.bing.com/th/id/OIP.T69N77PYMv0z7lRZL7NFPAHaE6?w=500",
    "Tablet iPad Air": "https://th.bing.com/th/id/OIP.xf4ZPWYTW7nKrrROxEXLUgHaHa?w=500",
    "Amazon Echo Dot 5": "https://tse3.mm.bing.net/th/id/OIP.ESO2INXhaqQULsGkUxpF5wAAAA?w=500",
    "Google Nest Hub": "https://images.unsplash.com/photo-1543512214-318c7553f230?w=500",
    "Ring Video Doorbell": "https://th.bing.com/th/id/OIP.pU9M-sN3ChSTZwfoXQjV9wHaEK?w=500",
    "Chromecast con Google TV": "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=500",
    
    # Fotografía (7)
    "Cámara Canon EOS R6": "https://th.bing.com/th/id/OIP.4Fk568uPYh7qLLj4bzOLugHaHa?w=500",
    "Nikon Z5": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=500",
    "Lente Canon RF 24-70mm": "https://th.bing.com/th/id/OIP.SB1AzkGblypUfw5D54nLwQAAAA?w=500",
    "Trípode Profesional": "https://th.bing.com/th/id/OIP.QcEVqrqY_LZ7z20VVlMNiAHaIN?w=500",
    "Flash Externo": "https://th.bing.com/th/id/OIP.G8yIyxrWS2R0METrU1cMeQHaFf?w=500",
    "Mochila Fotográfica": "https://th.bing.com/th/id/OIP.xLNFJkNNBeGoTxcRTiyi7wHaE8?w=500",
    "Tarjeta SD 128GB": "https://th.bing.com/th/id/OIP.tyCL668m9lyuxnntxe0K5gHaHe?w=500",
    
    # Gaming (8)
    "PlayStation 5": "https://th.bing.com/th/id/OIP._GUSIeQTU3y4FgNi2pvlwgHaHa?w=500",
    "Xbox Series X": "https://th.bing.com/th/id/OIP.sfxGU57tjIMQVUEweM9VkQHaEn?w=500",
    "Nintendo Switch OLED": "https://th.bing.com/th/id/OIP.LyrQeajRxYOUk6z2wMml_AHaEK?w=500",
    "Control DualSense PS5": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=500",
    "Silla Gaming RGB": "https://th.bing.com/th/id/OIP.HM7CvBit7UQ79XuzvpkrOAHaHa?w=500",
    "Auriculares SteelSeries Arctis": "https://th.bing.com/th/id/OIP.zNvUR0qsiN5nbgum1_ZsjAHaHa?w=500",
    "Micrófono HyperX QuadCast": "https://th.bing.com/th/id/OIP.sAY0Luc4QlJo-3poYtwDSQHaHa?w=500",
    "Volante Logitech G29": "https://th.bing.com/th/id/OIP.04osWjaAmvrnlrmIxLEPqwHaFK?w=500",
    
    # Hogar (8)
    "Aspiradora Robot": "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=500",
    "Cafetera Express": "https://th.bing.com/th/id/OIP.VxDXIGxGCrdy2jLzKtQX1QHaHa?w=500",
    "Microondas Digital": "https://th.bing.com/th/id/OIP.7_tAZu6_Qp3JEmfobzS-TgHaHa?w=500",
    "Licuadora Premium": "https://th.bing.com/th/id/OIP.mQ0HAz7hNabDYQBUfs4SYAHaHa?w=500",
    "Purificador de Aire Xiaomi": "https://th.bing.com/th/id/OIP._86iLEtjqgp1GVx_Rdn9rAHaHa?w=500",
    "Ventilador de Torre": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500",
    "Humidificador Ultrasónico": "https://th.bing.com/th/id/OIP.e5FBiTc72IPZnxd2VT6IhwHaE8?w=500",
    "Termostato Inteligente": "https://th.bing.com/th/id/OIP.g6nXbtmg_JGQH8sdjiHPWAHaHa?w=500",
}

def update_images(production=False):
    """Actualiza las URLs de imágenes de los productos"""
    if production:
        print("\n⚠️  ADVERTENCIA: Modificarás la base de datos de PRODUCCIÓN")
        input("Presiona ENTER para continuar o Ctrl+C para cancelar...")
    
    print("\n" + "="*70)
    print("🖼️  ACTUALIZANDO IMÁGENES DE PRODUCTOS CON LINKS DE BING")
    print("="*70)
    
    updated_count = 0
    not_found = []
    
    for product_name, image_url in PRODUCT_IMAGES.items():
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
    
    # Productos sin imagen
    products_without_image = Product.objects.filter(image_url__isnull=True) | Product.objects.filter(image_url='')
    print(f"\n📋 Productos que AÚN NO tienen imagen: {products_without_image.count()}")
    
    if products_without_image.exists():
        print("\nProductos sin imagen:")
        for p in products_without_image:
            print(f"  - {p.name} (Categoría: {p.category.name if p.category else 'Sin categoría'})")
    
    print("="*70)

if __name__ == "__main__":
    import sys
    production = '--production' in sys.argv
    update_images(production=production)
