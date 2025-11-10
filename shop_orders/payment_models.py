"""
Modelos para gestionar información de pagos (Stripe)
"""

from django.db import models
from django.conf import settings
from shop_orders.models import Order


class Payment(models.Model):
    """
    Modelo para almacenar información de pagos procesados por Stripe.
    """
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        COMPLETED = 'COMPLETED', 'Completado'
        FAILED = 'FAILED', 'Fallido'
        REFUNDED = 'REFUNDED', 'Reembolsado'
        PARTIALLY_REFUNDED = 'PARTIALLY_REFUNDED', 'Parcialmente reembolsado'

    order = models.OneToOneField(
        Order, 
        on_delete=models.CASCADE, 
        related_name='payment'
    )
    
    # Stripe IDs
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="ID del payment intent de Stripe"
    )
    stripe_charge_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="ID del charge de Stripe"
    )
    
    # Información del pago
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Monto total pagado"
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text="Moneda del pago"
    )
    
    # Estado y timestamps
    status = models.CharField(
        max_length=25,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Información adicional
    customer_email = models.EmailField(blank=True, null=True)
    payment_method_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Tipo de método de pago (card, etc.)"
    )
    last4 = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        help_text="Últimos 4 dígitos de la tarjeta"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
    
    def __str__(self):
        return f"Pago {self.id} - Orden #{self.order.id} - ${self.amount}"


class Refund(models.Model):
    """
    Modelo para rastrear reembolsos realizados.
    """
    class RefundStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        PROCESSING = 'PROCESSING', 'Procesando'
        SUCCEEDED = 'SUCCEEDED', 'Exitoso'
        FAILED = 'FAILED', 'Fallido'
        CANCELLED = 'CANCELLED', 'Cancelado'

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='refunds'
    )
    return_obj = models.ForeignKey(
        'deliveries.Return',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stripe_refunds',
        help_text="Devolución asociada"
    )
    
    # Stripe IDs
    stripe_refund_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="ID del refund de Stripe"
    )
    
    # Información del reembolso
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Monto reembolsado"
    )
    currency = models.CharField(max_length=3, default='USD')
    reason = models.TextField(blank=True, null=True)
    
    # Estado y timestamps
    status = models.CharField(
        max_length=25,
        choices=RefundStatus.choices,
        default=RefundStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='initiated_refunds',
        help_text="Usuario que inició el reembolso"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Reembolso'
        verbose_name_plural = 'Reembolsos'
    
    def __str__(self):
        return f"Reembolso {self.id} - ${self.amount} - {self.status}"
