from django.urls import path
from .views import SalesReportView, ProductsReportView, DynamicReportParserView, OrderInvoiceView

urlpatterns = [
    path('sales/', SalesReportView.as_view(), name='sales-report'),
    path('products/', ProductsReportView.as_view(), name='products-report'),
    # Endpoint inteligente para comandos en lenguaje natural
    path('dynamic-parser/', DynamicReportParserView.as_view(), name='dynamic-report-parser'),
    # Endpoint para generar comprobante de orden individual
    path('orders/<int:order_id>/invoice/', OrderInvoiceView.as_view(), name='order-invoice'),
]
