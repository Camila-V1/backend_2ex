# users/device_token_models.py
"""
Modelo para almacenar tokens de dispositivos FCM (Firebase Cloud Messaging)
Permite enviar notificaciones push a múltiples dispositivos de un mismo usuario
"""

from django.db import models
from django.conf import settings


class DeviceToken(models.Model):
    """
    Almacena tokens FCM de dispositivos para enviar notificaciones push
    Un usuario puede tener múltiples dispositivos (móvil, tablet, etc.)
    """
    
    DEVICE_TYPES = [
        ('ANDROID', 'Android'),
        ('IOS', 'iOS'),
        ('WEB', 'Web'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='device_tokens',
        help_text='Usuario propietario del dispositivo'
    )
    
    token = models.CharField(
        max_length=500,
        unique=True,
        help_text='Token FCM del dispositivo'
    )
    
    device_type = models.CharField(
        max_length=20,
        choices=DEVICE_TYPES,
        default='ANDROID',
        help_text='Tipo de dispositivo'
    )
    
    device_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='ID único del dispositivo (opcional)'
    )
    
    device_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Nombre del dispositivo (ej: "iPhone 15 Pro de Juan")'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Si está activo (se desactiva si el token es inválido)'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de registro del token'
    )
    
    last_used_at = models.DateTimeField(
        auto_now=True,
        help_text='Última vez que se usó este token'
    )
    
    class Meta:
        verbose_name = 'Token de Dispositivo'
        verbose_name_plural = 'Tokens de Dispositivos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['token']),
        ]
    
    def __str__(self):
        device_info = self.device_name or f"{self.device_type} {self.device_id or ''}"
        return f"{self.user.username} - {device_info}"
    
    def deactivate(self):
        """Desactiva el token (útil cuando FCM devuelve error de token inválido)"""
        self.is_active = False
        self.save(update_fields=['is_active'])


class NotificationLog(models.Model):
    """
    Registro de notificaciones enviadas para auditoría y debugging
    """
    
    STATUS_CHOICES = [
        ('SENT', 'Enviada'),
        ('FAILED', 'Fallida'),
        ('DELIVERED', 'Entregada'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_logs'
    )
    
    device_token = models.ForeignKey(
        DeviceToken,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notification_logs'
    )
    
    title = models.CharField(max_length=255)
    body = models.TextField()
    
    notification_type = models.CharField(
        max_length=50,
        help_text='Tipo de notificación: ORDER_DELIVERED, RETURN_APPROVED, etc.'
    )
    
    data = models.JSONField(
        default=dict,
        blank=True,
        help_text='Datos adicionales enviados con la notificación'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SENT'
    )
    
    error_message = models.TextField(
        blank=True,
        null=True,
        help_text='Mensaje de error si la notificación falló'
    )
    
    fcm_response = models.JSONField(
        default=dict,
        blank=True,
        help_text='Respuesta completa de FCM'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Log de Notificación'
        verbose_name_plural = 'Logs de Notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'notification_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} - {self.user.username} ({self.status})"
