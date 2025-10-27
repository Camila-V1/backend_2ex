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
    generate_invoice_pdf,
    generate_dynamic_report_pdf,
    generate_dynamic_report_excel,
    build_dynamic_sales_query
)
from .serializers import (
    DynamicReportRequestSerializer,
    DynamicReportResponseSerializer,
    InvoiceResponseSerializer,
    SalesReportPreviewSerializer,
    ProductsReportPreviewSerializer,
    DynamicReportPreviewSerializer
)
from shop_orders.models import Order
from users.permissions import CanViewReports
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
    - "Reporte de ventas agrupado por producto del mes de octubre"
    - "Muestra las ventas con nombres de clientes del mes pasado"
    - "Dame un reporte de compras por cliente con sus nombres"
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = DynamicReportRequestSerializer

    def parse_prompt(self, prompt):
        """
        Parsea el prompt en lenguaje natural para extraer todas las instrucciones.
        
        Returns:
            dict con: report_type, format, start_date, end_date, group_by, 
                     show_customer_names, show_product_names, count_orders, sum_totals
        """
        prompt_lower = prompt.lower()
        parsed = {
            'report_type': 'ventas',
            'format': 'pdf',
            'group_by': None,
            'show_customer_names': False,
            'show_product_names': False,
            'count_orders': False,
            'sum_totals': False,
            'start_date': None,
            'end_date': None
        }
        
        # 1. Tipo de reporte
        if any(word in prompt_lower for word in ['producto', 'inventario', 'stock']):
            parsed['report_type'] = 'productos'
            logger.info(f"📦 Tipo de reporte: PRODUCTOS")
        else:
            logger.info(f"💰 Tipo de reporte: VENTAS")
        
        # 2. Formato
        if any(word in prompt_lower for word in ['excel', 'xlsx', 'hoja de cálculo', 'hoja de calculo']):
            parsed['format'] = 'excel'
        logger.info(f"📄 Formato: {parsed['format'].upper()}")
        
        # 3. Agrupación
        if any(phrase in prompt_lower for phrase in ['agrupado por producto', 'agrupar por producto', 'por producto']):
            parsed['group_by'] = 'product'
            logger.info(f"� Agrupación: Por PRODUCTO")
        elif any(phrase in prompt_lower for phrase in ['agrupado por cliente', 'agrupar por cliente', 'por cliente', 'compras por cliente']):
            parsed['group_by'] = 'customer'
            logger.info(f"📊 Agrupación: Por CLIENTE")
        
        # 4. Mostrar nombres de clientes
        if any(phrase in prompt_lower for phrase in ['nombre del cliente', 'nombres de clientes', 'con nombres', 'mostrar cliente']):
            parsed['show_customer_names'] = True
            logger.info(f"👤 Mostrar nombres de clientes: SÍ")
        
        # 5. Mostrar nombres de productos
        if any(phrase in prompt_lower for phrase in ['nombre del producto', 'nombres de productos', 'mostrar producto', 'detalle de producto']):
            parsed['show_product_names'] = True
            logger.info(f"📦 Mostrar nombres de productos: SÍ")
        
        # 6. Contar órdenes
        if any(phrase in prompt_lower for phrase in ['cantidad de compras', 'cuantas compras', 'número de órdenes', 'numero de ordenes', 'contar']):
            parsed['count_orders'] = True
            logger.info(f"🔢 Contar órdenes: SÍ")
        
        # 7. Sumar totales
        if any(phrase in prompt_lower for phrase in ['total', 'suma', 'monto']):
            parsed['sum_totals'] = True
            logger.info(f"💵 Sumar totales: SÍ")
        
        # 8. Extraer fechas
        current_year = datetime.now().year
        
        # 8.1 Fechas específicas
        date_range_pattern = r'del?\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}-\d{2}-\d{2})\s+al?\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}-\d{2}-\d{2})'
        match = re.search(date_range_pattern, prompt_lower)
        
        if match:
            start_str, end_str = match.groups()
            logger.info(f"📅 Rango de fechas detectado: {start_str} al {end_str}")
            
            for date_format in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
                try:
                    parsed['start_date'] = datetime.strptime(start_str, date_format).date()
                    parsed['end_date'] = datetime.strptime(end_str, date_format).date()
                    logger.info(f"✅ Fechas parseadas: {parsed['start_date']} a {parsed['end_date']}")
                    break
                except ValueError:
                    continue
        
        # 8.2 Nombres de meses
        if not parsed['start_date']:
            meses = {
                "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
                "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
                "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
            }
            
            for nombre_mes, num_mes in meses.items():
                if nombre_mes in prompt_lower:
                    logger.info(f"📅 Mes detectado: {nombre_mes.upper()} ({num_mes})")
                    
                    year_match = re.search(r'\b(20\d{2})\b', prompt_lower)
                    if year_match:
                        current_year = int(year_match.group(1))
                    
                    primer_dia = datetime(current_year, num_mes, 1).date()
                    ultimo_dia_num = calendar.monthrange(current_year, num_mes)[1]
                    ultimo_dia = datetime(current_year, num_mes, ultimo_dia_num).date()
                    
                    parsed['start_date'] = primer_dia
                    parsed['end_date'] = ultimo_dia
                    logger.info(f"✅ Rango calculado: {parsed['start_date']} a {parsed['end_date']}")
                    break
        
        # 8.3 Mes actual por defecto
        if not parsed['start_date']:
            logger.info(f"⚠️ No se detectó fecha, usando mes actual")
            today = datetime.now()
            primer_dia = datetime(today.year, today.month, 1).date()
            ultimo_dia_num = calendar.monthrange(today.year, today.month)[1]
            ultimo_dia = datetime(today.year, today.month, ultimo_dia_num).date()
            parsed['start_date'] = primer_dia
            parsed['end_date'] = ultimo_dia
        
        return parsed

    def post(self, request, *args, **kwargs):
        prompt = request.data.get('prompt', '')
        
        logger.info(f"🤖 DynamicReportParserView - Prompt recibido: {prompt}")

        if not prompt:
            return Response(
                {"error": "El prompt no puede estar vacío."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parsear el prompt completo
        parsed = self.parse_prompt(prompt)
        
        # Para reportes de PRODUCTOS (no requieren fechas ni agrupación)
        if parsed['report_type'] == 'productos':
            logger.info(f"🔧 Generando reporte de productos...")
            try:
                if parsed['format'] == 'pdf':
                    buffer = generate_products_report_pdf()
                    response = HttpResponse(buffer, content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="reporte_productos.pdf"'
                else:
                    buffer = generate_products_report_excel()
                    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = 'attachment; filename="reporte_productos.xlsx"'
                logger.info(f"✅ Reporte de productos generado")
                return response
            except Exception as e:
                logger.error(f"❌ Error: {str(e)}")
                return Response(
                    {"error": f"Error al generar el reporte: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Para reportes de VENTAS con consulta dinámica
        try:
            logger.info(f"🔧 Construyendo consulta dinámica SQL...")
            
            # Construir la consulta SQL dinámica
            queryset, headers, formatter = build_dynamic_sales_query(parsed)
            
            # Procesar los datos
            data = []
            for item in queryset:
                data.append(formatter(item))
            
            logger.info(f"✅ Consulta ejecutada: {len(data)} registros obtenidos")
            
            # Determinar título del reporte
            if parsed['group_by'] == 'product':
                title = f"Ventas por Producto ({parsed['start_date']} a {parsed['end_date']})"
            elif parsed['group_by'] == 'customer':
                title = f"Ventas por Cliente ({parsed['start_date']} a {parsed['end_date']})"
            else:
                title = f"Reporte de Ventas ({parsed['start_date']} a {parsed['end_date']})"
            
            # Generar el reporte en el formato solicitado
            if parsed['format'] == 'pdf':
                buffer = generate_dynamic_report_pdf(data, headers, title)
                response = HttpResponse(buffer, content_type='application/pdf')
                filename = f"reporte_ventas_{parsed['start_date']}_a_{parsed['end_date']}.pdf"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
            else:
                buffer = generate_dynamic_report_excel(data, headers, title)
                response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                filename = f"reporte_ventas_{parsed['start_date']}_a_{parsed['end_date']}.xlsx"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            logger.info(f"✅ Reporte dinámico generado exitosamente")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error al generar reporte dinámico: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
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
    serializer_class = InvoiceResponseSerializer

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


# ============================================================================
# VISTAS DE PREVISUALIZACIÓN (RETORNAN JSON PARA EL FRONTEND)
# ============================================================================

class SalesReportPreviewView(APIView):
    """
    Vista para previsualizar datos de ventas en JSON antes de descargar PDF/Excel.
    
    El frontend puede mostrar los datos en una tabla y luego el usuario
    decide si descargar en PDF o Excel usando el endpoint original.
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = SalesReportPreviewSerializer

    def get(self, request, *args, **kwargs):
        logger.info(f"👁️ SalesReportPreviewView - GET request recibida")
        
        # Obtener parámetros
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        
        if not start_date_str or not end_date_str:
            return Response(
                {"error": "Los parámetros 'start_date' y 'end_date' son requeridos (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener órdenes del rango de fechas
        orders = Order.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status='PAID'
        ).select_related('user').prefetch_related('items__product').order_by('-created_at')
        
        # Preparar datos
        orders_data = []
        total_revenue = 0
        
        for order in orders:
            order_info = {
                'order_id': order.id,
                'date': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'customer': order.user.get_full_name() or order.user.username,
                'customer_email': order.user.email,
                'total': float(order.total_price),
                'items_count': order.items.count(),
                'items': [
                    {
                        'product': item.product.name,
                        'quantity': item.quantity,
                        'price': float(item.price),
                        'subtotal': float(item.quantity * item.price)
                    }
                    for item in order.items.all()
                ]
            }
            orders_data.append(order_info)
            total_revenue += float(order.total_price)
        
        response_data = {
            'start_date': start_date,
            'end_date': end_date,
            'total_orders': orders.count(),
            'total_revenue': round(total_revenue, 2),
            'orders': orders_data
        }
        
        logger.info(f"✅ Preview generado: {orders.count()} órdenes, ${total_revenue:.2f}")
        return Response(response_data, status=status.HTTP_200_OK)


class ProductsReportPreviewView(APIView):
    """
    Vista para previsualizar datos de productos en JSON antes de descargar PDF/Excel.
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ProductsReportPreviewSerializer

    def get(self, request, *args, **kwargs):
        logger.info(f"👁️ ProductsReportPreviewView - GET request recibida")
        
        from products.models import Product
        
        # Obtener todos los productos activos
        products = Product.objects.filter(is_active=True).order_by('category__name', 'name')
        
        # Preparar datos
        products_data = []
        total_stock = 0
        total_value = 0
        
        for product in products:
            product_value = float(product.price * product.stock)
            product_info = {
                'id': product.id,
                'name': product.name,
                'category': product.category.name if product.category else 'Sin categoría',
                'price': float(product.price),
                'stock': product.stock,
                'value': round(product_value, 2),
                'description': product.description[:100] if product.description else ''
            }
            products_data.append(product_info)
            total_stock += product.stock
            total_value += product_value
        
        response_data = {
            'total_products': products.count(),
            'total_stock': total_stock,
            'total_value': round(total_value, 2),
            'products': products_data
        }
        
        logger.info(f"✅ Preview generado: {products.count()} productos")
        return Response(response_data, status=status.HTTP_200_OK)


class DynamicReportPreviewView(APIView):
    """
    Vista para previsualizar datos de reporte dinámico en JSON.
    
    Interpreta el comando en lenguaje natural y retorna los datos en JSON
    para que el frontend pueda mostrarlos antes de descargar.
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = DynamicReportPreviewSerializer

    def post(self, request, *args, **kwargs):
        prompt = request.data.get('prompt', '')
        
        logger.info(f"👁️ DynamicReportPreviewView - Prompt recibido: {prompt}")

        if not prompt:
            return Response(
                {"error": "El prompt no puede estar vacío."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Usar el mismo parser que la vista original
        from reports.views import DynamicReportParserView
        parser_view = DynamicReportParserView()
        parsed = parser_view.parse_prompt(prompt)
        
        # Para reportes de PRODUCTOS
        if parsed['report_type'] == 'productos':
            logger.info(f"📦 Generando preview de productos...")
            
            from products.models import Product
            products = Product.objects.filter(is_active=True).order_by('category__name', 'name')
            
            data = []
            headers = ['ID', 'Producto', 'Categoría', 'Precio', 'Stock', 'Valor Total']
            
            for product in products:
                data.append({
                    'ID': product.id,
                    'Producto': product.name,
                    'Categoría': product.category.name if product.category else 'Sin categoría',
                    'Precio': f"${product.price:.2f}",
                    'Stock': product.stock,
                    'Valor Total': f"${(product.price * product.stock):.2f}"
                })
            
            response_data = {
                'title': 'Reporte de Productos',
                'headers': headers,
                'data': data,
                'total_records': len(data)
            }
            
            logger.info(f"✅ Preview de productos generado: {len(data)} registros")
            return Response(response_data, status=status.HTTP_200_OK)

        # Para reportes de VENTAS con consulta dinámica
        try:
            logger.info(f"💰 Generando preview de ventas...")
            
            # Construir la consulta SQL dinámica (igual que en la vista original)
            queryset, headers, formatter = build_dynamic_sales_query(parsed)
            
            # Procesar los datos
            data = []
            for item in queryset:
                data.append(formatter(item))
            
            # Determinar título del reporte
            if parsed['group_by'] == 'product':
                title = f"Ventas por Producto ({parsed['start_date']} a {parsed['end_date']})"
            elif parsed['group_by'] == 'customer':
                title = f"Ventas por Cliente ({parsed['start_date']} a {parsed['end_date']})"
            else:
                title = f"Reporte de Ventas ({parsed['start_date']} a {parsed['end_date']})"
            
            response_data = {
                'title': title,
                'start_date': parsed['start_date'],
                'end_date': parsed['end_date'],
                'headers': headers,
                'data': data,
                'total_records': len(data)
            }
            
            logger.info(f"✅ Preview de ventas generado: {len(data)} registros")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"❌ Error al generar preview: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return Response(
                {"error": f"Error al generar el preview: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
