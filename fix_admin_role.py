"""
Script para asignar el rol ADMIN al usuario admin.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Actualizar el usuario admin
admin_user = User.objects.get(username='admin')
admin_user.role = 'ADMIN'
admin_user.save()

print(f"✓ Usuario admin actualizado: role='{admin_user.role}'")
print(f"  - is_staff: {admin_user.is_staff}")
print(f"  - is_superuser: {admin_user.is_superuser}")
