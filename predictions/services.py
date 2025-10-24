import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
import os
from django.conf import settings

from shop_orders.models import OrderItem, Order


def train_sales_prediction_model(min_samples=10):
    """
    Entrena un modelo de Random Forest para predecir ventas y lo guarda.
    Devuelve un dict con el resultado o un error.
    """
    # 1. Recolectar y preprocesar los datos
    order_items = OrderItem.objects.filter(order__status=Order.OrderStatus.PAID).select_related('order', 'product__category')
    
    if not order_items.exists():
        return {"error": "No hay suficientes datos de ventas para entrenar el modelo."}

    data = [
        {
            'date': item.order.created_at,
            'product_id': item.product.id if item.product else 0,
            'category_id': item.product.category.id if (item.product and item.product.category) else 0,
            'price': float(item.price),
            'quantity': int(item.quantity),
        }
        for item in order_items
    ]

    df = pd.DataFrame(data)
    if df.empty:
        return {"error": "No hay suficientes datos para entrenar el modelo."}

    df['date'] = pd.to_datetime(df['date'])
    # Ingeniería de características: extraer partes de la fecha
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['weekday'] = df['date'].dt.weekday

    # 2. Definir características (X) y objetivo (y)
    features = ['year', 'month', 'day', 'weekday', 'product_id', 'category_id', 'price']
    target = 'quantity'

    X = df[features]
    y = df[target]

    # Simple check for minimum data
    if len(df) < min_samples:
        return {"error": f"Se requieren al menos {min_samples} muestras para entrenar. Datos disponibles: {len(df)}"}

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. Entrenar el modelo
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    # 4. Evaluar el modelo (opcional, pero buena práctica)
    predictions = model.predict(X_test)
    mse = float(mean_squared_error(y_test, predictions))

    # 5. Guardar (serializar) el modelo entrenado
    model_dir = os.path.join(settings.BASE_DIR, 'predictions')
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'sales_model.joblib')
    joblib.dump(model, model_path)

    return {"status": "Modelo entrenado y guardado exitosamente.", "path": model_path, "mse": mse, "n_samples": len(df)}
