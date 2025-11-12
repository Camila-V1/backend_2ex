"""
Script para poblar imágenes en PRODUCCIÓN vía API
REQUIERE: Token de administrador
"""
import requests
import json

# Configuración
PRODUCTION_URL = "https://backend-2ex-ecommerce.onrender.com/api/products/populate-images/"

def main():
    print("=" * 70)
    print("🖼️  POBLADOR DE IMÁGENES EN PRODUCCIÓN")
    print("=" * 70)
    
    # Solicitar token
    print("\n📝 Ingresa tu token de administrador:")
    print("   (Obtenerlo de CREDENCIALES_SISTEMA.md o login como admin)")
    token = input("Token: ").strip()
    
    if not token:
        print("❌ Token requerido. Abortando.")
        return
    
    # Preparar headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🌐 Conectando a: {PRODUCTION_URL}")
    print("⏳ Enviando solicitud POST...")
    
    try:
        response = requests.post(PRODUCTION_URL, headers=headers, timeout=60)
        
        print(f"\n📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n" + "=" * 70)
            print("✅ ÉXITO - IMÁGENES POBLADAS")
            print("=" * 70)
            
            # Estadísticas
            stats = data.get('statistics', {})
            print(f"\n📊 ESTADÍSTICAS:")
            print(f"   Total de productos:      {stats.get('total_products')}")
            print(f"   ✅ Con imagen:            {stats.get('products_with_images')}")
            print(f"   ❌ Sin imagen:            {stats.get('products_without_images')}")
            print(f"   📈 Porcentaje:            {stats.get('percentage')}%")
            
            # Detalles
            print(f"\n📦 DETALLES DE ACTUALIZACIÓN:")
            print(f"   Actualizados:  {data.get('updated')}")
            print(f"   No encontrados: {data.get('not_found')}")
            print(f"   Errores:        {data.get('errors')}")
            
            # Primeros productos actualizados
            if data.get('updated_products'):
                print(f"\n🖼️  PRIMEROS PRODUCTOS ACTUALIZADOS:")
                for product in data.get('updated_products', [])[:5]:
                    print(f"   ✓ {product['name']}")
                    print(f"     URL: {product['image_url'][:60]}...")
            
            # Advertencias
            if data.get('not_found_products'):
                print(f"\n⚠️  PRODUCTOS NO ENCONTRADOS EN BD:")
                for name in data.get('not_found_products')[:5]:
                    print(f"   • {name}")
            
            if data.get('error_details'):
                print(f"\n❌ ERRORES:")
                for error in data.get('error_details'):
                    print(f"   • {error['product']}: {error['error']}")
            
            print("\n" + "=" * 70)
            print("🎉 PROCESO COMPLETADO")
            print("=" * 70)
            print("\n💡 Verifica con: python check_production_full.py")
            
        elif response.status_code == 401:
            print("\n❌ ERROR: Token inválido o expirado")
            print("   Solución: Genera un nuevo token de admin")
            
        elif response.status_code == 403:
            print("\n❌ ERROR: No tienes permisos de administrador")
            print("   Solución: Usa un token de cuenta ADMIN")
            
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(f"   Respuesta: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("\n⏱️  ERROR: Timeout (60s) - El servidor tardó demasiado")
        print("   El proceso podría estar ejecutándose en el servidor")
        print("   Espera 2 minutos y verifica con check_production_full.py")
        
    except requests.exceptions.ConnectionError:
        print("\n🌐 ERROR: No se pudo conectar al servidor")
        print("   Verifica tu conexión a internet")
        print("   Verifica que el servidor esté activo")
        
    except Exception as e:
        print(f"\n💥 ERROR INESPERADO: {e}")

if __name__ == "__main__":
    main()
