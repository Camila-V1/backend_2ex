#!/usr/bin/env python3
"""
Diagnóstico de permisos 403 en dashboard
"""
import requests

BASE_URL = 'https://backend-2ex-ecommerce.onrender.com/api'

# Login
print("🔐 Login como admin...")
response = requests.post(f'{BASE_URL}/token/', json={
    'username': 'admin',
    'password': 'admin123'
})

if response.status_code != 200:
    print(f"❌ Error login: {response.status_code}")
    exit(1)

token = response.json()['access']
print(f"✅ Token obtenido\n")

headers = {'Authorization': f'Bearer {token}'}

# Probar endpoints críticos
endpoints = [
    '/orders/admin/dashboard/',
    '/orders/admin/',
    '/users/',
    '/products/',
    '/users/wallets/my_wallet/',
    '/audit/',
    '/reports/sales/preview/?start_date=2024-01-01&end_date=2024-12-31',
    '/predictions/sales/'
]

print("🔍 Probando permisos en endpoints:\n")
for endpoint in endpoints:
    r = requests.get(f'{BASE_URL}{endpoint}', headers=headers)
    status = '✅' if r.status_code == 200 else '❌'
    print(f"{status} {endpoint}: {r.status_code}")
    
    if r.status_code == 403:
        try:
            print(f"   Error: {r.json()}")
        except:
            print(f"   Error: {r.text[:100]}")

print("\n📊 Verificando perfil del usuario:")
r = requests.get(f'{BASE_URL}/users/profile/', headers=headers)
if r.ok:
    profile = r.json()
    print(f"   Usuario: {profile.get('username')}")
    print(f"   Role: {profile.get('role')}")
    print(f"   Is staff: {profile.get('is_staff')}")
    print(f"   Is superuser: {profile.get('is_superuser')}")
