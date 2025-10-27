"""
Script para probar login de usuarios
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password, check_password

User = get_user_model()

print("\n" + "="*70)
print("  PRUEBA DE LOGIN - VERIFICACIÓN DE USUARIOS")
print("="*70 + "\n")

# Usuarios de prueba del seed_data
test_users = [
    ('admin', 'admin123'),
    ('juan_cliente', 'juan123'),
    ('maria_admin', 'maria123'),
    ('carlos_manager', 'carlos123'),
]

print("🔍 VERIFICANDO USUARIOS EN LA BASE DE DATOS:\n")

for username, password in test_users:
    try:
        user = User.objects.get(username=username)
        print(f"✅ Usuario encontrado: {username}")
        print(f"   - Email: {user.email}")
        print(f"   - is_active: {user.is_active}")
        print(f"   - has_usable_password: {user.has_usable_password()}")
        
        # Probar autenticación
        auth_user = authenticate(username=username, password=password)
        if auth_user:
            print(f"   - ✅ LOGIN EXITOSO con '{password}'")
        else:
            print(f"   - ❌ LOGIN FALLIDO con '{password}'")
            # Probar si la contraseña está hasheada correctamente
            if user.check_password(password):
                print(f"   - ⚠️  Password hash es correcto, pero authenticate() falla")
            else:
                print(f"   - ❌ Password hash NO coincide")
        print()
    except User.DoesNotExist:
        print(f"❌ Usuario NO encontrado: {username}\n")

print("="*70)
print("\n💡 PARA CORREGIR PASSWORDS MANUALMENTE:")
print("\n  Opción 1 - Volver a ejecutar seed_data.py:")
print("    python seed_data.py")
print("\n  Opción 2 - Resetear password de un usuario:")
print("    python manage.py shell")
print("    >>> from django.contrib.auth import get_user_model")
print("    >>> User = get_user_model()")
print("    >>> user = User.objects.get(username='juan_cliente')")
print("    >>> user.set_password('juan123')")
print("    >>> user.save()")
print("\n" + "="*70 + "\n")
