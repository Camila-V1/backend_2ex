from products.models import Category, Product
from shop_orders.models import Order

print("=" * 60)
print("CATEGORIAS DISPONIBLES")
print("=" * 60)
categories = Category.objects.all()
for cat in categories:
    print(f"ID: {cat.id:2d} | Nombre: {cat.name}")

print("\n" + "=" * 60)
print("PRODUCTOS DISPONIBLES (primeros 5)")
print("=" * 60)
products = Product.objects.all()[:5]
for prod in products:
    print(f"ID: {prod.id:3d} | Nombre: {prod.name:40s} | Categoría ID: {prod.category_id}")

print("\n" + "=" * 60)
print("ORDENES DISPONIBLES (primeras 5)")
print("=" * 60)
orders = Order.objects.all()[:5]
for order in orders:
    print(f"ID: {order.id:3d} | Usuario: {order.user.username:20s} | Status: {order.status} | Total: ${order.total_price}")
