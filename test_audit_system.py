#!/usr/bin/env python
"""
Script de prueba para el sistema de auditoría
Ejecutar después de iniciar el servidor con: python manage.py runserver
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_info(msg):
    print(f"ℹ️  {msg}")

def get_admin_token():
    """Obtener token de administrador"""
    response = requests.post(f"{BASE_URL}/api/token/", json={
        'username': 'admin',
        'password': 'admin123'
    })
    if response.status_code == 200:
        return response.json()['access']
    else:
        print_error(f"No se pudo obtener token: {response.status_code}")
        print(response.text)
        return None

def test_audit_list(token):
    """Probar listado de logs de auditoría"""
    print_header("1. LISTADO DE LOGS DE AUDITORÍA")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{BASE_URL}/api/audit/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Endpoint funcionando correctamente")
        print_info(f"Total de logs: {data.get('count', 0)}")
        
        if data.get('results'):
            print_info("\nÚltimos 3 registros:")
            for log in data['results'][:3]:
                print(f"  - {log['timestamp']}: {log['action_display']} por {log['username'] or 'Anónimo'} desde {log['ip_address']}")
        return True
    else:
        print_error(f"Error: {response.status_code}")
        print(response.text)
        return False

def test_audit_stats(token):
    """Probar endpoint de estadísticas"""
    print_header("2. ESTADÍSTICAS DE AUDITORÍA")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{BASE_URL}/api/audit/stats/", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        print_success("Estadísticas obtenidas correctamente")
        
        print_info(f"Total de logs: {stats.get('total_logs', 0)}")
        print_info(f"Últimas 24 horas: {stats.get('last_24_hours', 0)}")
        print_info(f"Última semana: {stats.get('last_week', 0)}")
        print_info(f"Exitosos: {stats.get('success_count', 0)}")
        print_info(f"Con errores: {stats.get('error_count', 0)}")
        
        print_info("\nTop 5 acciones:")
        for item in stats.get('by_action', [])[:5]:
            print(f"  - {item['action']}: {item['count']} veces")
        
        print_info("\nTop 5 usuarios:")
        for item in stats.get('by_user', [])[:5]:
            print(f"  - {item['username']}: {item['count']} acciones")
        
        print_info("\nTop 5 IPs:")
        for item in stats.get('by_ip', [])[:5]:
            print(f"  - {item['ip_address']}: {item['count']} peticiones")
        
        return True
    else:
        print_error(f"Error: {response.status_code}")
        print(response.text)
        return False

def test_audit_filters(token):
    """Probar filtros de auditoría"""
    print_header("3. FILTROS DE AUDITORÍA")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Filtro por acción
    print_info("Filtrando por acción LOGIN...")
    response = requests.get(f"{BASE_URL}/api/audit/?action=LOGIN", headers=headers)
    if response.status_code == 200:
        count = response.json().get('count', 0)
        print_success(f"Encontrados {count} logs de LOGIN")
    
    # Filtro por severidad
    print_info("\nFiltrando por severidad ERROR...")
    response = requests.get(f"{BASE_URL}/api/audit/?severity=ERROR", headers=headers)
    if response.status_code == 200:
        count = response.json().get('count', 0)
        print_success(f"Encontrados {count} logs con ERROR")
    
    # Filtro por usuario
    print_info("\nFiltrando por usuario 'admin'...")
    response = requests.get(f"{BASE_URL}/api/audit/?username=admin", headers=headers)
    if response.status_code == 200:
        count = response.json().get('count', 0)
        print_success(f"Encontrados {count} logs del usuario admin")
    
    # Filtro por fecha
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    print_info(f"\nFiltrando desde {yesterday}...")
    response = requests.get(f"{BASE_URL}/api/audit/?start_date={yesterday}", headers=headers)
    if response.status_code == 200:
        count = response.json().get('count', 0)
        print_success(f"Encontrados {count} logs desde ayer")
    
    # Búsqueda de texto
    print_info("\nBúsqueda de texto 'login'...")
    response = requests.get(f"{BASE_URL}/api/audit/?search=login", headers=headers)
    if response.status_code == 200:
        count = response.json().get('count', 0)
        print_success(f"Encontrados {count} logs con 'login' en la descripción")
    
    return True

def test_audit_export_pdf(token):
    """Probar exportación a PDF"""
    print_header("4. EXPORTACIÓN A PDF")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{BASE_URL}/api/audit/export_pdf/", headers=headers)
    
    if response.status_code == 200:
        filename = f"auditoria_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print_success(f"PDF generado correctamente: {filename}")
        print_info(f"Tamaño: {len(response.content)} bytes")
        return True
    else:
        print_error(f"Error: {response.status_code}")
        print(response.text)
        return False

def test_audit_export_excel(token):
    """Probar exportación a Excel"""
    print_header("5. EXPORTACIÓN A EXCEL")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{BASE_URL}/api/audit/export_excel/", headers=headers)
    
    if response.status_code == 200:
        filename = f"auditoria_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print_success(f"Excel generado correctamente: {filename}")
        print_info(f"Tamaño: {len(response.content)} bytes")
        return True
    else:
        print_error(f"Error: {response.status_code}")
        print(response.text)
        return False

def generate_test_activity(token):
    """Generar actividad para crear más logs de auditoría"""
    print_header("0. GENERANDO ACTIVIDAD DE PRUEBA")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Ver productos (PRODUCT_VIEW)
    print_info("Consultando productos...")
    requests.get(f"{BASE_URL}/api/products/", headers=headers)
    
    # Ver órdenes (ORDER_VIEW)
    print_info("Consultando órdenes...")
    requests.get(f"{BASE_URL}/api/orders/", headers=headers)
    
    # Consulta NLP (NLP_QUERY)
    print_info("Haciendo consulta NLP...")
    requests.post(f"{BASE_URL}/api/orders/natural-language/", 
                 headers=headers,
                 json={'query': 'laptops'})
    
    # Intentar acceso sin autorización (PERMISSION_DENIED)
    print_info("Intentando acceso sin autorización...")
    requests.get(f"{BASE_URL}/api/audit/")
    
    print_success("Actividad de prueba generada")

def main():
    print_header("SISTEMA DE PRUEBAS - AUDITORÍA")
    print("🔍 Asegúrate de que el servidor esté corriendo en http://localhost:8000")
    print("   Ejecuta: python manage.py runserver")
    input("\nPresiona Enter cuando el servidor esté listo...")
    
    # Obtener token
    token = get_admin_token()
    if not token:
        print_error("No se pudo obtener token de administrador")
        return
    
    print_success("Token obtenido correctamente\n")
    
    # Generar actividad de prueba
    generate_test_activity(token)
    
    # Ejecutar pruebas
    results = []
    results.append(("Listado de logs", test_audit_list(token)))
    results.append(("Estadísticas", test_audit_stats(token)))
    results.append(("Filtros", test_audit_filters(token)))
    results.append(("Exportación PDF", test_audit_export_pdf(token)))
    results.append(("Exportación Excel", test_audit_export_excel(token)))
    
    # Resumen
    print_header("RESUMEN DE PRUEBAS")
    total = len(results)
    passed = sum(1 for _, result in results if result)
    
    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status}: {name}")
    
    print(f"\n📊 Resultado final: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron! El sistema de auditoría está funcionando correctamente.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
