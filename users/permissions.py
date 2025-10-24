# users/permissions.py

from rest_framework import permissions

class IsAdminOrSelf(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo a los administradores o al propio usuario
    editar o ver su información.
    """
    def has_permission(self, request, view):
        # Permitir acceso solo a usuarios autenticados
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Los administradores (is_staff) o superusuarios tienen permiso siempre.
        if request.user and request.user.is_staff:
            return True
        
        # El propio usuario tiene permiso para ver o editar su perfil.
        return obj == request.user