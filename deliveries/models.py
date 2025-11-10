from django.db import models
from django.conf import settings
from shop_orders.models import Order
from products.models import Product


class DeliveryZone(models.Model):
    """Zonas de entrega (Norte, Sur, Este, Oeste, Centro)"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Zona de Entrega'
        verbose_name_plural = 'Zonas de Entrega'


class DeliveryProfile(models.Model):
    """Perfil extendido para usuarios con rol DELIVERY"""
    
    class DeliveryStatus(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Disponible'
        BUSY = 'BUSY', 'Ocupado'
        OFFLINE = 'OFFLINE', 'Fuera de servicio'
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='delivery_profile'
    )
    zone = models.ForeignKey(
        DeliveryZone,
        on_delete=models.SET_NULL,
        null=True,
        related_name='deliveries'
    )
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.AVAILABLE
    )
    vehicle_type = models.CharField(max_length=50, blank=True)  # moto, auto, bicicleta
    license_plate = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.zone.name if self.zone else 'Sin zona'}"
    
    class Meta:
        verbose_name = 'Perfil de Delivery'
        verbose_name_plural = 'Perfiles de Delivery'


class Warranty(models.Model):
    """Garantías de productos"""
    
    class WarrantyStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Activa'
        CLAIMED = 'CLAIMED', 'Reclamada'
        EXPIRED = 'EXPIRED', 'Expirada'
        VOID = 'VOID', 'Anulada'
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='warranties')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=WarrantyStatus.choices,
        default=WarrantyStatus.ACTIVE
    )
    terms = models.TextField(help_text="Términos y condiciones de la garantía")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Garantía {self.id} - {self.product.name}"
    
    class Meta:
        verbose_name = 'Garantía'
        verbose_name_plural = 'Garantías'
        ordering = ['-start_date']


class Return(models.Model):
    """Devoluciones de productos"""
    
    class ReturnStatus(models.TextChoices):
        REQUESTED = 'REQUESTED', 'Solicitada'
        APPROVED = 'APPROVED', 'Aprobada'
        REJECTED = 'REJECTED', 'Rechazada'
        IN_TRANSIT = 'IN_TRANSIT', 'En tránsito'
        COMPLETED = 'COMPLETED', 'Completada'
    
    class ReturnReason(models.TextChoices):
        DEFECTIVE = 'DEFECTIVE', 'Producto defectuoso'
        WRONG_ITEM = 'WRONG_ITEM', 'Producto equivocado'
        NOT_AS_DESCRIBED = 'NOT_AS_DESCRIBED', 'No como se describe'
        CHANGED_MIND = 'CHANGED_MIND', 'Cambió de opinión'
        OTHER = 'OTHER', 'Otro'
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='returns')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    reason = models.CharField(max_length=20, choices=ReturnReason.choices)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=ReturnStatus.choices,
        default=ReturnStatus.REQUESTED
    )
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    manager_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Devolución {self.id} - {self.product.name}"
    
    class Meta:
        verbose_name = 'Devolución'
        verbose_name_plural = 'Devoluciones'
        ordering = ['-requested_at']


class Repair(models.Model):
    """Reparaciones de productos"""
    
    class RepairStatus(models.TextChoices):
        REQUESTED = 'REQUESTED', 'Solicitada'
        IN_PROGRESS = 'IN_PROGRESS', 'En progreso'
        COMPLETED = 'COMPLETED', 'Completada'
        DELIVERED = 'DELIVERED', 'Entregada'
        CANCELLED = 'CANCELLED', 'Cancelada'
    
    warranty = models.ForeignKey(
        Warranty,
        on_delete=models.CASCADE,
        related_name='repairs',
        null=True,
        blank=True
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='repairs')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    description = models.TextField(help_text="Descripción del problema")
    status = models.CharField(
        max_length=20,
        choices=RepairStatus.choices,
        default=RepairStatus.REQUESTED
    )
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_under_warranty = models.BooleanField(default=False)
    technician_notes = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Reparación {self.id} - {self.product.name}"
    
    class Meta:
        verbose_name = 'Reparación'
        verbose_name_plural = 'Reparaciones'
        ordering = ['-requested_at']


class Delivery(models.Model):
    """Tracking de entregas"""
    
    class DeliveryStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        ASSIGNED = 'ASSIGNED', 'Asignada'
        PICKED_UP = 'PICKED_UP', 'Recogida'
        IN_TRANSIT = 'IN_TRANSIT', 'En tránsito'
        DELIVERED = 'DELIVERED', 'Entregada'
        FAILED = 'FAILED', 'Fallida'
    
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='delivery'
    )
    delivery_person = models.ForeignKey(
        'DeliveryProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries_assigned'
    )
    zone = models.ForeignKey(
        DeliveryZone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING
    )
    delivery_address = models.TextField()
    customer_phone = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Entrega #{self.order.id} - {self.status}"
    
    class Meta:
        verbose_name = 'Entrega'
        verbose_name_plural = 'Entregas'
        ordering = ['-assigned_at']
