# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Wallet, WalletTransaction

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


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('balance', 'created_at', 'updated_at')
    ordering = ('-balance',)


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'balance_after', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('wallet__user__username', 'description', 'reference_id')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
