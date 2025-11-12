import requests

url = "https://backend-2ex-ecommerce.onrender.com/api/products/"

response = requests.get(url, timeout=30)
products = response.json()

print(f"Total productos: {len(products)}\n")
print("Productos SIN imagen:")
print("=" * 60)

for product in products:
    if not product.get('image_url'):
        print(f"ID: {product['id']:3} | {product['name']}")
        print(f"   Precio: ${product['price']}")
        print(f"   Stock: {product['stock']}")
        print()
