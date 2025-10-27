from django.urls import path
from .views import (
    SalesReportView, 
    ProductsReportView, 
    DynamicReportParserView, 
    OrderInvoiceView,
    SalesReportPreviewView,
    ProductsReportPreviewView,
    DynamicReportPreviewView
)

urlpatterns = [
    # Endpoints de descarga directa (PDF/Excel)
    path('sales/', SalesReportView.as_view(), name='sales-report'),
    path('products/', ProductsReportView.as_view(), name='products-report'),
    # Endpoint inteligente para comandos en lenguaje natural
    path('dynamic-parser/', DynamicReportParserView.as_view(), name='dynamic-report-parser'),
    # Endpoint para generar comprobante de orden individual
    path('orders/<int:order_id>/invoice/', OrderInvoiceView.as_view(), name='order-invoice'),
    
    # Endpoints de previsualización (retornan JSON)
    path('sales/preview/', SalesReportPreviewView.as_view(), name='sales-report-preview'),
    path('products/preview/', ProductsReportPreviewView.as_view(), name='products-report-preview'),
    path('dynamic-parser/preview/', DynamicReportPreviewView.as_view(), name='dynamic-report-preview'),
]
