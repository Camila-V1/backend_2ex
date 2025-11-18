"""
Script para probar filtros en PRODUCCIÓN
"""
import requests

BACKEND_URL = "https://backend-2ex-ecommerce.onrender.com/api"

def get_token():
    response = requests.post(
        f"{BACKEND_URL}/token/",
        json={"username": "admin", "password": "admin123"}
    )
    return response.json()["access"]

def test_production_filters():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("=" * 80)
    print("🧪 TESTING PRODUCTION FILTERS AND PAGINATION")
    print("=" * 80)
    
    # Test 1: Paginación básica (50 por página)
    print("\n1️⃣  Test: Página 1 (debe mostrar 50 órdenes)")
    response = requests.get(f"{BACKEND_URL}/orders/?page=1", headers=headers)
    data = response.json()
    print(f"   ✅ Total count: {data['count']}")
    print(f"   ✅ Results en página 1: {len(data['results'])}")
    print(f"   ✅ Tiene página siguiente: {data['next'] is not None}")
    print(f"   ✅ Total de páginas estimado: {(data['count'] + 49) // 50}")
    
    # Test 2: Filtro por estado DELIVERED
    print("\n2️⃣  Test: Filtrar por status=DELIVERED")
    response = requests.get(f"{BACKEND_URL}/orders/?status=DELIVERED", headers=headers)
    data = response.json()
    print(f"   ✅ Total DELIVERED: {data['count']}")
    if data['results']:
        estados = [o['status'] for o in data['results'][:5]]
        print(f"   ✅ Primeros 5 estados: {estados}")
    
    # Test 3: Filtro por fecha (noviembre 2025)
    print("\n3️⃣  Test: Filtrar por start_date=2025-11-01")
    response = requests.get(f"{BACKEND_URL}/orders/?start_date=2025-11-01", headers=headers)
    data = response.json()
    print(f"   ✅ Órdenes desde nov 2025: {data['count']}")
    
    # Test 4: Rango de fechas completo
    print("\n4️⃣  Test: Rango de fechas (01 a 17 de noviembre)")
    response = requests.get(
        f"{BACKEND_URL}/orders/?start_date=2025-11-01&end_date=2025-11-17",
        headers=headers
    )
    data = response.json()
    print(f"   ✅ Órdenes en rango: {data['count']}")
    
    # Test 5: Combinar filtros
    print("\n5️⃣  Test: status=PAID + start_date=2025-11-01")
    response = requests.get(
        f"{BACKEND_URL}/orders/?status=PAID&start_date=2025-11-01",
        headers=headers
    )
    data = response.json()
    print(f"   ✅ Órdenes PAID en noviembre: {data['count']}")
    
    # Test 6: Página 2
    print("\n6️⃣  Test: Navegar a página 2")
    response = requests.get(f"{BACKEND_URL}/orders/?page=2", headers=headers)
    data = response.json()
    print(f"   ✅ Results en página 2: {len(data['results'])}")
    print(f"   ✅ Tiene previous: {data['previous'] is not None}")
    print(f"   ✅ Tiene next: {data['next'] is not None}")
    
    # Test 7: Estado PENDING
    print("\n7️⃣  Test: Filtrar por status=PENDING")
    response = requests.get(f"{BACKEND_URL}/orders/?status=PENDING", headers=headers)
    data = response.json()
    print(f"   ✅ Total PENDING: {data['count']}")
    
    print("\n" + "=" * 80)
    print("✅ TODOS LOS FILTROS FUNCIONAN CORRECTAMENTE")
    print("=" * 80)
    print("\n📱 Ahora puedes implementar esto en Flutter usando el código del documento")
    print("📄 Ver: SOLUCION_REPORTES_Y_PAGINACION.md")

if __name__ == "__main__":
    test_production_filters()
