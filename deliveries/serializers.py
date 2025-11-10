from rest_framework import serializers
from .models import DeliveryZone, DeliveryProfile, Delivery, Warranty, Return, Repair
from users.serializers import UserProfileSerializer
from shop_orders.serializers import OrderSerializer
from products.serializers import ProductSerializer


class DeliveryZoneSerializer(serializers.ModelSerializer):
    """Serializer para zonas de delivery"""
    
    class Meta:
        model = DeliveryZone
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class DeliveryProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfiles de repartidores"""
    user = UserProfileSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    
    class Meta:
        model = DeliveryProfile
        fields = [
            'id', 'user', 'user_id', 'zone', 'zone_name', 
            'status', 'vehicle_type', 'license_plate', 'phone',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_status(self, value):
        """Validar que el estado sea válido"""
        if value not in dict(DeliveryProfile.DeliveryStatus.choices):
            raise serializers.ValidationError(f"Estado inválido: {value}")
        return value


class DeliveryProfileSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas de repartidores"""
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    
    class Meta:
        model = DeliveryProfile
        fields = ['id', 'full_name', 'zone_name', 'status', 'vehicle_type', 'phone']


class DeliverySerializer(serializers.ModelSerializer):
    """Serializer para entregas"""
    delivery_person_details = DeliveryProfileSimpleSerializer(source='delivery_person', read_only=True)
    delivery_person_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    order_details = serializers.SerializerMethodField()
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Delivery
        fields = [
            'id', 'order', 'order_details', 'delivery_person', 'delivery_person_id',
            'delivery_person_details', 'zone', 'zone_name', 'status', 'status_display',
            'delivery_address', 'customer_phone', 'notes',
            'assigned_at', 'picked_up_at', 'delivered_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'assigned_at', 'picked_up_at', 'delivered_at']
    
    def get_order_details(self, obj):
        """Obtener detalles básicos de la orden"""
        return {
            'id': obj.order.id,
            'customer_name': obj.order.user.get_full_name() if obj.order.user else 'N/A',
            'total_amount': str(obj.order.total_price),
            'status': obj.order.status
        }
    
    def validate_delivery_person_id(self, value):
        """Validar que el repartidor exista y esté disponible"""
        if value:
            try:
                profile = DeliveryProfile.objects.get(id=value)
                if profile.status == DeliveryProfile.DeliveryStatus.OFFLINE:
                    raise serializers.ValidationError("El repartidor está desconectado")
            except DeliveryProfile.DoesNotExist:
                raise serializers.ValidationError("Perfil de repartidor no encontrado")
        return value
    
    def validate_status(self, value):
        """Validar transiciones de estado válidas"""
        if self.instance:
            current_status = self.instance.status
            valid_transitions = {
                Delivery.DeliveryStatus.PENDING: [Delivery.DeliveryStatus.ASSIGNED, Delivery.DeliveryStatus.FAILED],
                Delivery.DeliveryStatus.ASSIGNED: [Delivery.DeliveryStatus.PICKED_UP, Delivery.DeliveryStatus.FAILED],
                Delivery.DeliveryStatus.PICKED_UP: [Delivery.DeliveryStatus.IN_TRANSIT, Delivery.DeliveryStatus.FAILED],
                Delivery.DeliveryStatus.IN_TRANSIT: [Delivery.DeliveryStatus.DELIVERED, Delivery.DeliveryStatus.FAILED],
            }
            
            if current_status in valid_transitions and value not in valid_transitions[current_status]:
                raise serializers.ValidationError(
                    f"No se puede cambiar de {current_status} a {value}"
                )
        
        return value


class WarrantySerializer(serializers.ModelSerializer):
    """Serializer para garantías"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Warranty
        fields = [
            'id', 'order', 'order_id', 'product', 'product_name',
            'start_date', 'end_date', 'status', 'status_display',
            'terms', 'notes', 'is_expired',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_is_expired(self, obj):
        """Verificar si la garantía está vencida"""
        from django.utils import timezone
        return obj.end_date < timezone.now().date() if obj.end_date else False
    
    def validate(self, data):
        """Validar fechas de garantía"""
        if data.get('start_date') and data.get('end_date'):
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError(
                    "La fecha de fin debe ser posterior a la fecha de inicio"
                )
        return data


class ReturnSerializer(serializers.ModelSerializer):
    """Serializer simplificado para devoluciones"""
    # Campos read-only para mostrar información relacionada
    product_details = serializers.SerializerMethodField()
    order_details = serializers.SerializerMethodField()
    customer_details = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    refund_method_display = serializers.CharField(source='get_refund_method_display', read_only=True)
    
    # Campos write-only para crear devoluciones
    order_id = serializers.IntegerField(write_only=True, required=True)
    product_id = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = Return
        fields = [
            # IDs para crear/editar
            'id', 'order_id', 'product_id',
            
            # Información básica
            'order', 'product', 'user', 'quantity', 'reason', 'reason_display', 
            'description', 'status', 'status_display',
            
            # Detalles relacionados (read-only)
            'product_details', 'order_details', 'customer_details',
            
            # Evaluación y notas
            'evaluation_notes', 'manager_notes',
            
            # Reembolso
            'refund_amount', 'refund_method', 'refund_method_display',
            
            # Timestamps
            'requested_at', 'evaluated_at', 'processed_at', 'completed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order', 'product', 'user', 
            'requested_at', 'evaluated_at', 'processed_at', 'completed_at',
            'created_at', 'updated_at'
        ]
    
    def get_product_details(self, obj):
        """Información del producto"""
        return {
            'id': obj.product.id,
            'name': obj.product.name,
            'price': str(obj.product.price),
            'category': obj.product.category.name if obj.product.category else None
        }
    
    def get_order_details(self, obj):
        """Información de la orden"""
        return {
            'id': obj.order.id,
            'order_number': f"#{obj.order.id}",
            'order_date': obj.order.created_at.isoformat(),
            'total_price': str(obj.order.total_price),
            'status': obj.order.status
        }
    
    def get_customer_details(self, obj):
        """Información del cliente"""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'full_name': obj.user.get_full_name()
        }
    
    def validate_quantity(self, value):
        """Validar que la cantidad sea positiva"""
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0")
        return value
    
    def validate_refund_amount(self, value):
        """Validar que el monto de reembolso sea válido"""
        if value and value < 0:
            raise serializers.ValidationError("El monto de reembolso no puede ser negativo")
        return value
    
    def validate(self, data):
        """Validaciones adicionales"""
        # Si se está creando una nueva devolución
        if not self.instance:
            order_id = data.get('order_id')
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)
            
            # Validar que la orden exista
            from shop_orders.models import Order
            try:
                order = Order.objects.get(id=order_id)
                data['order'] = order
            except Order.DoesNotExist:
                raise serializers.ValidationError({"order_id": "Orden no encontrada"})
            
            # Validar que el producto exista en la orden
            from products.models import Product
            try:
                product = Product.objects.get(id=product_id)
                data['product'] = product
            except Product.DoesNotExist:
                raise serializers.ValidationError({"product_id": "Producto no encontrado"})
            
            # Verificar que el producto esté en la orden
            order_item = order.items.filter(product=product).first()
            if not order_item:
                raise serializers.ValidationError({
                    "product_id": "Este producto no está en la orden especificada"
                })
            
            # Validar cantidad
            if quantity > order_item.quantity:
                raise serializers.ValidationError({
                    "quantity": f"Solo puedes devolver hasta {order_item.quantity} unidades"
                })
            
            # Validar que la orden esté entregada
            if order.status != 'DELIVERED':
                raise serializers.ValidationError({
                    "order_id": "Solo puedes devolver productos de órdenes entregadas"
                })
            
            # Establecer el usuario automáticamente
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                data['user'] = request.user
        
        return data
    
    def create(self, validated_data):
        """Crear devolución con valores iniciales"""
        # Remover campos write-only que ya fueron procesados
        validated_data.pop('order_id', None)
        validated_data.pop('product_id', None)
        
        # Establecer estado inicial
        validated_data['status'] = Return.ReturnStatus.REQUESTED
        
        # Crear la devolución
        from django.utils import timezone
        validated_data['requested_at'] = timezone.now()
        
        return super().create(validated_data)


class RepairSerializer(serializers.ModelSerializer):
    """Serializer para reparaciones"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    warranty_id = serializers.IntegerField(source='warranty.id', read_only=True, allow_null=True)
    customer_name = serializers.CharField(source='order.user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Repair
        fields = [
            'id', 'warranty', 'warranty_id', 'order', 'order_id',
            'product', 'product_name', 'customer_name',
            'description', 'status', 'status_display',
            'estimated_cost', 'final_cost', 'is_under_warranty',
            'technician_notes', 'requested_at', 'completed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'requested_at', 'completed_at']
    
    def validate_estimated_cost(self, value):
        """Validar que el costo estimado sea válido"""
        if value and value < 0:
            raise serializers.ValidationError("El costo estimado no puede ser negativo")
        return value
    
    def validate_final_cost(self, value):
        """Validar que el costo final sea válido"""
        if value and value < 0:
            raise serializers.ValidationError("El costo final no puede ser negativo")
        return value
    
    def validate(self, data):
        """Validar lógica de garantía"""
        is_under_warranty = data.get('is_under_warranty', False)
        warranty = data.get('warranty')
        
        if is_under_warranty and not warranty:
            raise serializers.ValidationError(
                "Si la reparación está bajo garantía, debe especificar la garantía"
            )
        
        return data
