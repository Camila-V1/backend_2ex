from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import (
    OrderViewSet, 
    CreateOrderView, 
    CreateCheckoutSessionView, 
    StripeWebhookView,
    AdminOrderViewSet,
    admin_dashboard,
    admin_users_list,
    admin_sales_analytics,
    CartNaturalLanguageView,
    ProductSuggestionsView
)

# Usar SimpleRouter
router = SimpleRouter()
router.register(r'', OrderViewSet, basename='order')
router.register(r'admin', AdminOrderViewSet, basename='admin-order')

# URLs manuales
urlpatterns = [
    # Endpoints de usuarios normales
    path('create/', CreateOrderView.as_view(), name='create-order'),
    path('<int:order_id>/create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('stripe-webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    
    # 🎤 NUEVO: Carrito con lenguaje natural (texto/voz)
    path('cart/add-natural-language/', CartNaturalLanguageView.as_view(), name='cart-natural-language'),
    path('cart/suggestions/', ProductSuggestionsView.as_view(), name='product-suggestions'),
    
    # Endpoints de administración - Dashboard y Analytics
    path('admin/dashboard/', admin_dashboard, name='admin-dashboard'),
    path('admin/users/', admin_users_list, name='admin-users'),
    path('admin/analytics/sales/', admin_sales_analytics, name='admin-sales-analytics'),
]

# Agregar rutas del router
urlpatterns += router.urls