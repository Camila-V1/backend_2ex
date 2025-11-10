from django.apps import AppConfig


class DeliveriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'deliveries'
    verbose_name = 'Sistema de Entregas'
    
    def ready(self):
        """
        Importar signals cuando la app esté lista.
        Esto conecta automáticamente los signals de creación de deliveries y warranties.
        """
        import deliveries.signals
