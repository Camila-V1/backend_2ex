import requests

login_url = "https://backend-2ex-ecommerce.onrender.com/api/users/login/"

# Lista de posibles credenciales (probar con username Y email)
test_credentials = [
    # Con username
    {"username": "admin", "password": "admin123"},
    {"username": "superadmin", "password": "admin123"},
    {"username": "admin", "password": "admin"},
    # Con email
    {"email": "admin@example.com", "password": "admin123"},
    {"email": "admin@ecommerce.com", "password": "admin123"},
    {"email": "superadmin@example.com", "password": "admin123"},
]

print("🔍 Probando credenciales...\n")

for creds in test_credentials:
    identifier = creds.get('username') or creds.get('email')
    print(f"Probando: {identifier} con {creds}")
    try:
        response = requests.post(login_url, json=creds, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✅ FUNCIONA!")
            data = response.json()
            print(f"  Token: {data.get('access', 'N/A')[:50]}...")
            print(f"  User: {data.get('user', {})}")
            break
        else:
            print(f"  ❌ Error: {response.text[:150]}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")
    print()
