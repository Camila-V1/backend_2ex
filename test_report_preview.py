#!/usr/bin/env python
"""
Script de prueba para los endpoints de previsualización de reportes
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

def test_sales_preview(token):
    """Probar preview de reporte de ventas"""
    print_header("1. PREVISUALIZACIÓN DE REPORTE DE VENTAS")
    
    # Calcular fechas del mes actual
    today = datetime.now()
    start_date = today.replace(day=1).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    print_info(f"Consultando ventas del {start_date} al {end_date}")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f"{BASE_URL}/api/reports/sales/preview/?start_date={start_date}&end_date={end_date}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success("Preview de ventas obtenido correctamente")
        print_info(f"Total de órdenes: {data.get('total_orders', 0)}")
        print_info(f"Total de ingresos: ${data.get('total_revenue', 0):.2f}")
        
        if data.get('orders'):
            print_info(f"\nPrimeras 3 órdenes:")
            for order in data['orders'][:3]:
                print(f"  - Orden #{order['order_id']}: {order['customer']} - ${order['total']}")
                print(f"    Items: {order['items_count']}, Fecha: {order['date']}")
        else:
            print_info("No hay órdenes en el período seleccionado")
        
        return True
    else:
        print_error(f"Error: {response.status_code}")
        print(response.text)
        return False

def test_products_preview(token):
    """Probar preview de reporte de productos"""
    print_header("2. PREVISUALIZACIÓN DE REPORTE DE PRODUCTOS")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f"{BASE_URL}/api/reports/products/preview/",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success("Preview de productos obtenido correctamente")
        print_info(f"Total de productos: {data.get('total_products', 0)}")
        print_info(f"Total de stock: {data.get('total_stock', 0)} unidades")
        print_info(f"Valor total del inventario: ${data.get('total_value', 0):.2f}")
        
        if data.get('products'):
            print_info(f"\nPrimeros 5 productos:")
            for product in data['products'][:5]:
                print(f"  - {product['name']}")
                print(f"    Categoría: {product['category']}, Precio: ${product['price']}, Stock: {product['stock']}")
        
        return True
    else:
        print_error(f"Error: {response.status_code}")
        print(response.text)
        return False

def test_dynamic_preview(token):
    """Probar preview de reporte dinámico"""
    print_header("3. PREVISUALIZACIÓN DE REPORTE DINÁMICO")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Prueba 1: Ventas del mes actual
    today = datetime.now()
    month_name = today.strftime('%B').lower()  # octubre, noviembre, etc.
    
    prompts = [
        f"ventas del mes de {month_name}",
        f"ventas agrupado por producto del mes de {month_name}",
        "reporte de productos"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print_info(f"\nPrueba {i}: '{prompt}'")
        
        response = requests.post(
            f"{BASE_URL}/api/reports/dynamic-parser/preview/",
            headers=headers,
            json={'prompt': prompt}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Preview generado correctamente")
            print_info(f"Título: {data.get('title', 'N/A')}")
            print_info(f"Columnas: {', '.join(data.get('headers', []))}")
            print_info(f"Total de registros: {data.get('total_records', 0)}")
            
            if data.get('data'):
                print_info(f"Primeros 2 registros:")
                for row in data['data'][:2]:
                    print(f"  - {row}")
        else:
            print_error(f"Error: {response.status_code}")
            print(response.text)
            return False
    
    return True

def test_download_after_preview(token):
    """Probar que los endpoints de descarga siguen funcionando"""
    print_header("4. DESCARGA DE REPORTES (ENDPOINTS ORIGINALES)")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Calcular fechas del mes actual
    today = datetime.now()
    start_date = today.replace(day=1).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    # Prueba 1: Descargar PDF de ventas
    print_info("Descargando reporte de ventas en PDF...")
    response = requests.get(
        f"{BASE_URL}/api/reports/sales/?start_date={start_date}&end_date={end_date}&format=pdf",
        headers=headers
    )
    
    if response.status_code == 200 and response.headers.get('Content-Type') == 'application/pdf':
        filename = f"test_ventas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print_success(f"PDF de ventas descargado: {filename} ({len(response.content)} bytes)")
    else:
        print_error(f"Error al descargar PDF: {response.status_code}")
        return False
    
    # Prueba 2: Descargar Excel de productos
    print_info("\nDescargando reporte de productos en Excel...")
    response = requests.get(
        f"{BASE_URL}/api/reports/products/?format=excel",
        headers=headers
    )
    
    if response.status_code == 200:
        filename = f"test_productos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print_success(f"Excel de productos descargado: {filename} ({len(response.content)} bytes)")
    else:
        print_error(f"Error al descargar Excel: {response.status_code}")
        return False
    
    return True

def main():
    print_header("SISTEMA DE PRUEBAS - PREVISUALIZACIÓN DE REPORTES")
    print("🔍 Asegúrate de que el servidor esté corriendo en http://localhost:8000")
    print("   Ejecuta: python manage.py runserver")
    input("\nPresiona Enter cuando el servidor esté listo...")
    
    # Obtener token
    token = get_admin_token()
    if not token:
        print_error("No se pudo obtener token de administrador")
        return
    
    print_success("Token obtenido correctamente\n")
    
    # Ejecutar pruebas
    results = []
    results.append(("Preview de ventas", test_sales_preview(token)))
    results.append(("Preview de productos", test_products_preview(token)))
    results.append(("Preview dinámico", test_dynamic_preview(token)))
    results.append(("Descarga original", test_download_after_preview(token)))
    
    # Resumen
    print_header("RESUMEN DE PRUEBAS")
    total = len(results)
    passed = sum(1 for _, result in results if result)
    
    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status}: {name}")
    
    print(f"\n📊 Resultado final: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron! El sistema de previsualización está funcionando correctamente.")
        print("\n📝 Archivos de prueba generados:")
        print("   - test_ventas_*.pdf")
        print("   - test_productos_*.xlsx")
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
