from django.urls import path
from .views import SalesPredictionView

urlpatterns = [
    path('predictions/sales/', SalesPredictionView.as_view(), name='sales-prediction'),
]
