from .models import AuditLog


class AuditMiddleware:
    """
    Middleware para registrar automáticamente todas las acciones en la bitácora
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Procesar request
        response = self.get_response(request)
        
        # Registrar en auditoría (solo para ciertos endpoints)
        self.log_request(request, response)
        
        return response
    
    def log_request(self, request, response):
        """Registrar la solicitud en auditoría"""
        
        # Ignorar ciertos paths
        ignored_paths = [
            '/admin/jsi18n/',
            '/static/',
            '/media/',
            '/favicon.ico',
        ]
        
        if any(request.path.startswith(path) for path in ignored_paths):
            return
        
        # Determinar acción basado en el path y método
        action = self.determine_action(request, response)
        if not action:
            return
        
        # Determinar severidad basado en status code
        severity = self.determine_severity(response.status_code)
        
        # Obtener descripción
        description = self.get_description(request, response)
        
        # Obtener información del objeto si es posible
        object_type, object_id, object_repr = self.extract_object_info(request)
        
        # Determinar si fue exitoso
        success = 200 <= response.status_code < 400
        
        # Registrar en auditoría
        try:
            AuditLog.log_action(
                action=action,
                request=request,
                description=description,
                object_type=object_type,
                object_id=object_id,
                object_repr=object_repr,
                success=success,
                severity=severity,
                extra_data={
                    'status_code': response.status_code,
                    'content_type': response.get('Content-Type', ''),
                }
            )
        except Exception as e:
            # No fallar si el logging falla
            print(f"Error en AuditMiddleware: {e}")
    
    def determine_action(self, request, response):
        """Determinar el tipo de acción basado en el path y método"""
        path = request.path
        method = request.method
        
        # Login/Logout
        if 'token' in path and method == 'POST':
            return 'LOGIN' if response.status_code == 200 else 'LOGIN_FAILED'
        
        if 'logout' in path:
            return 'LOGOUT'
        
        # Usuarios
        if '/users/' in path:
            if method == 'POST':
                return 'USER_CREATE'
            elif method in ['PUT', 'PATCH']:
                return 'USER_UPDATE'
            elif method == 'DELETE':
                return 'USER_DELETE'
        
        # Productos
        if '/products/' in path:
            if method == 'POST':
                return 'PRODUCT_CREATE'
            elif method in ['PUT', 'PATCH']:
                return 'PRODUCT_UPDATE'
            elif method == 'DELETE':
                return 'PRODUCT_DELETE'
            elif method == 'GET' and path.split('/')[-2].isdigit():
                return 'PRODUCT_VIEW'
        
        # Órdenes
        if '/orders/' in path:
            if 'create' in path:
                return 'ORDER_CREATE'
            elif method in ['PUT', 'PATCH']:
                return 'ORDER_UPDATE'
            elif method == 'DELETE':
                return 'ORDER_DELETE'
            elif 'webhook' in path:
                return 'ORDER_PAYMENT'
        
        # NLP
        if 'natural-language' in path:
            return 'NLP_QUERY'
        
        # Reportes
        if '/reports/' in path:
            if 'download' in path or response.get('Content-Type', '').startswith('application/'):
                return 'REPORT_DOWNLOAD'
            return 'REPORT_GENERATE'
        
        # Exportación de datos
        if 'export' in path or response.get('Content-Disposition', '').startswith('attachment'):
            return 'DATA_EXPORT'
        
        # Si no coincide con nada conocido, no registrar
        return None
    
    def determine_severity(self, status_code):
        """Determinar severidad basado en código de estado"""
        if status_code >= 500:
            return 'CRITICAL'
        elif status_code >= 400:
            return 'ERROR'
        elif status_code >= 300:
            return 'WARNING'
        else:
            return 'INFO'
    
    def get_description(self, request, response):
        """Generar descripción de la acción"""
        method = request.method
        path = request.path
        status = response.status_code
        
        return f"{method} {path} - Status {status}"
    
    def extract_object_info(self, request):
        """Extraer información del objeto de la URL"""
        path_parts = request.path.strip('/').split('/')
        
        object_type = ''
        object_id = None
        object_repr = ''
        
        # Intentar extraer de la URL
        if 'products' in path_parts:
            object_type = 'Product'
            # Buscar el ID después de 'products'
            try:
                idx = path_parts.index('products')
                if idx + 1 < len(path_parts) and path_parts[idx + 1].isdigit():
                    object_id = int(path_parts[idx + 1])
            except:
                pass
        
        elif 'orders' in path_parts:
            object_type = 'Order'
            try:
                idx = path_parts.index('orders')
                if idx + 1 < len(path_parts) and path_parts[idx + 1].isdigit():
                    object_id = int(path_parts[idx + 1])
            except:
                pass
        
        elif 'users' in path_parts:
            object_type = 'User'
            try:
                idx = path_parts.index('users')
                if idx + 1 < len(path_parts) and path_parts[idx + 1].isdigit():
                    object_id = int(path_parts[idx + 1])
            except:
                pass
        
        return object_type, object_id, object_repr
