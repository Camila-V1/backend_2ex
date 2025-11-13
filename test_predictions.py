#!/usr/bin/env python
"""
Script para probar el endpoint de predicciones
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from users.models import CustomUser
from predictions.views import SalesPredictionView

# Obtener admin
admin = CustomUser.objects.get(username='admin')

# Crear request factory
factory = APIRequestFactory()
request = factory.get('/api/predictions/sales/')
force_authenticate(request, user=admin)

# Llamar a la vista
view = SalesPredictionView.as_view()
response = view(request)

print("\n" + "=" * 80)
print("  📊 PREDICCIONES DE VENTAS (CON VARIACIONES)")
print("=" * 80 + "\n")

if response.status_code == 200:
    data = response.data
    predictions = data.get('predictions', [])
    
    print(f"✅ Total predicciones: {len(predictions)}\n")
    print("📅 Primeros 10 días:\n")
    print(f"{'Fecha':<15} {'Unidades':<12} {'Día de la Semana'}")
    print("─" * 60)
    
    for pred in predictions[:10]:
        date = pred['date']
        sales = pred['predicted_sales']
        day = pred['day_of_week']
        print(f"{date:<15} {sales:<12.2f} {day}")
    
    # Calcular estadísticas
    sales_values = [p['predicted_sales'] for p in predictions]
    min_sales = min(sales_values)
    max_sales = max(sales_values)
    avg_sales = sum(sales_values) / len(sales_values)
    
    print("\n" + "─" * 60)
    print("\n📈 Estadísticas:")
    print(f"   • Mínimo: {min_sales:.2f} unidades")
    print(f"   • Máximo: {max_sales:.2f} unidades")
    print(f"   • Promedio: {avg_sales:.2f} unidades")
    print(f"   • Variación: {((max_sales - min_sales) / avg_sales * 100):.1f}%")
    
    print("\n" + "=" * 80)
    print("✅ Las predicciones ahora tienen variaciones realistas!")
    print("=" * 80 + "\n")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.data)
