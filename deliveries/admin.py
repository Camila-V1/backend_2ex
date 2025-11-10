from django.contrib import admin
from .models import DeliveryZone, DeliveryProfile, Delivery, Warranty, Return, Repair


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    """Administración de zonas de delivery"""
    list_display = ['id', 'name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DeliveryProfile)
class DeliveryProfileAdmin(admin.ModelAdmin):
    """Administración de perfiles de repartidores"""
    list_display = ['id', 'user', 'zone', 'status', 'vehicle_type', 'phone', 'created_at']
    list_filter = ['status', 'zone', 'vehicle_type', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone', 'license_plate']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información de Delivery', {
            'fields': ('zone', 'status', 'vehicle_type', 'license_plate', 'phone')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['mark_as_available', 'mark_as_busy', 'mark_as_offline']
    
    def mark_as_available(self, request, queryset):
        """Marcar repartidores como disponibles"""
        updated = queryset.update(status=DeliveryProfile.DeliveryStatus.AVAILABLE)
        self.message_user(request, f'{updated} repartidor(es) marcado(s) como disponible(s).')
    mark_as_available.short_description = 'Marcar como disponible'
    
    def mark_as_busy(self, request, queryset):
        """Marcar repartidores como ocupados"""
        updated = queryset.update(status=DeliveryProfile.DeliveryStatus.BUSY)
        self.message_user(request, f'{updated} repartidor(es) marcado(s) como ocupado(s).')
    mark_as_busy.short_description = 'Marcar como ocupado'
    
    def mark_as_offline(self, request, queryset):
        """Marcar repartidores como desconectados"""
        updated = queryset.update(status=DeliveryProfile.DeliveryStatus.OFFLINE)
        self.message_user(request, f'{updated} repartidor(es) marcado(s) como desconectado(s).')
    mark_as_offline.short_description = 'Marcar como desconectado'


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    """Administración de entregas"""
    list_display = [
        'id', 'order', 'delivery_person', 'zone', 'status', 
        'assigned_at', 'delivered_at', 'created_at'
    ]
    list_filter = ['status', 'zone', 'assigned_at', 'delivered_at', 'created_at']
    search_fields = [
        'order__id', 'delivery_address', 'customer_phone', 
        'delivery_person__user__username', 'notes'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Orden y Asignación', {
            'fields': ('order', 'delivery_person', 'zone')
        }),
        ('Información de Contacto', {
            'fields': ('delivery_address', 'customer_phone')
        }),
        ('Estado y Seguimiento', {
            'fields': ('status', 'notes', 'assigned_at', 'picked_up_at', 'delivered_at')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'assigned_at', 'picked_up_at', 'delivered_at']
    
    actions = ['mark_as_picked_up', 'mark_as_in_transit', 'mark_as_delivered']
    
    def mark_as_picked_up(self, request, queryset):
        """Marcar entregas como recogidas"""
        from django.utils import timezone
        updated = queryset.filter(status=Delivery.DeliveryStatus.ASSIGNED).update(
            status=Delivery.DeliveryStatus.PICKED_UP,
            picked_up_at=timezone.now()
        )
        self.message_user(request, f'{updated} entrega(s) marcada(s) como recogida(s).')
    mark_as_picked_up.short_description = 'Marcar como recogido'
    
    def mark_as_in_transit(self, request, queryset):
        """Marcar entregas como en tránsito"""
        updated = queryset.filter(status=Delivery.DeliveryStatus.PICKED_UP).update(
            status=Delivery.DeliveryStatus.IN_TRANSIT
        )
        self.message_user(request, f'{updated} entrega(s) marcada(s) como en tránsito.')
    mark_as_in_transit.short_description = 'Marcar como en tránsito'
    
    def mark_as_delivered(self, request, queryset):
        """Marcar entregas como entregadas"""
        from django.utils import timezone
        updated = queryset.filter(status=Delivery.DeliveryStatus.IN_TRANSIT).update(
            status=Delivery.DeliveryStatus.DELIVERED,
            delivered_at=timezone.now()
        )
        self.message_user(request, f'{updated} entrega(s) marcada(s) como entregada(s).')
    mark_as_delivered.short_description = 'Marcar como entregado'


@admin.register(Warranty)
class WarrantyAdmin(admin.ModelAdmin):
    """Administración de garantías"""
    list_display = ['id', 'order', 'product', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['status', 'start_date', 'end_date', 'created_at']
    search_fields = ['order__id', 'product__name', 'warranty_terms', 'notes']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información de Garantía', {
            'fields': ('order', 'product', 'start_date', 'end_date', 'status')
        }),
        ('Detalles', {
            'fields': ('warranty_terms', 'notes')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['mark_as_active', 'mark_as_expired', 'mark_as_void']
    
    def mark_as_active(self, request, queryset):
        """Marcar garantías como activas"""
        updated = queryset.update(status=Warranty.WarrantyStatus.ACTIVE)
        self.message_user(request, f'{updated} garantía(s) marcada(s) como activa(s).')
    mark_as_active.short_description = 'Marcar como activa'
    
    def mark_as_expired(self, request, queryset):
        """Marcar garantías como expiradas"""
        updated = queryset.update(status=Warranty.WarrantyStatus.EXPIRED)
        self.message_user(request, f'{updated} garantía(s) marcada(s) como expirada(s).')
    mark_as_expired.short_description = 'Marcar como expirada'
    
    def mark_as_void(self, request, queryset):
        """Anular garantías"""
        updated = queryset.update(status=Warranty.WarrantyStatus.VOID)
        self.message_user(request, f'{updated} garantía(s) anulada(s).')
    mark_as_void.short_description = 'Anular garantía'


@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    """Administración de devoluciones"""
    list_display = [
        'id', 'order', 'product', 'quantity', 'reason', 'status', 
        'refund_amount', 'requested_at', 'processed_at'
    ]
    list_filter = ['status', 'reason', 'requested_at', 'processed_at', 'created_at']
    search_fields = [
        'order__id', 'product__name', 'description', 
        'manager_notes', 'order__customer__username'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información de Devolución', {
            'fields': ('order', 'product', 'quantity', 'reason', 'status')
        }),
        ('Detalles', {
            'fields': ('description', 'refund_amount', 'manager_notes')
        }),
        ('Fechas', {
            'fields': ('requested_at', 'processed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'requested_at', 'processed_at']
    
    actions = ['approve_returns', 'reject_returns', 'mark_as_in_transit', 'mark_as_completed']
    
    def approve_returns(self, request, queryset):
        """Aprobar devoluciones"""
        from django.utils import timezone
        updated = queryset.filter(status=Return.ReturnStatus.REQUESTED).update(
            status=Return.ReturnStatus.APPROVED,
            processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} devolución(es) aprobada(s).')
    approve_returns.short_description = 'Aprobar devoluciones'
    
    def reject_returns(self, request, queryset):
        """Rechazar devoluciones"""
        from django.utils import timezone
        updated = queryset.filter(status=Return.ReturnStatus.REQUESTED).update(
            status=Return.ReturnStatus.REJECTED,
            processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} devolución(es) rechazada(s).')
    reject_returns.short_description = 'Rechazar devoluciones'
    
    def mark_as_in_transit(self, request, queryset):
        """Marcar devoluciones como en tránsito"""
        updated = queryset.filter(status=Return.ReturnStatus.APPROVED).update(
            status=Return.ReturnStatus.IN_TRANSIT
        )
        self.message_user(request, f'{updated} devolución(es) marcada(s) como en tránsito.')
    mark_as_in_transit.short_description = 'Marcar como en tránsito'
    
    def mark_as_completed(self, request, queryset):
        """Marcar devoluciones como completadas"""
        updated = queryset.filter(status=Return.ReturnStatus.IN_TRANSIT).update(
            status=Return.ReturnStatus.COMPLETED
        )
        self.message_user(request, f'{updated} devolución(es) completada(s).')
    mark_as_completed.short_description = 'Marcar como completada'


@admin.register(Repair)
class RepairAdmin(admin.ModelAdmin):
    """Administración de reparaciones"""
    list_display = [
        'id', 'order', 'product', 'status', 'is_under_warranty', 
        'estimated_cost', 'final_cost', 'requested_at', 'completed_at'
    ]
    list_filter = ['status', 'is_under_warranty', 'requested_at', 'completed_at', 'created_at']
    search_fields = [
        'order__id', 'product__name', 'description', 
        'technician_notes', 'order__customer__username'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información de Reparación', {
            'fields': ('warranty', 'order', 'product', 'status', 'is_under_warranty')
        }),
        ('Descripción', {
            'fields': ('description', 'technician_notes')
        }),
        ('Costos', {
            'fields': ('estimated_cost', 'final_cost')
        }),
        ('Fechas', {
            'fields': ('requested_at', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'requested_at', 'completed_at']
    
    actions = ['mark_as_in_progress', 'mark_as_completed', 'mark_as_delivered']
    
    def mark_as_in_progress(self, request, queryset):
        """Marcar reparaciones como en progreso"""
        updated = queryset.filter(status=Repair.RepairStatus.REQUESTED).update(
            status=Repair.RepairStatus.IN_PROGRESS
        )
        self.message_user(request, f'{updated} reparación(es) marcada(s) como en progreso.')
    mark_as_in_progress.short_description = 'Marcar como en progreso'
    
    def mark_as_completed(self, request, queryset):
        """Marcar reparaciones como completadas"""
        from django.utils import timezone
        updated = queryset.filter(status=Repair.RepairStatus.IN_PROGRESS).update(
            status=Repair.RepairStatus.COMPLETED,
            completed_at=timezone.now()
        )
        self.message_user(request, f'{updated} reparación(es) completada(s).')
    mark_as_completed.short_description = 'Marcar como completada'
    
    def mark_as_delivered(self, request, queryset):
        """Marcar reparaciones como entregadas"""
        updated = queryset.filter(status=Repair.RepairStatus.COMPLETED).update(
            status=Repair.RepairStatus.DELIVERED
        )
        self.message_user(request, f'{updated} reparación(es) entregada(s).')
    mark_as_delivered.short_description = 'Marcar como entregada'
