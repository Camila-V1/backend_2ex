from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import DeliveryZone, DeliveryProfile, Delivery, Warranty, Return, Repair
from .serializers import (
    DeliveryZoneSerializer, DeliveryProfileSerializer, DeliveryProfileSimpleSerializer,
    DeliverySerializer, WarrantySerializer, ReturnSerializer, RepairSerializer
)
from users.permissions import IsAdminUser, IsManagerUser, IsDeliveryUser, IsAdminOrManager
from shop_orders.models import Order


class DeliveryZoneViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar zonas de delivery"""
    queryset = DeliveryZone.objects.all()
    serializer_class = DeliveryZoneSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class DeliveryProfileViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar perfiles de repartidores"""
    queryset = DeliveryProfile.objects.select_related('user', 'zone').all()
    serializer_class = DeliveryProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['zone', 'status']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']
    ordering_fields = ['created_at', 'user__username']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAdminOrManager])
    def available(self, request):
        """Obtener repartidores disponibles (no ocupados ni offline)"""
        zone_id = request.query_params.get('zone', None)
        
        queryset = self.queryset.filter(
            status=DeliveryProfile.DeliveryStatus.AVAILABLE
        )
        
        if zone_id:
            queryset = queryset.filter(zone_id=zone_id)
        
        serializer = DeliveryProfileSimpleSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsDeliveryUser])
    def update_status(self, request, pk=None):
        """Permitir a un repartidor actualizar su propio estado"""
        profile = self.get_object()
        
        # Verificar que el usuario sea el dueño del perfil o sea manager/admin
        if profile.user != request.user and request.user.role not in ['MANAGER', 'ADMIN']:
            return Response(
                {'error': 'No tienes permiso para actualizar este perfil'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'Debe proporcionar un estado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in dict(DeliveryProfile.DeliveryStatus.choices):
            return Response(
                {'error': f'Estado inválido: {new_status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        profile.status = new_status
        profile.save()
        
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class DeliveryViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar entregas"""
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'zone', 'delivery_person']
    search_fields = ['order__id', 'delivery_address', 'customer_phone']
    ordering_fields = ['created_at', 'assigned_at', 'delivered_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filtrar entregas según el rol del usuario"""
        user = self.request.user
        
        # Base queryset con select_related para optimizar
        queryset = Delivery.objects.select_related(
            'order',
            'order__user',
            'delivery_person',
            'delivery_person__user',
            'delivery_person__zone',
            'zone'
        ).prefetch_related(
            'order__items',
            'order__items__product'
        ).all()
        
        # Si es repartidor, solo ver sus propias entregas
        if user.role == 'DELIVERY':
            try:
                profile = DeliveryProfile.objects.get(user=user)
                return queryset.filter(delivery_person=profile)
            except DeliveryProfile.DoesNotExist:
                return queryset.none()
        
        # Managers y admins ven todo
        return queryset
    
    def get_permissions(self):
        """Permisos específicos por acción"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'assign_delivery']:
            permission_classes = [IsAuthenticated, IsAdminOrManager]
        elif self.action in ['my_deliveries', 'update_delivery_status']:
            permission_classes = [IsAuthenticated, IsDeliveryUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsDeliveryUser])
    def my_deliveries(self, request):
        """Obtener las entregas asignadas al repartidor autenticado"""
        try:
            profile = DeliveryProfile.objects.get(user=request.user)
        except DeliveryProfile.DoesNotExist:
            return Response(
                {'error': 'No tienes un perfil de repartidor'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Filtrar por estado si se proporciona
        status_filter = request.query_params.get('status', None)
        
        queryset = self.queryset.filter(delivery_person=profile)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        else:
            # Por defecto, mostrar solo entregas activas (no entregadas ni fallidas)
            queryset = queryset.exclude(
                status__in=[
                    Delivery.DeliveryStatus.DELIVERED,
                    Delivery.DeliveryStatus.FAILED
                ]
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminOrManager])
    def assign_delivery(self, request, pk=None):
        """Asignar un repartidor a una entrega"""
        delivery = self.get_object()
        delivery_person_id = request.data.get('delivery_person_id')
        
        if not delivery_person_id:
            return Response(
                {'error': 'Debe proporcionar el ID del repartidor'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            delivery_person = DeliveryProfile.objects.get(id=delivery_person_id)
        except DeliveryProfile.DoesNotExist:
            return Response(
                {'error': 'Repartidor no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que el repartidor esté disponible
        if delivery_person.status == DeliveryProfile.DeliveryStatus.OFFLINE:
            return Response(
                {'error': 'El repartidor está desconectado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Asignar repartidor
        delivery.delivery_person = delivery_person
        delivery.zone = delivery_person.zone
        delivery.status = Delivery.DeliveryStatus.ASSIGNED
        delivery.assigned_at = timezone.now()
        delivery.save()
        
        # Actualizar estado del repartidor a BUSY
        delivery_person.status = DeliveryProfile.DeliveryStatus.BUSY
        delivery_person.save()
        
        serializer = self.get_serializer(delivery)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsDeliveryUser])
    def update_delivery_status(self, request, pk=None):
        """Permitir al repartidor actualizar el estado de la entrega"""
        delivery = self.get_object()
        
        # Verificar que el usuario sea el repartidor asignado
        if not hasattr(request.user, 'deliveryprofile') or delivery.delivery_person != request.user.deliveryprofile:
            if request.user.role not in ['MANAGER', 'ADMIN']:
                return Response(
                    {'error': 'No tienes permiso para actualizar esta entrega'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if not new_status:
            return Response(
                {'error': 'Debe proporcionar un estado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar transición de estado
        valid_transitions = {
            Delivery.DeliveryStatus.PENDING: [Delivery.DeliveryStatus.ASSIGNED],
            Delivery.DeliveryStatus.ASSIGNED: [Delivery.DeliveryStatus.PICKED_UP, Delivery.DeliveryStatus.FAILED],
            Delivery.DeliveryStatus.PICKED_UP: [Delivery.DeliveryStatus.IN_TRANSIT, Delivery.DeliveryStatus.FAILED],
            Delivery.DeliveryStatus.IN_TRANSIT: [Delivery.DeliveryStatus.DELIVERED, Delivery.DeliveryStatus.FAILED],
        }
        
        if delivery.status not in valid_transitions or new_status not in valid_transitions[delivery.status]:
            return Response(
                {'error': f'No se puede cambiar de {delivery.status} a {new_status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar estado
        delivery.status = new_status
        if notes:
            delivery.notes = notes
        
        # Actualizar timestamps según el estado
        if new_status == Delivery.DeliveryStatus.PICKED_UP:
            delivery.picked_up_at = timezone.now()
        elif new_status == Delivery.DeliveryStatus.DELIVERED:
            delivery.delivered_at = timezone.now()
            # Liberar al repartidor
            if delivery.delivery_person:
                delivery.delivery_person.status = DeliveryProfile.DeliveryStatus.AVAILABLE
                delivery.delivery_person.save()
            # Actualizar estado de la orden
            delivery.order.status = Order.OrderStatus.DELIVERED
            delivery.order.save()
        elif new_status == Delivery.DeliveryStatus.FAILED:
            # Liberar al repartidor
            if delivery.delivery_person:
                delivery.delivery_person.status = DeliveryProfile.DeliveryStatus.AVAILABLE
                delivery.delivery_person.save()
        
        delivery.save()
        
        serializer = self.get_serializer(delivery)
        return Response(serializer.data)


class WarrantyViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar garantías"""
    serializer_class = WarrantySerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'product', 'order']
    search_fields = ['product__name', 'order__id']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Optimizar queryset con select_related"""
        return Warranty.objects.select_related(
            'order',
            'order__user',
            'product',
            'product__category'
        ).all()
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Obtener garantías activas y no vencidas"""
        today = timezone.now().date()
        queryset = self.queryset.filter(
            status=Warranty.WarrantyStatus.ACTIVE,
            end_date__gte=today
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        """Marcar una garantía como reclamada"""
        warranty = self.get_object()
        
        if warranty.status != Warranty.WarrantyStatus.ACTIVE:
            return Response(
                {'error': 'La garantía no está activa'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        today = timezone.now().date()
        if warranty.end_date < today:
            warranty.status = Warranty.WarrantyStatus.EXPIRED
            warranty.save()
            return Response(
                {'error': 'La garantía ha expirado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        warranty.status = Warranty.WarrantyStatus.CLAIMED
        warranty.notes = request.data.get('notes', warranty.notes)
        warranty.save()
        
        serializer = self.get_serializer(warranty)
        return Response(serializer.data)


class ReturnViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar devoluciones"""
    serializer_class = ReturnSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'reason', 'order', 'product']
    search_fields = ['order__id', 'product__name', 'description']
    ordering_fields = ['requested_at', 'processed_at', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Optimizar queryset con select_related"""
        return Return.objects.select_related(
            'order',
            'order__user',
            'product',
            'product__category'
        ).all()
    
    def get_permissions(self):
        """Clientes pueden crear, managers pueden aprobar/rechazar"""
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['approve', 'reject', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminOrManager]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminOrManager])
    def approve(self, request, pk=None):
        """Aprobar una devolución"""
        return_obj = self.get_object()
        
        if return_obj.status != Return.ReturnStatus.REQUESTED:
            return Response(
                {'error': 'Solo se pueden aprobar devoluciones en estado REQUESTED'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        refund_amount = request.data.get('refund_amount')
        manager_notes = request.data.get('manager_notes', '')
        
        if refund_amount is None:
            return Response(
                {'error': 'Debe especificar el monto de reembolso'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return_obj.status = Return.ReturnStatus.APPROVED
        return_obj.refund_amount = refund_amount
        return_obj.manager_notes = manager_notes
        return_obj.processed_at = timezone.now()
        return_obj.save()
        
        serializer = self.get_serializer(return_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminOrManager])
    def reject(self, request, pk=None):
        """Rechazar una devolución"""
        return_obj = self.get_object()
        
        if return_obj.status != Return.ReturnStatus.REQUESTED:
            return Response(
                {'error': 'Solo se pueden rechazar devoluciones en estado REQUESTED'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        manager_notes = request.data.get('manager_notes', '')
        
        if not manager_notes:
            return Response(
                {'error': 'Debe proporcionar una razón para el rechazo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return_obj.status = Return.ReturnStatus.REJECTED
        return_obj.manager_notes = manager_notes
        return_obj.processed_at = timezone.now()
        return_obj.save()
        
        serializer = self.get_serializer(return_obj)
        return Response(serializer.data)


class RepairViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar reparaciones"""
    serializer_class = RepairSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_under_warranty', 'order', 'product']
    search_fields = ['order__id', 'product__name', 'description']
    ordering_fields = ['requested_at', 'completed_at', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Optimizar queryset con select_related"""
        return Repair.objects.select_related(
            'order',
            'order__user',
            'product',
            'product__category',
            'warranty'
        ).all()
    
    def get_permissions(self):
        """Clientes pueden crear, managers pueden gestionar"""
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy', 'update_status']:
            permission_classes = [IsAuthenticated, IsAdminOrManager]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminOrManager])
    def update_status(self, request, pk=None):
        """Actualizar el estado de una reparación"""
        repair = self.get_object()
        new_status = request.data.get('status')
        technician_notes = request.data.get('technician_notes', '')
        final_cost = request.data.get('final_cost')
        
        if not new_status:
            return Response(
                {'error': 'Debe proporcionar un estado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in dict(Repair.RepairStatus.choices):
            return Response(
                {'error': f'Estado inválido: {new_status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        repair.status = new_status
        if technician_notes:
            repair.technician_notes = technician_notes
        if final_cost is not None:
            repair.final_cost = final_cost
        
        if new_status == Repair.RepairStatus.COMPLETED:
            repair.completed_at = timezone.now()
        
        repair.save()
        
        serializer = self.get_serializer(repair)
        return Response(serializer.data)
