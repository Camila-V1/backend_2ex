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


class IsAdminUser(permissions.BasePermission):
    """
    Permiso para usuarios con rol ADMIN.
    """
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.role == 'ADMIN'
        )


class IsManagerUser(permissions.BasePermission):
    """
    Permiso para usuarios con rol MANAGER.
    Managers pueden ver reportes y gestionar productos/categorías.
    """
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.role in ['MANAGER', 'ADMIN']
        )


class IsCajeroUser(permissions.BasePermission):
    """
    Permiso para usuarios con rol CAJERO.
    Cajeros pueden crear órdenes y ver productos.
    """
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.role in ['CAJERO', 'MANAGER', 'ADMIN']
        )


class IsAdminOrManager(permissions.BasePermission):
    """
    Permiso para ADMIN o MANAGER.
    """
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.role in ['ADMIN', 'MANAGER']
        )


class CanViewReports(permissions.BasePermission):
    """
    Permiso para ver reportes (ADMIN, MANAGER).
    """
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.role in ['ADMIN', 'MANAGER']
        )


class IsDeliveryUser(permissions.BasePermission):
    """
    Permiso para usuarios con rol DELIVERY.
    Delivery puede ver y actualizar sus entregas asignadas.
    """
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.role in ['DELIVERY', 'MANAGER', 'ADMIN']
        )