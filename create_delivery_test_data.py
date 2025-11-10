"""
Script para crear datos de prueba para el sistema de deliveries
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from deliveries.models import DeliveryZone, DeliveryProfile
from users.models import CustomUser


def create_delivery_zones():
    """Crear zonas de delivery"""
    zones = [
        {'name': 'Zona Norte', 'description': 'Incluye distritos del norte de la ciudad'},
        {'name': 'Zona Sur', 'description': 'Incluye distritos del sur de la ciudad'},
        {'name': 'Zona Este', 'description': 'Incluye distritos del este de la ciudad'},
        {'name': 'Zona Oeste', 'description': 'Incluye distritos del oeste de la ciudad'},
        {'name': 'Zona Centro', 'description': 'Incluye el centro histórico y áreas cercanas'},
    ]
    
    created_zones = []
    for zone_data in zones:
        zone, created = DeliveryZone.objects.get_or_create(
            name=zone_data['name'],
            defaults={'description': zone_data['description']}
        )
        if created:
            print(f"✅ Zona creada: {zone.name}")
        else:
            print(f"ℹ️  Zona ya existe: {zone.name}")
        created_zones.append(zone)
    
    return created_zones


def create_delivery_user():
    """Crear un usuario de prueba con rol DELIVERY"""
    # Verificar si ya existe
    if CustomUser.objects.filter(username='delivery1').exists():
        print("ℹ️  Usuario delivery1 ya existe")
        return CustomUser.objects.get(username='delivery1')
    
    user = CustomUser.objects.create_user(
        username='delivery1',
        email='delivery1@example.com',
        password='delivery123',
        first_name='Juan',
        last_name='Pérez',
        role='DELIVERY'
    )
    print(f"✅ Usuario delivery creado: {user.username}")
    return user


def create_delivery_profile(user, zone):
    """Crear perfil de delivery para el usuario"""
    if hasattr(user, 'delivery_profile'):
        print(f"ℹ️  Perfil de delivery ya existe para {user.username}")
        return user.delivery_profile
    
    profile = DeliveryProfile.objects.create(
        user=user,
        zone=zone,
        status='AVAILABLE',
        vehicle_type='Moto',
        license_plate='ABC-123',
        phone='+51 999 888 777'
    )
    print(f"✅ Perfil de delivery creado para {user.username}")
    return profile


def main():
    print("=" * 60)
    print("CREANDO DATOS DE PRUEBA PARA SISTEMA DE DELIVERIES")
    print("=" * 60)
    print()
    
    # 1. Crear zonas
    print("1️⃣  Creando zonas de delivery...")
    zones = create_delivery_zones()
    print()
    
    # 2. Crear usuario delivery
    print("2️⃣  Creando usuario delivery...")
    delivery_user = create_delivery_user()
    print()
    
    # 3. Crear perfil de delivery
    print("3️⃣  Creando perfil de delivery...")
    delivery_profile = create_delivery_profile(delivery_user, zones[0])  # Asignar a Zona Norte
    print()
    
    print("=" * 60)
    print("✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE")
    print("=" * 60)
    print()
    print("📋 CREDENCIALES DE ACCESO:")
    print(f"   Username: {delivery_user.username}")
    print(f"   Password: delivery123")
    print(f"   Rol: {delivery_user.role}")
    print(f"   Zona: {delivery_profile.zone.name}")
    print()


if __name__ == '__main__':
    main()
