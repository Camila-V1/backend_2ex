from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin para registros de auditoría"""
    
    list_display = ['timestamp', 'action', 'severity', 'username', 'ip_address', 
                    'method', 'success', 'object_type']
    list_filter = ['action', 'severity', 'success', 'timestamp', 'object_type']
    search_fields = ['username', 'ip_address', 'description', 'path', 'error_message']
    readonly_fields = ['timestamp', 'action', 'severity', 'user', 'username', 
                       'ip_address', 'user_agent', 'method', 'path', 'description',
                       'object_type', 'object_id', 'object_repr', 'extra_data',
                       'success', 'error_message']
    
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        """No permitir agregar registros manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar registros"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo superusuarios pueden eliminar"""
        return request.user.is_superuser
