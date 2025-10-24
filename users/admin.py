# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Añadimos el campo 'role' a la lista que se muestra en el admin
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')

    # Añadimos el campo 'role' a los campos editables en el detalle del usuario
    # Lo agregamos a un nuevo "fieldset" para que se vea organizado
    fieldsets = UserAdmin.fieldsets + (
        ('Roles y Permisos', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
