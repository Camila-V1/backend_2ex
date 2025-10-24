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
