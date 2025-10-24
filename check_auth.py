from users.models import CustomUser
from django.contrib.auth import authenticate

print("=== VERIFICANDO CONFIGURACION ===")
print(f"USERNAME_FIELD: {CustomUser.USERNAME_FIELD}")

admin = CustomUser.objects.get(email='admin@smartsales365.com')
print(f"\nAdmin username: {admin.username}")
print(f"Admin email: {admin.email}")
print(f"Check password 'admin123': {admin.check_password('admin123')}")

# Probar authenticate con username
print("\n=== PROBANDO AUTHENTICATE ===")
user1 = authenticate(username='admin@smartsales365.com', password='admin123')
print(f"authenticate(username='admin@smartsales365.com'): {user1}")

user2 = authenticate(username='admin', password='admin123')
print(f"authenticate(username='admin'): {user2}")

# Probar con email
user3 = authenticate(email='admin@smartsales365.com', password='admin123')
print(f"authenticate(email='admin@smartsales365.com'): {user3}")

print("\n=== SOLUCION ===")
if user2:
    print(f'✅ Para JWT usa: {{ "username": "admin", "password": "admin123" }}')
elif user1:
    print(f'✅ Para JWT usa: {{ "username": "admin@smartsales365.com", "password": "admin123" }}')
