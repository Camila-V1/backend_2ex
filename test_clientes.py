import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

print('\n' + '='*60)
print('TEST: LOGIN DE CLIENTES (NO ADMIN)')
print('='*60)

# Obtener usuarios que NO son admin
clientes = User.objects.filter(is_staff=False)

print(f'\n📊 Total clientes registrados: {clientes.count()}')
print('\n--- LISTA DE CLIENTES ---')

for user in clientes:
    print(f'\nID: {user.id}')
    print(f'Username: {user.username}')
    print(f'Email: {user.email}')
    print(f'is_active: {user.is_active}')
    print(f'is_staff: {user.is_staff}')
    print(f'has_password: {user.has_usable_password()}')
    
    # Intentar autenticar con password genérico
    if user.username != 'admin':
        # Extraer solo el nombre del username (sin "_cliente")
        nombre = user.username.replace('_cliente', '')
        password_correcta = f'{nombre}123'  # Ej: juan123 (no juan_cliente123)
        
        password_intentos = [
            password_correcta,      # Ej: juan123
            f'{user.username}123',  # Ej: juan_cliente123
            user.username,
            'password123',
            'cliente123'
        ]
        
        print(f'\n🔐 Probando passwords para {user.username}:')
        for password in password_intentos:
            auth_user = authenticate(username=user.username, password=password)
            if auth_user:
                print(f'  ✅ {password} - LOGIN EXITOSO ✅')
                break
            else:
                print(f'  ❌ {password} - INCORRECTO')

print('\n' + '='*60)
print('RESUMEN:')
print('='*60)
print(f'Total clientes: {clientes.count()}')
print(f'Clientes activos: {clientes.filter(is_active=True).count()}')
print(f'Clientes con password: {sum(1 for u in clientes if u.has_usable_password())}')
