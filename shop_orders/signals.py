"""
Signals para invalidar cache automáticamente cuando cambian los datos.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Order


@receiver([post_save, post_delete], sender=Order)
def invalidate_dashboard_cache(sender, instance, **kwargs):
    """
    Invalida el cache del dashboard cuando se crea/actualiza/elimina una orden.
    """
    cache_key = 'admin_dashboard_data'
    cache.delete(cache_key)
    # También podríamos invalidar otros caches relacionados
    cache.delete('sales_analytics_data')
