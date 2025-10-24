import joblib
import os
import pandas as pd
from datetime import date, timedelta
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .serializers import SalesPredictionResponseSerializer


class SalesPredictionView(APIView):
    """
    API endpoint para obtener predicciones de ventas futuras usando el modelo entrenado.
    
    Requiere que el modelo haya sido entrenado previamente con:
    python manage.py train_sales_model
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = SalesPredictionResponseSerializer

    def get(self, request, *args, **kwargs):
        model_path = os.path.join(settings.BASE_DIR, 'predictions', 'sales_model.joblib')

        # 1. Verificar si el modelo entrenado existe
        if not os.path.exists(model_path):
            return Response(
                {"error": "El modelo de predicción no ha sido entrenado. Ejecute 'python manage.py train_sales_model' primero."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Cargar el modelo
        try:
            model = joblib.load(model_path)
        except Exception as e:
            return Response(
                {"error": f"Error al cargar el modelo: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 3. Preparar los datos para la predicción (próximos 30 días)
        today = date.today()
        future_dates = [today + timedelta(days=i) for i in range(30)]
        
        # Asumimos predicciones generales con valores promedio
        # Para predicciones más precisas, estos valores podrían venir como parámetros
        future_data = {
            'year': [d.year for d in future_dates],
            'month': [d.month for d in future_dates],
            'day': [d.day for d in future_dates],
            'weekday': [d.weekday() for d in future_dates],
            'product_id': [1] * 30,  # Valor de ejemplo
            'category_id': [1] * 30, # Valor de ejemplo
            'price': [100.0] * 30    # Valor de ejemplo (precio promedio)
        }
        future_df = pd.DataFrame(future_data)

        # 4. Realizar la predicción
        try:
            predicted_quantities = model.predict(future_df)
        except Exception as e:
            return Response(
                {"error": f"Error al realizar la predicción: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 5. Formatear la respuesta
        response_data = []
        for i, d in enumerate(future_dates):
            response_data.append({
                "date": d.strftime('%Y-%m-%d'),
                "predicted_sales": round(float(predicted_quantities[i]), 2), # Cantidad de unidades predichas
                "day_of_week": d.strftime('%A')  # Día de la semana para análisis
            })
        
        return Response({
            "predictions": response_data,
            "model_info": {
                "trained": True,
                "model_path": model_path,
                "prediction_period": "30 days",
                "start_date": today.strftime('%Y-%m-%d'),
                "end_date": future_dates[-1].strftime('%Y-%m-%d')
            }
        }, status=status.HTTP_200_OK)
