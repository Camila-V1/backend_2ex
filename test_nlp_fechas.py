"""
Script para probar reconocimiento de fechas en NLP de reportes
"""
import requests

BACKEND_URL = "https://backend-2ex-ecommerce.onrender.com/api"

def get_token():
    response = requests.post(
        f"{BACKEND_URL}/token/",
        json={"username": "admin", "password": "admin123"}
    )
    return response.json()["access"]

def test_nlp_dates():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("=" * 80)
    print("🧪 TESTING NLP RECONOCIMIENTO DE FECHAS")
    print("=" * 80)
    
    # Test cases con diferentes formatos
    test_cases = [
        {
            "prompt": "Reporte de ventas del 1 al 5 de septiembre en PDF",
            "descripcion": "Números simples (1 al 5)"
        },
        {
            "prompt": "Dame ventas del uno al cinco de septiembre",
            "descripcion": "Números en palabras (uno al cinco)"
        },
        {
            "prompt": "Reporte del primero al quince de octubre",
            "descripcion": "Números en palabras (primero al quince)"
        },
        {
            "prompt": "Ventas del 10 al 20 de noviembre",
            "descripcion": "Números dobles dígitos (10 al 20)"
        },
        {
            "prompt": "Reporte del diez al veinte de noviembre en Excel",
            "descripcion": "Números en palabras dobles dígitos"
        },
        {
            "prompt": "Ventas de septiembre",
            "descripcion": "Mes completo (septiembre completo)"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}️⃣  Test: {test['descripcion']}")
        print(f"   Prompt: \"{test['prompt']}\"")
        
        try:
            # Usar el endpoint de preview para ver qué fechas interpreta
            response = requests.post(
                f"{BACKEND_URL}/reports/dynamic-parser/preview/",
                headers=headers,
                json={"prompt": test['prompt']}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {response.status_code}")
                print(f"   📅 Fecha inicio: {data.get('start_date', 'N/A')}")
                print(f"   📅 Fecha fin: {data.get('end_date', 'N/A')}")
                print(f"   📊 Registros: {data.get('total_records', 0)}")
            else:
                print(f"   ❌ Error {response.status_code}: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
    
    print("\n" + "=" * 80)
    print("✅ PRUEBAS COMPLETADAS")
    print("=" * 80)
    print("\n📝 COMANDOS QUE DEBERÍAN FUNCIONAR:")
    print("   • 'del 1 al 5 de septiembre'")
    print("   • 'del uno al cinco de septiembre'")
    print("   • 'del primero al quince de octubre'")
    print("   • 'del diez al veinte de noviembre'")

if __name__ == "__main__":
    test_nlp_dates()
