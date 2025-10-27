from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AuditLog(models.Model):
    """
    🔍 Modelo de Bitácora/Auditoría del Sistema
    Registra todas las acciones importantes del sistema con detalles completos
    """
    
    # Tipos de acciones
    class ActionType(models.TextChoices):
        # Autenticación
        LOGIN = 'LOGIN', 'Inicio de Sesión'
        LOGOUT = 'LOGOUT', 'Cierre de Sesión'
        LOGIN_FAILED = 'LOGIN_FAILED', 'Intento de Login Fallido'
        
        # Usuarios
        USER_CREATE = 'USER_CREATE', 'Creación de Usuario'
        USER_UPDATE = 'USER_UPDATE', 'Actualización de Usuario'
        USER_DELETE = 'USER_DELETE', 'Eliminación de Usuario'
        
        # Productos
        PRODUCT_CREATE = 'PRODUCT_CREATE', 'Creación de Producto'
        PRODUCT_UPDATE = 'PRODUCT_UPDATE', 'Actualización de Producto'
        PRODUCT_DELETE = 'PRODUCT_DELETE', 'Eliminación de Producto'
        PRODUCT_VIEW = 'PRODUCT_VIEW', 'Visualización de Producto'
        
        # Órdenes
        ORDER_CREATE = 'ORDER_CREATE', 'Creación de Orden'
        ORDER_UPDATE = 'ORDER_UPDATE', 'Actualización de Orden'
        ORDER_DELETE = 'ORDER_DELETE', 'Eliminación de Orden'
        ORDER_PAYMENT = 'ORDER_PAYMENT', 'Pago de Orden'
        ORDER_CANCEL = 'ORDER_CANCEL', 'Cancelación de Orden'
        
        # Reportes
        REPORT_GENERATE = 'REPORT_GENERATE', 'Generación de Reporte'
        REPORT_DOWNLOAD = 'REPORT_DOWNLOAD', 'Descarga de Reporte'
        
        # NLP
        NLP_QUERY = 'NLP_QUERY', 'Consulta NLP'
        
        # Sistema
        SYSTEM_ERROR = 'SYSTEM_ERROR', 'Error del Sistema'
        PERMISSION_DENIED = 'PERMISSION_DENIED', 'Acceso Denegado'
        DATA_EXPORT = 'DATA_EXPORT', 'Exportación de Datos'
        
    # Niveles de severidad
    class SeverityLevel(models.TextChoices):
        INFO = 'INFO', 'Información'
        WARNING = 'WARNING', 'Advertencia'
        ERROR = 'ERROR', 'Error'
        CRITICAL = 'CRITICAL', 'Crítico'
    
    # Campos principales
    action = models.CharField(
        max_length=50,
        choices=ActionType.choices,
        verbose_name='Acción'
    )
    
    severity = models.CharField(
        max_length=20,
        choices=SeverityLevel.choices,
        default=SeverityLevel.INFO,
        verbose_name='Severidad'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='Usuario'
    )
    
    username = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Nombre de Usuario',
        help_text='Guardado en caso de que el usuario sea eliminado'
    )
    
    # Información de la solicitud
    ip_address = models.GenericIPAddressField(
        verbose_name='Dirección IP',
        null=True,
        blank=True
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    
    method = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Método HTTP'
    )
    
    path = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Ruta'
    )
    
    # Detalles de la acción
    description = models.TextField(
        verbose_name='Descripción',
        blank=True
    )
    
    object_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Tipo de Objeto',
        help_text='Ej: Product, Order, User'
    )
    
    object_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='ID del Objeto'
    )
    
    object_repr = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Representación del Objeto'
    )
    
    # Datos adicionales (JSON)
    extra_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Datos Adicionales',
        help_text='Información adicional en formato JSON'
    )
    
    # Timestamps
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y Hora',
        db_index=True
    )
    
    # Status
    success = models.BooleanField(
        default=True,
        verbose_name='Exitoso'
    )
    
    error_message = models.TextField(
        blank=True,
        verbose_name='Mensaje de Error'
    )
    
    class Meta:
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['severity']),
        ]
    
    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {self.get_action_display()} - {self.username or 'Anónimo'}"
    
    @classmethod
    def log_action(cls, action, request=None, user=None, description='', 
                   object_type='', object_id=None, object_repr='', 
                   extra_data=None, success=True, error_message='', severity='INFO'):
        """
        Método helper para crear registros de auditoría fácilmente
        """
        # Obtener usuario
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
        
        # Obtener IP
        ip_address = None
        if request:
            ip_address = cls.get_client_ip(request)
        
        # Obtener User Agent
        user_agent = ''
        if request:
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Obtener método y path
        method = ''
        path = ''
        if request:
            method = request.method
            path = request.path
        
        # Crear registro
        return cls.objects.create(
            action=action,
            severity=severity,
            user=user,
            username=user.username if user else 'Anónimo',
            ip_address=ip_address,
            user_agent=user_agent,
            method=method,
            path=path,
            description=description,
            object_type=object_type,
            object_id=object_id,
            object_repr=object_repr,
            extra_data=extra_data or {},
            success=success,
            error_message=error_message
        )
    
    @staticmethod
    def get_client_ip(request):
        """Obtener la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
