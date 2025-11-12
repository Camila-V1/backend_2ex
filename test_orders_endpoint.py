import requests
import json

# Login
print('🔐 Intentando login (puede tardar 1-2 minutos por cold start)...')
login_response = requests.post(
    'https://backend-2ex-ecommerce.onrender.com/api/token/',
    json={'username': 'admin', 'password': 'admin123'},
    timeout=120
)

if login_response.status_code != 200:
    print(f'❌ Login falló: {login_response.status_code}')
    print(login_response.text)
    exit(1)

token = login_response.json()['access']
print('✅ Login exitoso')

# Get orders
headers = {'Authorization': f'Bearer {token}'}
orders_response = requests.get(
    'https://backend-2ex-ecommerce.onrender.com/api/orders/admin/',
    headers=headers
)

data = orders_response.json()

print(f'✅ Status: {orders_response.status_code}')
print(f'📊 Total órdenes: {len(data)}')
print(f'\n🔢 Primeras 5 órdenes:')
for order in data[:5]:
    print(f"  Orden #{order['id']} - {order['user']} - {order['status']} - ${order['total_price']} - {len(order['items'])} items")

print(f'\n🔢 Últimas 5 órdenes:')
for order in data[-5:]:
    print(f"  Orden #{order['id']} - {order['user']} - {order['status']} - ${order['total_price']} - {len(order['items'])} items")
