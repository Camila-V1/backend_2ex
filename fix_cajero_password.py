"""
Script para resetear la contraseña del cajero luis_cajero
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def fix_cajero():
    print("=" * 60)
    print("🔧 ARREGLANDO CONTRASEÑA DE CAJERO")
    print("=" * 60)
    
    # Buscar usuario
    cajero = User.objects.filter(username='luis_cajero').first()
    
    if not cajero:
        print("❌ Usuario luis_cajero no existe")
        print("\n✨ Creando usuario luis_cajero...")
        
        cajero = User.objects.create_user(
            username='luis_cajero',
            email='luis.cajero@ecommerce.com',
            password='cajero123',
            first_name='Luis',
            last_name='Cajero',
            role='CAJERO'
        )
        print("✅ Usuario creado exitosamente")
    else:
        print(f"✅ Usuario encontrado: {cajero.username}")
        print(f"   Email: {cajero.email}")
        print(f"   Role: {cajero.role}")
        print(f"   Is active: {cajero.is_active}")
        
        # Resetear contraseña
        print("\n🔐 Reseteando contraseña a 'cajero123'...")
        cajero.set_password('cajero123')
        cajero.is_active = True
        cajero.role = 'CAJERO'
        cajero.save()
        print("✅ Contraseña actualizada")
    
    # Verificar otros cajeros
    print("\n📋 Verificando todos los cajeros...")
    cajeros = User.objects.filter(role='CAJERO')
    
    for c in cajeros:
        print(f"\n   Usuario: {c.username}")
        print(f"   Email: {c.email}")
        print(f"   Activo: {c.is_active}")
        print(f"   Role: {c.role}")
    
    print("\n" + "=" * 60)
    print("✅ PROCESO COMPLETADO")
    print("=" * 60)
    print("\n📝 Credenciales:")
    print("   Usuario: luis_cajero")
    print("   Contraseña: cajero123")
    print("\n🧪 Prueba de login:")
    print("   curl -X POST http://localhost:8000/api/token/ \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"username\":\"luis_cajero\",\"password\":\"cajero123\"}'")

if __name__ == "__main__":
    fix_cajero()
