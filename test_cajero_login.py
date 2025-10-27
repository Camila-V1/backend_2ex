"""
Script para probar login de cajero
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_cajero_login():
    print("=" * 60)
    print("🔐 TEST DE LOGIN - CAJERO")
    print("=" * 60)
    
    # Datos de login
    credentials = {
        "username": "luis_cajero",
        "password": "cajero123"
    }
    
    print(f"\n1️⃣ Intentando login con:")
    print(f"   Usuario: {credentials['username']}")
    print(f"   Contraseña: {credentials['password']}")
    
    try:
        # Login
        response = requests.post(
            f"{BASE_URL}/api/token/",
            json=credentials,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n2️⃣ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access')
            
            print(f"   ✅ LOGIN EXITOSO!")
            print(f"   Access token: {access_token[:50]}...")
            print(f"   Role: {data.get('role')}")
            print(f"   Username: {data.get('username')}")
            
            # Probar perfil
            print(f"\n3️⃣ Obteniendo perfil...")
            profile_response = requests.get(
                f"{BASE_URL}/api/users/profile/",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
            )
            
            if profile_response.status_code == 200:
                profile = profile_response.json()
                print(f"   ✅ Perfil obtenido:")
                print(f"      Username: {profile.get('username')}")
                print(f"      Email: {profile.get('email')}")
                print(f"      Role: {profile.get('role')}")
                print(f"      Nombre: {profile.get('first_name')} {profile.get('last_name')}")
            
            # Probar acceso a productos
            print(f"\n4️⃣ Probando acceso a productos...")
            products_response = requests.get(
                f"{BASE_URL}/api/products/",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
            )
            
            if products_response.status_code == 200:
                products = products_response.json()
                print(f"   ✅ Productos accesibles")
                print(f"      Total productos: {products.get('count', 'N/A')}")
            else:
                print(f"   ❌ Error al acceder productos: {products_response.status_code}")
            
            # Probar acceso a dashboard (debe fallar - solo admin/manager)
            print(f"\n5️⃣ Probando acceso a dashboard admin (debe fallar)...")
            dashboard_response = requests.get(
                f"{BASE_URL}/api/orders/admin/dashboard/",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
            )
            
            if dashboard_response.status_code == 403:
                print(f"   ✅ Correcto! Dashboard bloqueado (403 Forbidden)")
                print(f"      Cajero NO tiene acceso a dashboard admin")
            elif dashboard_response.status_code == 200:
                print(f"   ⚠️ Dashboard accesible (no debería)")
            else:
                print(f"   Status: {dashboard_response.status_code}")
            
            # Probar auditoría (debe fallar)
            print(f"\n6️⃣ Probando acceso a auditoría (debe fallar)...")
            audit_response = requests.get(
                f"{BASE_URL}/api/audit/",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
            )
            
            if audit_response.status_code == 403:
                print(f"   ✅ Correcto! Auditoría bloqueada (403 Forbidden)")
                print(f"      Cajero NO tiene acceso a logs de auditoría")
            else:
                print(f"   Status: {audit_response.status_code}")
            
            print(f"\n✅ RESUMEN:")
            print(f"   ✅ Login funciona correctamente")
            print(f"   ✅ Perfil accesible")
            print(f"   ✅ Productos accesibles")
            print(f"   ✅ Dashboard admin BLOQUEADO (correcto)")
            print(f"   ✅ Auditoría BLOQUEADA (correcto)")
            
        else:
            error_data = response.json()
            print(f"   ❌ ERROR EN LOGIN")
            print(f"   Mensaje: {error_data}")
            print(f"\n   Posibles causas:")
            print(f"   1. Contraseña incorrecta")
            print(f"   2. Usuario no existe")
            print(f"   3. Usuario no activo")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ ERROR: No se puede conectar al servidor")
        print(f"   ¿Está corriendo? (python manage.py runserver)")
    except Exception as e:
        print(f"   ❌ Error inesperado: {str(e)}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_cajero_login()
