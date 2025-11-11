"""
Views básicas para el proyecto ecommerce_api
"""
from django.http import JsonResponse


def health_check(request):
    """
    Endpoint de health check para servicios como Render, AWS, etc.
    Responde con 200 OK para indicar que el servicio está funcionando.
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'ecommerce_api',
        'message': 'Service is running'
    })
