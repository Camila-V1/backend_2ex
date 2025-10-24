from django.core.management.base import BaseCommand
from predictions.services import train_sales_prediction_model


class Command(BaseCommand):
    help = 'Entrena y guarda el modelo de predicción de ventas'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Iniciando el entrenamiento del modelo de predicción de ventas...'))
        
        result = train_sales_prediction_model()
        
        if "error" in result:
            self.stdout.write(self.style.ERROR(result["error"]))
        else:
            self.stdout.write(self.style.SUCCESS(f'¡Éxito! {result["status"]}'))
            self.stdout.write(f'  - Guardado en: {result["path"]}')
            self.stdout.write(f'  - MSE: {result["mse"]}')
            self.stdout.write(f'  - Muestras usadas: {result.get("n_samples")}')
