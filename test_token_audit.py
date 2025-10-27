"""
Script para probar el sistema de autenticación y acceso a auditoría
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_login_and_audit():
    print("=" * 60)
    print("🔐 TEST DE AUTENTICACIÓN Y AUDITORÍA")
    print("=" * 60)
    
    # 1. Login
    print("\n1️⃣ Intentando login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/token/", json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens.get('access')
            refresh_token = tokens.get('refresh')
            
            print(f"   ✅ Login exitoso!")
            print(f"   Access token: {access_token[:50]}...")
            print(f"   Refresh token: {refresh_token[:50]}...")
            
            # 2. Probar endpoint de auditoría
            print("\n2️⃣ Probando endpoint /api/audit/...")
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            audit_response = requests.get(f"{BASE_URL}/api/audit/?page=1", headers=headers)
            print(f"   Status: {audit_response.status_code}")
            
            if audit_response.status_code == 200:
                data = audit_response.json()
                print(f"   ✅ Auditoría accesible!")
                print(f"   Total logs: {data.get('count', 0)}")
                print(f"   Logs en esta página: {len(data.get('results', []))}")
                
                if data.get('results'):
                    print(f"\n   📋 Primer log:")
                    first_log = data['results'][0]
                    print(f"      ID: {first_log.get('id')}")
                    print(f"      Acción: {first_log.get('action')}")
                    print(f"      Usuario: {first_log.get('username')}")
                    print(f"      Timestamp: {first_log.get('timestamp')}")
            else:
                print(f"   ❌ Error al acceder a auditoría")
                print(f"   Respuesta: {audit_response.text}")
            
            # 3. Probar stats
            print("\n3️⃣ Probando endpoint /api/audit/stats/...")
            stats_response = requests.get(f"{BASE_URL}/api/audit/stats/", headers=headers)
            print(f"   Status: {stats_response.status_code}")
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"   ✅ Stats accesibles!")
                print(f"   Total logs: {stats.get('total_logs')}")
                print(f"   Últimas 24h: {stats.get('last_24_hours')}")
                print(f"   Última semana: {stats.get('last_week')}")
            else:
                print(f"   ❌ Error al acceder a stats")
                print(f"   Respuesta: {stats_response.text}")
            
            # 4. Verificar que el token se puede usar en localStorage
            print("\n4️⃣ Información para el Frontend:")
            print(f"   📝 Guardar en localStorage:")
            print(f"      localStorage.setItem('access_token', '{access_token}');")
            print(f"\n   📝 Header a usar:")
            print(f"      'Authorization': 'Bearer {access_token}'")
            
        else:
            print(f"   ❌ Error en login: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ ERROR: No se puede conectar al servidor")
        print("   ¿Está el servidor corriendo? (python manage.py runserver)")
    except Exception as e:
        print(f"   ❌ Error inesperado: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ Test completado")
    print("=" * 60)

if __name__ == "__main__":
    test_login_and_audit()
