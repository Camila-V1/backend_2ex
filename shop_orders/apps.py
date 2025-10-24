from django.apps import AppConfig


class ShopOrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop_orders'
    
    def ready(self):
        """Importa los signals cuando la app está lista."""
        import shop_orders.signals

