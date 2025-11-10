# shop_orders/payment_admin.py

from django.contrib import admin
from .payment_models import Payment, Refund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin para gestionar pagos"""
    list_display = [
        'id',
        'order',
        'amount',
        'currency',
        'status',
        'stripe_payment_intent_id',
        'payment_method_type',
        'last4',
        'created_at',
        'completed_at'
    ]
    list_filter = ['status', 'currency', 'payment_method_type', 'created_at']
    search_fields = [
        'order__id',
        'stripe_payment_intent_id',
        'stripe_charge_id',
        'customer_email',
        'order__user__username',
        'order__user__email'
    ]
    readonly_fields = [
        'stripe_payment_intent_id',
        'stripe_charge_id',
        'created_at',
        'completed_at'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('order', 'amount', 'currency', 'status')
        }),
        ('Stripe', {
            'fields': (
                'stripe_payment_intent_id',
                'stripe_charge_id',
                'payment_method_type',
                'last4'
            )
        }),
        ('Cliente', {
            'fields': ('customer_email',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        }),
    )


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """Admin para gestionar reembolsos"""
    list_display = [
        'id',
        'payment',
        'return_obj',
        'amount',
        'currency',
        'status',
        'stripe_refund_id',
        'initiated_by',
        'created_at',
        'processed_at'
    ]
    list_filter = ['status', 'currency', 'created_at']
    search_fields = [
        'stripe_refund_id',
        'payment__order__id',
        'payment__stripe_payment_intent_id',
        'return_obj__id',
        'initiated_by__username'
    ]
    readonly_fields = [
        'stripe_refund_id',
        'payment',
        'return_obj',
        'created_at',
        'processed_at'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('payment', 'return_obj', 'amount', 'currency', 'status')
        }),
        ('Stripe', {
            'fields': ('stripe_refund_id',)
        }),
        ('Detalles', {
            'fields': ('reason', 'initiated_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'processed_at')
        }),
    )
    
    def has_add_permission(self, request):
        """No permitir crear reembolsos manualmente desde admin"""
        return False
