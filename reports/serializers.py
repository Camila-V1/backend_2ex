from rest_framework import serializers


class DynamicReportRequestSerializer(serializers.Serializer):
    """Serializer para solicitud de reporte dinámico con lenguaje natural"""
    prompt = serializers.CharField(
        help_text="""Comando en lenguaje natural para generar reportes.
        
        Ejemplos:
        - "Quiero un reporte de ventas del mes de octubre en PDF"
        - "Dame el reporte de ventas de septiembre en excel"
        - "Genera un reporte de productos en PDF"
        - "Reporte de ventas del 01/10/2025 al 31/10/2025 en excel"
        - "Reporte de ventas agrupado por producto del mes de octubre"
        - "Muestra las ventas con nombres de clientes del mes pasado"
        """
    )


class DynamicReportResponseSerializer(serializers.Serializer):
    """Serializer para respuesta del parser de reportes (solo para documentación)"""
    report_type = serializers.CharField()
    format = serializers.CharField()
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    group_by = serializers.CharField(required=False)
    show_customer_names = serializers.BooleanField()
    show_product_names = serializers.BooleanField()


class InvoiceResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de factura PDF (solo para documentación)"""
    message = serializers.CharField(default="PDF generado")
    filename = serializers.CharField()


# ============================================================================
# SERIALIZERS PARA PREVISUALIZACIÓN DE REPORTES
# ============================================================================

class SalesReportPreviewSerializer(serializers.Serializer):
    """Serializer para previsualización de reporte de ventas"""
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    total_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    orders = serializers.ListField(
        child=serializers.DictField(),
        help_text="Lista de órdenes con detalles"
    )


class ProductsReportPreviewSerializer(serializers.Serializer):
    """Serializer para previsualización de reporte de productos"""
    total_products = serializers.IntegerField()
    total_stock = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    products = serializers.ListField(
        child=serializers.DictField(),
        help_text="Lista de productos con detalles"
    )


class DynamicReportPreviewSerializer(serializers.Serializer):
    """Serializer para previsualización de reporte dinámico"""
    title = serializers.CharField()
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    headers = serializers.ListField(
        child=serializers.CharField(),
        help_text="Encabezados de las columnas"
    )
    data = serializers.ListField(
        child=serializers.DictField(),
        help_text="Datos del reporte"
    )
    total_records = serializers.IntegerField()
