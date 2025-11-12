"""
Script para listar todos los productos de la base de datos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from products.models import Product


def list_products():
    print("\n" + "="*90)
    print("📦 PRODUCTOS EN BASE DE DATOS DE PRODUCCIÓN")
    print("="*90)
    
    products = Product.objects.select_related('category').order_by('category__name', 'name')
    total = products.count()
    
    print(f"\nTotal de productos: {total}\n")
    
    current_category = None
    count_by_category = {}
    
    for product in products:
        category_name = product.category.name if product.category else "Sin categoría"
        
        # Contar por categoría
        count_by_category[category_name] = count_by_category.get(category_name, 0) + 1
        
        # Mostrar encabezado de categoría
        if category_name != current_category:
            if current_category is not None:
                print()
            print(f"\n🏷️  {category_name.upper()}")
            print("-" * 90)
            current_category = category_name
        
        # Estado del producto
        status = "✅" if product.is_active else "❌"
        
        # Formato de precio
        price_str = f"${product.price}"
        
        # Imprimir producto
        print(f"{status} ID:{product.id:3d} | {product.name[:45]:45s} | {price_str:>12s} | Stock:{product.stock:4d}")
    
    # Resumen por categoría
    print("\n" + "="*90)
    print("📊 RESUMEN POR CATEGORÍA")
    print("="*90)
    
    for cat, count in sorted(count_by_category.items()):
        print(f"   {cat:30s}: {count:3d} productos")
    
    print(f"\n   {'TOTAL':30s}: {total:3d} productos")
    print("="*90)


if __name__ == '__main__':
    try:
        list_products()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
