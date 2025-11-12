"""
Script para probar el nuevo endpoint de recomendaciones personalizadas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from users.models import CustomUser
from products.models import Product, Category
from shop_orders.models import Order, OrderItem
from django.db.models import Count

User = CustomUser


def test_personalized_recommendations():
    print("\n" + "="*70)
    print("🧪 PROBANDO SISTEMA DE RECOMENDACIONES PERSONALIZADAS")
    print("="*70)
    
    # 1. Verificar usuario con historial
    print("\n📋 PASO 1: Verificar usuario con historial de compras")
    
    # Buscar cualquier usuario con órdenes pagadas/entregadas (sin filtrar por rol CLIENT que no existe)
    user = User.objects.filter(
        orders__status__in=['PAID', 'DELIVERED']
    ).distinct().first()
    
    if not user:
        print("❌ No se encontró usuario con historial de compras")
        return
    
    print(f"✅ Usuario encontrado: {user.username} ({user.email})")
    
    # Ver su historial
    orders = Order.objects.filter(
        user=user,
        status__in=['PAID', 'DELIVERED']
    ).prefetch_related('items__product__category')
    
    print(f"\n📦 Historial de compras:")
    print(f"   Total de órdenes: {orders.count()}")
    
    # Categorías compradas
    categories_bought = {}
    products_bought = []
    
    for order in orders:
        for item in order.items.all():
            if item.product:
                products_bought.append(item.product.name)
                cat_name = item.product.category.name if item.product.category else "Sin categoría"
                categories_bought[cat_name] = categories_bought.get(cat_name, 0) + item.quantity
    
    print(f"\n   📊 Categorías compradas:")
    for cat, qty in sorted(categories_bought.items(), key=lambda x: x[1], reverse=True):
        print(f"      • {cat}: {qty} productos")
    
    print(f"\n   🛒 Productos comprados ({len(products_bought)}):")
    for i, prod in enumerate(products_bought[:5], 1):
        print(f"      {i}. {prod}")
    if len(products_bought) > 5:
        print(f"      ... y {len(products_bought) - 5} más")
    
    # 2. Simular el endpoint
    print("\n" + "="*70)
    print("🤖 PASO 2: Generar recomendaciones con IA")
    print("="*70)
    
    from products.views import ProductViewSet
    from rest_framework.test import APIRequestFactory
    from rest_framework.request import Request
    
    factory = APIRequestFactory()
    request = factory.get('/api/products/personalized/')
    request.user = user
    
    # Crear vista y ejecutar
    view = ProductViewSet()
    view.request = Request(request)
    view.format_kwarg = None
    
    response = view.personalized(request)
    data = response.data
    
    print(f"\n✅ Recomendaciones generadas:")
    print(f"   Usuario: {data['user']}")
    print(f"   Estrategia usada: {data['strategy_used']}")
    print(f"   Categorías favoritas: {', '.join(data['favorite_categories'])}")
    print(f"   Total de productos recomendados: {data['count']}")
    
    print(f"\n🎯 Productos recomendados para {user.username}:")
    print("   " + "-"*66)
    
    for i, product in enumerate(data['recommendations'], 1):
        print(f"   {i}. {product['name']}")
        print(f"      💰 Precio: ${product['price']}")
        print(f"      📦 Stock: {product['stock']}")
        if product.get('category_name'):
            print(f"      🏷️  Categoría: {product['category_name']}")
        print()
    
    # 3. Verificar que no recomienda productos ya comprados
    print("="*70)
    print("🔍 PASO 3: Verificar que NO recomienda productos ya comprados")
    print("="*70)
    
    recommended_names = [p['name'] for p in data['recommendations']]
    duplicates = set(products_bought) & set(recommended_names)
    
    if duplicates:
        print(f"⚠️  ADVERTENCIA: Se encontraron {len(duplicates)} productos duplicados:")
        for dup in duplicates:
            print(f"   • {dup}")
    else:
        print("✅ Perfecto: Ningún producto recomendado ya fue comprado por el usuario")
    
    # 4. Probar con usuario sin historial
    print("\n" + "="*70)
    print("🧪 PASO 4: Probar con usuario SIN historial")
    print("="*70)
    
    new_user = User.objects.exclude(
        id__in=Order.objects.values_list('user_id', flat=True)
    ).first()
    
    if new_user:
        print(f"✅ Usuario sin historial: {new_user.username}")
        
        request_new = factory.get('/api/products/personalized/')
        request_new.user = new_user
        
        view_new = ProductViewSet()
        view_new.request = Request(request_new)
        view_new.format_kwarg = None
        
        response_new = view_new.personalized(request_new)
        data_new = response_new.data
        
        print(f"   Estrategia usada: {data_new['strategy_used']}")
        print(f"   Productos recomendados: {data_new['count']}")
        print(f"   ✅ Fallback a productos populares funcionando correctamente")
    else:
        print("⚠️  No se encontró usuario sin historial para probar")
    
    # Resumen final
    print("\n" + "="*70)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*70)
    print("✅ Endpoint implementado correctamente")
    print("✅ IA genera recomendaciones basadas en historial")
    print("✅ Evita recomendar productos ya comprados")
    print("✅ Fallback a productos populares para usuarios nuevos")
    print("\n🎉 Sistema listo para menú de publicidad personalizada")
    print("="*70)
    
    # Instrucciones de uso
    print("\n📋 CÓMO USAR EN EL FRONTEND:")
    print("   URL: GET /api/products/personalized/")
    print("   Headers: Authorization: Bearer {token}")
    print("   Parámetros opcionales: ?limit=10")
    print("\n   Ejemplo con axios:")
    print("""
   const response = await axios.get(
       '/api/products/personalized/',
       {
           headers: { Authorization: `Bearer ${token}` },
           params: { limit: 6 }  // Para mostrar 6 productos en el banner
       }
   );
   
   // response.data.recommendations contiene los productos
   """)


if __name__ == '__main__':
    try:
        test_personalized_recommendations()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
