"""
Utilidades para envío de emails relacionados con devoluciones.

Este módulo centraliza el envío de notificaciones por email para:
- Nuevas solicitudes de devolución (a managers)
- Aprobación de devoluciones (a clientes)
- Rechazo de devoluciones (a clientes)
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def send_new_return_notification_to_managers(return_obj):
    """
    Enviar email a managers notificando nueva solicitud de devolución.
    
    Args:
        return_obj: Instancia del modelo Return
    """
    # Obtener todos los managers y admins
    managers = User.objects.filter(role__in=['MANAGER', 'ADMIN'])
    
    if not managers.exists():
        print("⚠️  No hay managers para notificar")
        return
    
    recipient_list = [manager.email for manager in managers if manager.email]
    
    if not recipient_list:
        print("⚠️  No hay managers con email válido")
        return
    
    # Asunto
    subject = f"🔔 Nueva Solicitud de Devolución #{return_obj.id}"
    
    # Mensaje texto plano
    message = f"""
Hola Manager,

Un cliente ha solicitado una devolución:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 DETALLES DE LA DEVOLUCIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Devolución ID: #{return_obj.id}
Cliente: {return_obj.user.get_full_name()} ({return_obj.user.email})
Orden: #{return_obj.order.id}
Producto: {return_obj.product.name}
Cantidad: {return_obj.quantity}
Precio: ${return_obj.product.price}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 MOTIVO DE LA DEVOLUCIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Razón: {return_obj.get_reason_display()}
Descripción del cliente:
{return_obj.description}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Por favor, revisa la solicitud y envíala a evaluación física cuando sea posible.

Puedes gestionar esta devolución en:
{settings.ALLOWED_HOSTS[0]}/admin/deliveries/return/{return_obj.id}/

Saludos,
Sistema SmartSales365
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        print(f"✅ Email enviado a {len(recipient_list)} manager(s)")
    except Exception as e:
        print(f"❌ Error enviando email: {str(e)}")


def send_return_approved_notification(return_obj):
    """
    Enviar email al cliente notificando que su devolución fue aprobada.
    
    Args:
        return_obj: Instancia del modelo Return
    """
    if not return_obj.user.email:
        print(f"⚠️  Cliente {return_obj.user.username} no tiene email")
        return
    
    # Asunto
    subject = f"✅ Tu Devolución #{return_obj.id} ha sido Aprobada"
    
    # Mensaje texto plano
    message = f"""
Hola {return_obj.user.first_name or return_obj.user.username},

¡Buenas noticias! Tu solicitud de devolución ha sido aprobada.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ DETALLES DE LA DEVOLUCIÓN APROBADA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Devolución ID: #{return_obj.id}
Orden: #{return_obj.order.id}
Producto: {return_obj.product.name}
Cantidad: {return_obj.quantity}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 INFORMACIÓN DEL REEMBOLSO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Monto a reembolsar: ${return_obj.refund_amount}
Método de reembolso: {return_obj.get_refund_method_display()}

{'El reembolso se procesará en las próximas 24-48 horas.' if return_obj.refund_method == 'WALLET' else 
 'El reembolso se verá reflejado en tu método de pago original en 5-10 días hábiles.' if return_obj.refund_method == 'ORIGINAL' else
 'El reembolso se transferirá a tu cuenta bancaria en 3-5 días hábiles.'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 NOTAS DE EVALUACIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{return_obj.evaluation_notes or 'Sin notas adicionales'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Podrás ver el estado de tu reembolso en tu cuenta en:
{settings.ALLOWED_HOSTS[0]}/mi-cuenta/billetera

Gracias por tu compra,
Equipo SmartSales365

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Si tienes dudas, contáctanos en: soporte@smartsales365.com
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[return_obj.user.email],
            fail_silently=False,
        )
        print(f"✅ Email de aprobación enviado a {return_obj.user.email}")
    except Exception as e:
        print(f"❌ Error enviando email: {str(e)}")


def send_return_rejected_notification(return_obj):
    """
    Enviar email al cliente notificando que su devolución fue rechazada.
    
    Args:
        return_obj: Instancia del modelo Return
    """
    if not return_obj.user.email:
        print(f"⚠️  Cliente {return_obj.user.username} no tiene email")
        return
    
    # Asunto
    subject = f"❌ Tu Solicitud de Devolución #{return_obj.id}"
    
    # Mensaje texto plano
    message = f"""
Hola {return_obj.user.first_name or return_obj.user.username},

Lamentamos informarte que tu solicitud de devolución ha sido rechazada.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 DETALLES DE LA SOLICITUD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Devolución ID: #{return_obj.id}
Orden: #{return_obj.order.id}
Producto: {return_obj.product.name}
Motivo de solicitud: {return_obj.get_reason_display()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ MOTIVO DEL RECHAZO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Evaluación del producto:
{return_obj.evaluation_notes or 'Sin evaluación detallada'}

Decisión del manager:
{return_obj.manager_notes or 'No se proporcionaron notas adicionales'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Entendemos que esta noticia puede ser decepcionante. Si crees que ha 
habido un error o tienes información adicional que no fue considerada, 
por favor contáctanos directamente.

Equipo de Atención al Cliente:
📧 Email: soporte@smartsales365.com
📞 Teléfono: +591 (2) 2234567
⏰ Horario: Lunes a Viernes, 8:00 - 18:00

Gracias por tu comprensión,
Equipo SmartSales365
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[return_obj.user.email],
            fail_silently=False,
        )
        print(f"✅ Email de rechazo enviado a {return_obj.user.email}")
    except Exception as e:
        print(f"❌ Error enviando email: {str(e)}")


def send_return_evaluation_started_notification(return_obj):
    """
    Enviar email al cliente notificando que su devolución está en evaluación.
    
    Args:
        return_obj: Instancia del modelo Return
    """
    if not return_obj.user.email:
        print(f"⚠️  Cliente {return_obj.user.username} no tiene email")
        return
    
    # Asunto
    subject = f"🔬 Tu Devolución #{return_obj.id} está en Evaluación"
    
    # Mensaje texto plano
    message = f"""
Hola {return_obj.user.first_name or return_obj.user.username},

Tu solicitud de devolución ha sido recibida y ahora está en proceso de evaluación.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔬 ESTADO: EN EVALUACIÓN FÍSICA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Devolución ID: #{return_obj.id}
Orden: #{return_obj.order.id}
Producto: {return_obj.product.name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 PRÓXIMOS PASOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. El producto será evaluado por un técnico especializado
2. Se verificará el estado físico y funcional
3. Recibirás una respuesta en las próximas 24-48 horas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Te notificaremos por email cuando la evaluación esté completa.

Saludos,
Equipo SmartSales365
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[return_obj.user.email],
            fail_silently=False,
        )
        print(f"✅ Email de evaluación enviado a {return_obj.user.email}")
    except Exception as e:
        print(f"❌ Error enviando email: {str(e)}")
