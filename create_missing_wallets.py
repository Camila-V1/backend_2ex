#!/usr/bin/env python3
"""
Script para crear billeteras faltantes para todos los usuarios
Soluciona el error 404 en /wallet/my_wallet/
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from users.models import CustomUser
from users.wallet_models import Wallet

def create_missing_wallets():
    """Crea billeteras para usuarios que no tienen"""
    print("🔍 Buscando usuarios sin billetera...")
    
    users_without_wallet = CustomUser.objects.filter(wallet__isnull=True)
    total_users = CustomUser.objects.count()
    
    print(f"📊 Total usuarios: {total_users}")
    print(f"⚠️ Usuarios sin billetera: {users_without_wallet.count()}\n")
    
    if users_without_wallet.count() == 0:
        print("✅ Todos los usuarios ya tienen billetera!")
        return
    
    created = 0
    for user in users_without_wallet:
        try:
            wallet = Wallet.objects.create(user=user, balance=0.00)
            print(f"✅ Billetera creada para: {user.username} (ID: {user.id})")
            created += 1
        except Exception as e:
            print(f"❌ Error creando billetera para {user.username}: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Total billeteras creadas: {created}")
    print(f"{'='*60}\n")
    
    # Verificar
    users_with_wallet = CustomUser.objects.filter(wallet__isnull=False).count()
    print(f"📊 Verificación final:")
    print(f"   Usuarios con billetera: {users_with_wallet}/{total_users}")
    
    if users_with_wallet == total_users:
        print(f"   ✅ ¡Todos los usuarios tienen billetera ahora!")
    else:
        print(f"   ⚠️ Aún faltan {total_users - users_with_wallet} billeteras")


if __name__ == '__main__':
    create_missing_wallets()
