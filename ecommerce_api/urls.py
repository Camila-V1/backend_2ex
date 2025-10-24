"""
URL configuration for ecommerce_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# Importaciones para JWT authentication
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Importar vistas de reports DIRECTAMENTE
from reports.views import SalesReportView, ProductsReportView, DynamicReportParserView

# Importaciones para Swagger/OpenAPI
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URLs para autenticación JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # URLs de reports - vistas simples de Django (no DRF)
    path('api/reports/sales/', SalesReportView.as_view(), name='sales-report'),
    path('api/reports/products/', ProductsReportView.as_view(), name='products-report'),
    # Endpoint inteligente para comandos en lenguaje natural (IA)
    path('api/reports/dynamic-parser/', DynamicReportParserView.as_view(), name='dynamic-report-parser'),
    
    # URLs de las otras apps
    path('api/users/', include('users.urls')),
    path('api/products/', include('products.urls')),
    path('api/orders/', include('shop_orders.urls')),
    path('api/', include('predictions.urls')),  # Predicciones con ML
    path('api/', include('reports.urls')),  # Reportes (incluyendo invoices)
    
    # ============================================================================
    # DOCUMENTACIÓN DE LA API (SWAGGER/OpenAPI)
    # ============================================================================
    # Genera el archivo schema.yml en formato OpenAPI 3.0
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Interfaz de usuario Swagger (recomendada - interactiva y moderna)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Interfaz alternativa ReDoc (opcional - documentación más elegante para lectura)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]


