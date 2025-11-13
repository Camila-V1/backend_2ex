# users/device_token_views.py
"""
ViewSets y vistas para manejo de tokens de dispositivos FCM
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .device_token_models import DeviceToken, NotificationLog
from .device_token_serializers import (
    DeviceTokenSerializer,
    DeviceTokenListSerializer,
    NotificationLogSerializer
)


class DeviceTokenViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar tokens de dispositivos FCM
    
    - list: GET /api/device-tokens/ - Lista tokens del usuario autenticado
    - create: POST /api/device-tokens/ - Registra un nuevo token
    - retrieve: GET /api/device-tokens/{id}/ - Detalle de un token
    - update: PUT /api/device-tokens/{id}/ - Actualiza un token
    - destroy: DELETE /api/device-tokens/{id}/ - Elimina un token
    """
    
    serializer_class = DeviceTokenSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Solo muestra los tokens del usuario autenticado"""
        return DeviceToken.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DeviceTokenListSerializer
        return DeviceTokenSerializer
    
    @extend_schema(
        request=DeviceTokenSerializer,
        responses={201: DeviceTokenSerializer},
        description="Registra un nuevo token FCM para el dispositivo del usuario",
        tags=['Push Notifications']
    )
    def create(self, request, *args, **kwargs):
        """Registra o actualiza un token FCM"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device_token = serializer.save()
        
        return Response(
            {
                'success': True,
                'message': 'Token registrado correctamente',
                'data': DeviceTokenSerializer(device_token).data
            },
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        responses={204: None},
        description="Desactiva (pero no elimina) el token del dispositivo",
        tags=['Push Notifications']
    )
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Desactiva un token (útil al hacer logout)"""
        device_token = self.get_object()
        device_token.deactivate()
        
        return Response(
            {'success': True, 'message': 'Token desactivado'},
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        responses={200: NotificationLogSerializer(many=True)},
        description="Obtiene el historial de notificaciones del usuario",
        tags=['Push Notifications']
    )
    @action(detail=False, methods=['get'])
    def notification_history(self, request):
        """Lista el historial de notificaciones del usuario"""
        logs = NotificationLog.objects.filter(user=request.user)[:50]
        serializer = NotificationLogSerializer(logs, many=True)
        
        return Response({
            'success': True,
            'count': logs.count(),
            'results': serializer.data
        })


@extend_schema(
    request=DeviceTokenSerializer,
    responses={200: DeviceTokenSerializer},
    description="Registra el token FCM del dispositivo Flutter",
    tags=['Push Notifications']
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def register_device_token(request):
    """
    Endpoint simplificado para que Flutter registre su token FCM
    
    POST /api/users/register-device-token/
    {
        "token": "fcm_token_here",
        "device_type": "ANDROID",  // o "IOS"
        "device_id": "unique_device_id",
        "device_name": "Samsung Galaxy S23"
    }
    """
    
    serializer = DeviceTokenSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        device_token = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Token de dispositivo registrado correctamente',
            'device_token': {
                'id': device_token.id,
                'device_type': device_token.device_type,
                'is_active': device_token.is_active,
                'created_at': device_token.created_at
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses={200: {'type': 'object'}},
    description="Elimina todos los tokens del usuario (útil al hacer logout)",
    tags=['Push Notifications']
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unregister_all_tokens(request):
    """
    Desactiva todos los tokens del usuario autenticado
    Útil al hacer logout completo
    """
    
    count = DeviceToken.objects.filter(user=request.user, is_active=True).update(is_active=False)
    
    return Response({
        'success': True,
        'message': f'{count} token(s) desactivado(s)',
        'count': count
    }, status=status.HTTP_200_OK)
