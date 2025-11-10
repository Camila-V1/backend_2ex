"""
Servicio para gestionar reembolsos con Stripe.
"""

import stripe
from django.conf import settings
from decimal import Decimal
from django.utils import timezone

# Configurar Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeRefundService:
    """
    Servicio centralizado para gestionar reembolsos de Stripe.
    """
    
    @staticmethod
    def create_refund(payment_intent_id, amount, reason=None, metadata=None):
        """
        Crear un reembolso en Stripe.
        
        Args:
            payment_intent_id (str): ID del Payment Intent a reembolsar
            amount (Decimal): Monto a reembolsar (en la moneda original)
            reason (str): Razón del reembolso
            metadata (dict): Metadata adicional
        
        Returns:
            dict: Información del reembolso creado
        
        Raises:
            stripe.error.StripeError: Si hay un error en Stripe
        """
        try:
            # Convertir amount a centavos (Stripe trabaja en centavos)
            amount_cents = int(float(amount) * 100)
            
            refund_data = {
                'payment_intent': payment_intent_id,
                'amount': amount_cents,
            }
            
            if reason:
                # Stripe acepta: 'duplicate', 'fraudulent', 'requested_by_customer'
                if reason.lower() in ['duplicate', 'fraudulent', 'requested_by_customer']:
                    refund_data['reason'] = reason.lower()
                else:
                    refund_data['reason'] = 'requested_by_customer'
                    if metadata is None:
                        metadata = {}
                    metadata['custom_reason'] = reason
            
            if metadata:
                refund_data['metadata'] = metadata
            
            # Crear reembolso en Stripe
            refund = stripe.Refund.create(**refund_data)
            
            return {
                'success': True,
                'refund_id': refund.id,
                'amount': Decimal(refund.amount) / 100,  # Convertir de centavos a dólares
                'status': refund.status,
                'charge_id': refund.charge,
                'currency': refund.currency,
                'created': refund.created,
                'reason': refund.reason,
                'metadata': refund.metadata
            }
            
        except stripe.error.InvalidRequestError as e:
            # Petición inválida (ej: payment_intent no existe)
            return {
                'success': False,
                'error': 'invalid_request',
                'message': str(e),
                'details': e.user_message
            }
        
        except stripe.error.CardError as e:
            # Error con la tarjeta
            return {
                'success': False,
                'error': 'card_error',
                'message': str(e),
                'details': e.user_message
            }
        
        except stripe.error.AuthenticationError as e:
            # Error de autenticación con Stripe
            return {
                'success': False,
                'error': 'authentication_error',
                'message': 'Error de autenticación con Stripe',
                'details': str(e)
            }
        
        except stripe.error.StripeError as e:
            # Error general de Stripe
            return {
                'success': False,
                'error': 'stripe_error',
                'message': 'Error al procesar reembolso',
                'details': str(e)
            }
        
        except Exception as e:
            # Error inesperado
            return {
                'success': False,
                'error': 'unexpected_error',
                'message': 'Error inesperado al procesar reembolso',
                'details': str(e)
            }
    
    @staticmethod
    def retrieve_refund(refund_id):
        """
        Obtener información de un reembolso existente.
        
        Args:
            refund_id (str): ID del reembolso en Stripe
        
        Returns:
            dict: Información del reembolso
        """
        try:
            refund = stripe.Refund.retrieve(refund_id)
            
            return {
                'success': True,
                'refund_id': refund.id,
                'amount': Decimal(refund.amount) / 100,
                'status': refund.status,
                'charge_id': refund.charge,
                'payment_intent': refund.payment_intent,
                'currency': refund.currency,
                'created': refund.created,
                'reason': refund.reason
            }
        
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': 'stripe_error',
                'message': str(e)
            }
    
    @staticmethod
    def cancel_refund(refund_id):
        """
        Cancelar un reembolso pendiente (solo si aún no fue procesado).
        
        Args:
            refund_id (str): ID del reembolso a cancelar
        
        Returns:
            dict: Resultado de la operación
        """
        try:
            refund = stripe.Refund.cancel(refund_id)
            
            return {
                'success': True,
                'refund_id': refund.id,
                'status': refund.status
            }
        
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': 'stripe_error',
                'message': str(e)
            }
    
    @staticmethod
    def list_refunds(payment_intent_id=None, charge_id=None, limit=10):
        """
        Listar reembolsos de un payment intent o charge.
        
        Args:
            payment_intent_id (str): ID del payment intent
            charge_id (str): ID del charge
            limit (int): Número máximo de resultados
        
        Returns:
            dict: Lista de reembolsos
        """
        try:
            filters = {'limit': limit}
            
            if payment_intent_id:
                filters['payment_intent'] = payment_intent_id
            elif charge_id:
                filters['charge'] = charge_id
            
            refunds = stripe.Refund.list(**filters)
            
            return {
                'success': True,
                'refunds': [
                    {
                        'refund_id': r.id,
                        'amount': Decimal(r.amount) / 100,
                        'status': r.status,
                        'created': r.created,
                        'reason': r.reason
                    }
                    for r in refunds.data
                ],
                'has_more': refunds.has_more
            }
        
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': 'stripe_error',
                'message': str(e)
            }


class RefundStatusMapper:
    """
    Mapear estados de Stripe a estados del modelo Refund.
    """
    
    STRIPE_TO_MODEL = {
        'pending': 'PENDING',
        'requires_action': 'PROCESSING',
        'succeeded': 'SUCCEEDED',
        'failed': 'FAILED',
        'canceled': 'CANCELLED',
    }
    
    @classmethod
    def map_status(cls, stripe_status):
        """Convertir estado de Stripe a estado del modelo"""
        return cls.STRIPE_TO_MODEL.get(stripe_status, 'PENDING')


def process_return_refund_to_stripe(return_obj, manager_user):
    """
    Procesar reembolso de devolución usando Stripe.
    
    Args:
        return_obj: Objeto Return (devolución)
        manager_user: Usuario manager que aprueba
    
    Returns:
        tuple: (success: bool, message: str, refund_data: dict)
    """
    from shop_orders.payment_models import Payment, Refund
    
    try:
        # Obtener información del pago original
        try:
            payment = Payment.objects.get(order=return_obj.order)
        except Payment.DoesNotExist:
            return (
                False,
                "No se encontró información de pago para esta orden. "
                "No se puede reembolsar al método original.",
                None
            )
        
        # Validar que el pago esté completado
        if payment.status != Payment.PaymentStatus.COMPLETED:
            return (
                False,
                f"El pago está en estado {payment.status}, no se puede reembolsar.",
                None
            )
        
        # Crear reembolso en Stripe
        refund_result = StripeRefundService.create_refund(
            payment_intent_id=payment.stripe_payment_intent_id,
            amount=return_obj.refund_amount,
            reason="requested_by_customer",
            metadata={
                'return_id': return_obj.id,
                'order_id': return_obj.order.id,
                'product_id': return_obj.product.id,
                'customer_id': return_obj.user.id,
                'approved_by': manager_user.id
            }
        )
        
        if not refund_result['success']:
            return (
                False,
                f"Error al procesar reembolso en Stripe: {refund_result.get('message', 'Error desconocido')}",
                refund_result
            )
        
        # Guardar información del reembolso en la BD
        refund_record = Refund.objects.create(
            payment=payment,
            return_obj=return_obj,
            stripe_refund_id=refund_result['refund_id'],
            amount=refund_result['amount'],
            currency=refund_result['currency'],
            reason=return_obj.reason,
            status=RefundStatusMapper.map_status(refund_result['status']),
            initiated_by=manager_user
        )
        
        # Actualizar estado del pago si es reembolso total
        if refund_result['amount'] >= payment.amount:
            payment.status = Payment.PaymentStatus.REFUNDED
        else:
            payment.status = Payment.PaymentStatus.PARTIALLY_REFUNDED
        payment.save()
        
        # Marcar como procesado si el reembolso fue exitoso
        if refund_result['status'] == 'succeeded':
            refund_record.status = 'SUCCEEDED'
            refund_record.processed_at = timezone.now()
            refund_record.save()
        
        return (
            True,
            f"Reembolso de ${refund_result['amount']} procesado exitosamente en Stripe. "
            f"El dinero será devuelto a la tarjeta del cliente en 5-10 días hábiles.",
            {
                'refund_id': refund_result['refund_id'],
                'amount': refund_result['amount'],
                'status': refund_result['status'],
                'stripe_refund_id': refund_record.stripe_refund_id
            }
        )
    
    except Exception as e:
        return (
            False,
            f"Error inesperado al procesar reembolso: {str(e)}",
            None
        )
