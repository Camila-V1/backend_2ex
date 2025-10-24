from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.http import HttpResponse, JsonResponse
from django.views import View
from datetime import datetime
import calendar
import re
from .services import (
    generate_sales_report_pdf, 
    generate_sales_report_excel, 
    generate_products_report_pdf, 
    generate_products_report_excel,
    generate_invoice_pdf
)
from shop_orders.models import Order
import logging

logger = logging.getLogger(__name__)


class SalesReportView(View):
    """Vista simple de Django (no DRF) para evitar problemas con content negotiation"""

    def get(self, request, *args, **kwargs):
        logger.info(f"🔵 SalesReportView - GET request recibida")
        logger.info(f"🔵 User: {request.user}")
        logger.info(f"🔵 Query params: {request.GET}")
        # Obtener parámetros de la URL
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        report_format = request.GET.get('format', 'pdf').lower()
        
        logger.info(f"🔵 start_date: {start_date_str}, end_date: {end_date_str}, format: {report_format}")

        if not start_date_str or not end_date_str:
            logger.warning(f"⚠️ Faltan parámetros de fecha")
            return JsonResponse(
                {"error": "Los parámetros 'start_date' y 'end_date' son requeridos (YYYY-MM-DD)."},
                status=400
            )

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            logger.info(f"✅ Fechas parseadas correctamente: {start_date} a {end_date}")
        except ValueError:
            logger.error(f"❌ Error al parsear fechas")
            return JsonResponse(
                {"error": "Formato de fecha inválido. Use YYYY-MM-DD."},
                status=400
            )

        if report_format == 'pdf':
            logger.info(f"📄 Generando reporte PDF...")
            buffer = generate_sales_report_pdf(start_date, end_date)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="reporte_ventas_{start_date}_a_{end_date}.pdf"'
            logger.info(f"✅ PDF generado exitosamente")
            return response

        elif report_format == 'excel':
            logger.info(f"📊 Generando reporte Excel...")
            buffer = generate_sales_report_excel(start_date, end_date)
            response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="reporte_ventas_{start_date}_a_{end_date}.xlsx"'
            logger.info(f"✅ Excel generado exitosamente")
            return response
        
        else:
            logger.warning(f"⚠️ Formato no soportado: {report_format}")
            return JsonResponse(
                {"error": "Formato no soportado. Use 'pdf' o 'excel'."},
                status=400
            )


class ProductsReportView(View):
    """Vista simple de Django (no DRF) para evitar problemas con content negotiation"""

    def get(self, request, *args, **kwargs):
        logger.info(f"🟢 ProductsReportView - GET request recibida")
        logger.info(f"🟢 User: {request.user}")
        logger.info(f"🟢 Query params: {request.GET}")
        
        # Obtener formato del reporte
        report_format = request.GET.get('format', 'pdf').lower()
        logger.info(f"🟢 format: {report_format}")

        if report_format == 'pdf':
            logger.info(f"📄 Generando reporte de productos PDF...")
            buffer = generate_products_report_pdf()
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="reporte_productos.pdf"'
            logger.info(f"✅ PDF de productos generado exitosamente")
            return response

        elif report_format == 'excel':
            logger.info(f"📊 Generando reporte de productos Excel...")
            buffer = generate_products_report_excel()
            response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="reporte_productos.xlsx"'
            logger.info(f"✅ Excel de productos generado exitosamente")
            return response
        
        else:
            logger.warning(f"⚠️ Formato no soportado: {report_format}")
            return JsonResponse(
                {"error": "Formato no soportado. Use 'pdf' o 'excel'."},
                status=400
            )


class DynamicReportParserView(APIView):
    """
    Vista inteligente que interpreta comandos en lenguaje natural para generar reportes.
    
    Ejemplos de comandos:
    - "Quiero un reporte de ventas del mes de octubre en PDF"
    - "Dame el reporte de ventas de septiembre en excel"
    - "Genera un reporte de productos en PDF"
    - "Reporte de ventas del 01/10/2025 al 31/10/2025 en excel"
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        prompt = request.data.get('prompt', '').lower()
        
        logger.info(f"🤖 DynamicReportParserView - Prompt recibido: {prompt}")

        if not prompt:
            return Response(
                {"error": "El prompt no puede estar vacío."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Determinar el TIPO de reporte (ventas o productos)
        report_type = 'ventas'  # Por defecto
        if 'producto' in prompt or 'inventario' in prompt or 'stock' in prompt:
            report_type = 'productos'
            logger.info(f"📦 Tipo de reporte detectado: PRODUCTOS")
        else:
            logger.info(f"💰 Tipo de reporte detectado: VENTAS")

        # 2. Extraer el FORMATO (pdf o excel)
        report_format = 'pdf'  # Por defecto
        if 'excel' in prompt or 'xlsx' in prompt or 'hoja de cálculo' in prompt:
            report_format = 'excel'
        logger.info(f"📄 Formato detectado: {report_format.upper()}")

        # 3. Para reportes de PRODUCTOS (no requieren fechas)
        if report_type == 'productos':
            logger.info(f"🔧 Generando reporte de productos...")
            try:
                if report_format == 'pdf':
                    buffer = generate_products_report_pdf()
                    response = HttpResponse(buffer, content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="reporte_productos.pdf"'
                    logger.info(f"✅ Reporte de productos PDF generado")
                    return response
                else:
                    buffer = generate_products_report_excel()
                    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = 'attachment; filename="reporte_productos.xlsx"'
                    logger.info(f"✅ Reporte de productos Excel generado")
                    return response
            except Exception as e:
                logger.error(f"❌ Error al generar reporte de productos: {str(e)}")
                return Response(
                    {"error": f"Error al generar el reporte: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # 4. Para reportes de VENTAS (requieren fechas)
        start_date, end_date = None, None
        current_year = datetime.now().year

        # 4.1. Intentar extraer fechas específicas con regex (DD/MM/YYYY o YYYY-MM-DD)
        # Patrón: "del 01/10/2025 al 31/10/2025" o "del 2025-10-01 al 2025-10-31"
        date_range_pattern = r'del?\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}-\d{2}-\d{2})\s+al?\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}-\d{2}-\d{2})'
        match = re.search(date_range_pattern, prompt)
        
        if match:
            start_str, end_str = match.groups()
            logger.info(f"📅 Rango de fechas detectado: {start_str} al {end_str}")
            
            try:
                # Intentar varios formatos de fecha
                for date_format in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
                    try:
                        start_date = datetime.strptime(start_str, date_format).date()
                        end_date = datetime.strptime(end_str, date_format).date()
                        logger.info(f"✅ Fechas parseadas: {start_date} a {end_date}")
                        break
                    except ValueError:
                        continue
            except Exception as e:
                logger.error(f"❌ Error al parsear fechas específicas: {e}")

        # 4.2. Si no se encontraron fechas específicas, buscar nombre de mes
        if not start_date:
            meses = {
                "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
                "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
                "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
            }
            
            for nombre_mes, num_mes in meses.items():
                if nombre_mes in prompt:
                    logger.info(f"📅 Mes detectado: {nombre_mes.upper()} ({num_mes})")
                    
                    # Extraer año si está especificado
                    year_match = re.search(r'\b(20\d{2})\b', prompt)
                    if year_match:
                        current_year = int(year_match.group(1))
                        logger.info(f"📅 Año especificado: {current_year}")
                    
                    # Calcular primer y último día del mes
                    primer_dia = datetime(current_year, num_mes, 1).date()
                    ultimo_dia_num = calendar.monthrange(current_year, num_mes)[1]
                    ultimo_dia = datetime(current_year, num_mes, ultimo_dia_num).date()
                    
                    start_date, end_date = primer_dia, ultimo_dia
                    logger.info(f"✅ Rango calculado: {start_date} a {end_date}")
                    break

        # 4.3. Si aún no hay fechas, usar el mes actual
        if not start_date:
            logger.info(f"⚠️ No se detectó fecha específica, usando mes actual")
            today = datetime.now()
            primer_dia = datetime(today.year, today.month, 1).date()
            ultimo_dia_num = calendar.monthrange(today.year, today.month)[1]
            ultimo_dia = datetime(today.year, today.month, ultimo_dia_num).date()
            start_date, end_date = primer_dia, ultimo_dia
            logger.info(f"✅ Usando mes actual: {start_date} a {end_date}")

        # 5. Generar el reporte de ventas
        logger.info(f"🔧 Generando reporte de ventas desde {start_date} hasta {end_date} en {report_format}")
        
        try:
            if report_format == 'pdf':
                buffer = generate_sales_report_pdf(start_date, end_date)
                response = HttpResponse(buffer, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="reporte_ventas_{start_date}_a_{end_date}.pdf"'
                logger.info(f"✅ Reporte de ventas PDF generado exitosamente")
                return response
            else:
                buffer = generate_sales_report_excel(start_date, end_date)
                response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="reporte_ventas_{start_date}_a_{end_date}.xlsx"'
                logger.info(f"✅ Reporte de ventas Excel generado exitosamente")
                return response
        except Exception as e:
            logger.error(f"❌ Error al generar reporte de ventas: {str(e)}")
            return Response(
                {"error": f"Error al generar el reporte: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderInvoiceView(APIView):
    """
    Vista para generar el comprobante de venta (invoice/factura) de una orden individual.
    
    Permisos:
    - El usuario debe ser el dueño de la orden O ser administrador
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id, *args, **kwargs):
        logger.info(f"🧾 OrderInvoiceView - Generando invoice para orden #{order_id}")
        logger.info(f"👤 Usuario solicitante: {request.user.username}")
        
        try:
            # Buscamos la orden con prefetch de items y productos
            order = Order.objects.prefetch_related('items__product').get(id=order_id)
            logger.info(f"✅ Orden encontrada: #{order.id}, Usuario: {order.user.username}, Total: ${order.total_price}")

            # Verificamos permisos: debe ser el dueño de la orden o un admin
            if order.user != request.user and not request.user.is_staff:
                logger.warning(f"⛔ Acceso denegado: {request.user.username} no puede ver la orden #{order_id}")
                return Response(
                    {"error": "No tiene permiso para ver este comprobante."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            logger.info(f"✅ Permisos verificados, generando PDF...")
            
            # Generamos el PDF
            buffer = generate_invoice_pdf(order)
            
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="comprobante_orden_{order.id}.pdf"'
            
            logger.info(f"✅ Invoice generado exitosamente para orden #{order_id}")
            return response

        except Order.DoesNotExist:
            logger.error(f"❌ Orden #{order_id} no encontrada")
            return Response(
                {"error": "La orden especificada no existe."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"❌ Error al generar invoice: {str(e)}")
            return Response(
                {"error": f"Error al generar el comprobante: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
