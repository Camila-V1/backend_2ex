from rest_framework import serializers


class PredictionItemSerializer(serializers.Serializer):
    """Serializer para un item de predicción individual"""
    date = serializers.DateField(help_text="Fecha de la predicción")
    predicted_sales = serializers.FloatField(help_text="Cantidad de unidades predichas")
    day_of_week = serializers.CharField(help_text="Día de la semana")


class ModelInfoSerializer(serializers.Serializer):
    """Serializer para información del modelo ML"""
    trained = serializers.BooleanField()
    model_path = serializers.CharField()
    prediction_period = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class SalesPredictionResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de predicciones de ventas"""
    predictions = PredictionItemSerializer(many=True)
    model_info = ModelInfoSerializer()
