# users/views.py

from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import CustomUser
from .serializers import UserRegistrationSerializer, UserProfileSerializer
from .permissions import IsAdminOrSelf

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet que maneja el CRUD completo para los Usuarios.
    - list: GET /api/users/ (Solo Admins)
    - create: POST /api/users/ (Cualquiera puede registrarse)
    - retrieve: GET /api/users/{id}/ (Admin o el propio usuario)
    - update: PUT /api/users/{id}/ (Admin o el propio usuario)
    - partial_update: PATCH /api/users/{id}/ (Admin o el propio usuario)
    - destroy: DELETE /api/users/{id}/ (Admin o el propio usuario)
    """
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        # Usamos el serializer de registro para la acción 'create'
        if self.action == 'create':
            return UserRegistrationSerializer
        # Para todas las demás acciones (ver, editar), usamos el serializer de perfil
        return UserProfileSerializer

    def get_permissions(self):
        # Permitimos que cualquiera pueda crear (registrarse)
        if self.action == 'create':
            self.permission_classes = [permissions.AllowAny]
        # Para listar usuarios, solo administradores
        elif self.action == 'list':
            self.permission_classes = [permissions.IsAdminUser]
        # Para las demás acciones, requerimos que sea Admin o el propio usuario
        else:
            self.permission_classes = [IsAdminOrSelf]
        return super().get_permissions()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """
    Devuelve el perfil del usuario autenticado
    GET /api/users/profile/
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)
