from users.models import CustomUser

# Verificar usuarios existentes
users = CustomUser.objects.all()
print("=== USUARIOS EN LA BASE DE DATOS ===")
for u in users:
    print(f"Email: {u.email}, Username: {u.username}, Is Staff: {u.is_staff}")

# Crear o actualizar admin
admin_email = "admin@smartsales365.com"
try:
    admin = CustomUser.objects.get(email=admin_email)
    print(f"\n✅ Usuario admin encontrado: {admin.email}")
    admin.set_password("admin123")
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print("✅ Contraseña actualizada a 'admin123'")
except CustomUser.DoesNotExist:
    admin = CustomUser.objects.create_superuser(
        email=admin_email,
        username="admin",
        password="admin123",
        first_name="Admin",
        last_name="User"
    )
    print(f"\n✅ Usuario admin creado: {admin.email}")
    print("✅ Contraseña: admin123")

print("\n=== CREDENCIALES PARA LOGIN ===")
print(f"Email: {admin.email}")
print("Password: admin123")
print("\n=== PARA JWT USE ===")
print(f'{{ "username": "{admin.email}", "password": "admin123" }}')
