from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer para registros de auditoría"""
    
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    user_display = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'action',
            'action_display',
            'severity',
            'severity_display',
            'user',
            'username',
            'user_display',
            'ip_address',
            'user_agent',
            'method',
            'path',
            'description',
            'object_type',
            'object_id',
            'object_repr',
            'extra_data',
            'timestamp',
            'success',
            'error_message'
        ]
        read_only_fields = fields
    
    def get_user_display(self, obj):
        """Mostrar nombre completo del usuario"""
        if obj.user:
            return f"{obj.user.get_full_name()} ({obj.user.username})"
        return obj.username or 'Anónimo'


class AuditLogFilterSerializer(serializers.Serializer):
    """Serializer para filtros de búsqueda"""
    
    action = serializers.ChoiceField(
        choices=AuditLog.ActionType.choices,
        required=False,
        help_text='Tipo de acción'
    )
    
    severity = serializers.ChoiceField(
        choices=AuditLog.SeverityLevel.choices,
        required=False,
        help_text='Nivel de severidad'
    )
    
    user_id = serializers.IntegerField(
        required=False,
        help_text='ID del usuario'
    )
    
    username = serializers.CharField(
        required=False,
        help_text='Nombre de usuario'
    )
    
    ip_address = serializers.IPAddressField(
        required=False,
        help_text='Dirección IP'
    )
    
    object_type = serializers.CharField(
        required=False,
        help_text='Tipo de objeto (Product, Order, etc.)'
    )
    
    object_id = serializers.IntegerField(
        required=False,
        help_text='ID del objeto'
    )
    
    start_date = serializers.DateTimeField(
        required=False,
        help_text='Fecha inicial (YYYY-MM-DD o YYYY-MM-DD HH:MM:SS)'
    )
    
    end_date = serializers.DateTimeField(
        required=False,
        help_text='Fecha final (YYYY-MM-DD o YYYY-MM-DD HH:MM:SS)'
    )
    
    success = serializers.BooleanField(
        required=False,
        help_text='Filtrar por éxito (true) o error (false)'
    )
    
    search = serializers.CharField(
        required=False,
        help_text='Búsqueda en descripción, path, error_message'
    )
