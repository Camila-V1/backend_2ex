# users/device_token_serializers.py
"""
Serializers para manejo de tokens de dispositivos FCM
"""

from rest_framework import serializers
from .device_token_models import DeviceToken, NotificationLog


class DeviceTokenSerializer(serializers.ModelSerializer):
    """Serializer para registrar/actualizar tokens de dispositivos"""
    
    class Meta:
        model = DeviceToken
        fields = [
            'id',
            'token',
            'device_type',
            'device_id',
            'device_name',
            'is_active',
            'created_at',
            'last_used_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_used_at', 'is_active']
    
    def create(self, validated_data):
        """
        Crea o actualiza el token del dispositivo
        Si el token ya existe, lo actualiza en vez de crear uno nuevo
        """
        token = validated_data.get('token')
        user = self.context['request'].user
        
        # Intentar encontrar un token existente
        device_token, created = DeviceToken.objects.update_or_create(
            token=token,
            defaults={
                'user': user,
                'device_type': validated_data.get('device_type', 'ANDROID'),
                'device_id': validated_data.get('device_id'),
                'device_name': validated_data.get('device_name'),
                'is_active': True,
            }
        )
        
        return device_token


class DeviceTokenListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar tokens"""
    
    class Meta:
        model = DeviceToken
        fields = ['id', 'device_type', 'device_name', 'is_active', 'created_at']


class NotificationLogSerializer(serializers.ModelSerializer):
    """Serializer para ver el historial de notificaciones"""
    
    device_info = serializers.SerializerMethodField()
    
    class Meta:
        model = NotificationLog
        fields = [
            'id',
            'title',
            'body',
            'notification_type',
            'data',
            'status',
            'error_message',
            'device_info',
            'created_at'
        ]
    
    def get_device_info(self, obj):
        if obj.device_token:
            return {
                'device_type': obj.device_token.device_type,
                'device_name': obj.device_token.device_name
            }
        return None
