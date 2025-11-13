# users/push_notification_service.py
"""
Servicio centralizado para enviar notificaciones push via Firebase Cloud Messaging (FCM)
"""

import os
import json
import logging
from typing import List, Dict, Optional
from django.conf import settings
from .device_token_models import DeviceToken, NotificationLog

logger = logging.getLogger(__name__)

# Firebase Admin SDK se inicializa en users/apps.py
try:
    import firebase_admin
    from firebase_admin import messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("firebase-admin no está instalado. Las notificaciones push no funcionarán.")


class PushNotificationService:
    """
    Servicio para enviar notificaciones push a usuarios
    """
    
    @staticmethod
    def _get_active_tokens(user) -> List[str]:
        """
        Obtiene todos los tokens FCM activos del usuario
        """
        tokens = DeviceToken.objects.filter(
            user=user,
            is_active=True
        ).values_list('token', flat=True)
        
        return list(tokens)
    
    @staticmethod
    def _create_notification_log(user, device_token, title, body, notification_type, data, status, error_msg=None, fcm_response=None):
        """Crea un registro de la notificación enviada"""
        try:
            NotificationLog.objects.create(
                user=user,
                device_token=device_token,
                title=title,
                body=body,
                notification_type=notification_type,
                data=data,
                status=status,
                error_message=error_msg,
                fcm_response=fcm_response or {}
            )
        except Exception as e:
            logger.error(f"Error al guardar NotificationLog: {e}")
    
    @staticmethod
    def send_notification(
        user,
        title: str,
        body: str,
        notification_type: str,
        data: Optional[Dict] = None
    ) -> Dict:
        """
        Envía una notificación push a todos los dispositivos activos del usuario
        
        Args:
            user: Usuario a quien enviar la notificación
            title: Título de la notificación
            body: Cuerpo del mensaje
            notification_type: Tipo de notificación (ORDER_DELIVERED, RETURN_APPROVED, etc.)
            data: Datos adicionales opcionales (diccionario)
        
        Returns:
            Dict con resultado: {'success': bool, 'sent_count': int, 'failed_count': int, 'errors': []}
        """
        
        if not FIREBASE_AVAILABLE:
            logger.error("Firebase Admin SDK no disponible")
            return {
                'success': False,
                'error': 'Firebase no está configurado',
                'sent_count': 0,
                'failed_count': 0
            }
        
        # Verificar que Firebase esté inicializado
        if not settings.FIREBASE_INITIALIZED:
            logger.error("Firebase no está inicializado. Verifica firebase_credentials.json")
            return {
                'success': False,
                'error': 'Firebase no inicializado',
                'sent_count': 0,
                'failed_count': 0
            }
        
        tokens = PushNotificationService._get_active_tokens(user)
        
        if not tokens:
            logger.warning(f"Usuario {user.username} no tiene tokens FCM registrados")
            return {
                'success': False,
                'error': 'No hay dispositivos registrados',
                'sent_count': 0,
                'failed_count': 0
            }
        
        # Preparar datos adicionales
        notification_data = data or {}
        notification_data['type'] = notification_type
        notification_data['click_action'] = 'FLUTTER_NOTIFICATION_CLICK'
        
        # Convertir todos los valores a strings (FCM requirement)
        notification_data = {k: str(v) for k, v in notification_data.items()}
        
        sent_count = 0
        failed_count = 0
        errors = []
        
        # Enviar a cada token
        for token in tokens:
            try:
                # Crear mensaje
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data=notification_data,
                    token=token,
                    android=messaging.AndroidConfig(
                        priority='high',
                        notification=messaging.AndroidNotification(
                            sound='default',
                            click_action='FLUTTER_NOTIFICATION_CLICK',
                        ),
                    ),
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                sound='default',
                                content_available=True,
                            ),
                        ),
                    ),
                )
                
                # Enviar mensaje
                response = messaging.send(message)
                
                logger.info(f"✅ Notificación enviada a {user.username}: {response}")
                
                # Buscar el DeviceToken
                device_token_obj = DeviceToken.objects.filter(token=token).first()
                
                # Crear log de éxito
                PushNotificationService._create_notification_log(
                    user=user,
                    device_token=device_token_obj,
                    title=title,
                    body=body,
                    notification_type=notification_type,
                    data=notification_data,
                    status='SENT',
                    fcm_response={'message_id': response}
                )
                
                sent_count += 1
                
            except messaging.UnregisteredError:
                # Token inválido - desactivar
                logger.warning(f"Token inválido para {user.username}, desactivando...")
                DeviceToken.objects.filter(token=token).update(is_active=False)
                failed_count += 1
                errors.append(f"Token inválido (desactivado)")
                
            except Exception as e:
                logger.error(f"❌ Error al enviar notificación a {user.username}: {e}")
                
                device_token_obj = DeviceToken.objects.filter(token=token).first()
                
                # Crear log de error
                PushNotificationService._create_notification_log(
                    user=user,
                    device_token=device_token_obj,
                    title=title,
                    body=body,
                    notification_type=notification_type,
                    data=notification_data,
                    status='FAILED',
                    error_msg=str(e)
                )
                
                failed_count += 1
                errors.append(str(e))
        
        return {
            'success': sent_count > 0,
            'sent_count': sent_count,
            'failed_count': failed_count,
            'errors': errors
        }
    
    # ============= NOTIFICACIONES ESPECÍFICAS DEL SISTEMA =============
    
    @staticmethod
    def send_order_delivered_notification(user, order):
        """
        Envía notificación cuando una orden ha sido entregada
        """
        title = "🎉 ¡Tu pedido ha llegado!"
        body = f"Tu orden #{order.id} ha sido entregada exitosamente. ¡Disfruta tu compra!"
        
        data = {
            'order_id': str(order.id),
            'order_total': str(order.total_price),
            'screen': 'OrderDetailScreen',  # Flutter navegará a esta pantalla
        }
        
        return PushNotificationService.send_notification(
            user=user,
            title=title,
            body=body,
            notification_type='ORDER_DELIVERED',
            data=data
        )
    
    @staticmethod
    def send_return_approved_notification(user, return_obj):
        """
        Envía notificación cuando un reembolso ha sido aprobado
        """
        title = "✅ Reembolso Aprobado"
        body = f"Tu solicitud de devolución para la orden #{return_obj.order.id} ha sido aprobada. El reembolso se procesará pronto."
        
        data = {
            'return_id': str(return_obj.id),
            'order_id': str(return_obj.order.id),
            'refund_amount': str(return_obj.order.total_price),
            'screen': 'ReturnsScreen',
        }
        
        return PushNotificationService.send_notification(
            user=user,
            title=title,
            body=body,
            notification_type='RETURN_APPROVED',
            data=data
        )
    
    @staticmethod
    def send_return_rejected_notification(user, return_obj):
        """
        Envía notificación cuando un reembolso ha sido rechazado
        """
        title = "❌ Reembolso Rechazado"
        body = f"Tu solicitud de devolución para la orden #{return_obj.order.id} ha sido rechazada."
        
        if return_obj.rejection_reason:
            body += f" Razón: {return_obj.rejection_reason}"
        
        data = {
            'return_id': str(return_obj.id),
            'order_id': str(return_obj.order.id),
            'screen': 'ReturnsScreen',
        }
        
        return PushNotificationService.send_notification(
            user=user,
            title=title,
            body=body,
            notification_type='RETURN_REJECTED',
            data=data
        )
    
    @staticmethod
    def send_order_status_update_notification(user, order, new_status):
        """
        Envía notificación cuando el estado de una orden cambia
        """
        
        status_messages = {
            'PENDING': ('⏳ Orden Pendiente', 'Tu orden está pendiente de pago'),
            'PAID': ('💳 Pago Confirmado', 'Tu orden ha sido pagada y será procesada pronto'),
            'SHIPPED': ('📦 Orden Enviada', 'Tu orden está en camino'),
            'DELIVERED': ('🎉 Orden Entregada', '¡Tu orden ha llegado!'),
            'CANCELLED': ('❌ Orden Cancelada', 'Tu orden ha sido cancelada'),
        }
        
        title, body_base = status_messages.get(new_status, ('📋 Actualización de Orden', 'El estado de tu orden ha cambiado'))
        body = f"{body_base} (Orden #{order.id})"
        
        data = {
            'order_id': str(order.id),
            'new_status': new_status,
            'screen': 'OrderDetailScreen',
        }
        
        return PushNotificationService.send_notification(
            user=user,
            title=title,
            body=body,
            notification_type=f'ORDER_STATUS_{new_status}',
            data=data
        )
