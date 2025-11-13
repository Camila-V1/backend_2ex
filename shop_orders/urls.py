from django.urls import path
from django.views.generic import RedirectView
from rest_framework.routers import SimpleRouter
from .views import (
    OrderViewSet, 
    CreateOrderView, 
    CreateCheckoutSessionView, 
    CreatePaymentIntentView,
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

# Router separado para admin orders (debe ir ANTES de las rutas específicas)
admin_router = SimpleRouter()
admin_router.register(r'admin', AdminOrderViewSet, basename='admin-order')

# URLs manuales
urlpatterns = [
    # Endpoints de usuarios normales
    path('create/', CreateOrderView.as_view(), name='create-order'),
    path('<int:order_id>/create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('stripe-webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    
    # 📱 NUEVO: Payment Intent para app móvil (Flutter)
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    
    # 🧾 REDIRECT: Mantener compatibilidad con endpoint antiguo de invoice
    path('<int:order_id>/invoice/', RedirectView.as_view(url='/api/reports/orders/%(order_id)s/invoice/', permanent=True), name='order-invoice-redirect'),
    
    # 🎤 NUEVO: Carrito con lenguaje natural (texto/voz)
    path('cart/add-natural-language/', CartNaturalLanguageView.as_view(), name='cart-natural-language'),
    path('cart/suggestions/', ProductSuggestionsView.as_view(), name='product-suggestions'),
]

# Endpoints de administración - Dashboard y Analytics (rutas más específicas primero)
urlpatterns += [
    path('admin/dashboard/', admin_dashboard, name='admin-dashboard'),
    path('admin/users/', admin_users_list, name='admin-users'),
    path('admin/analytics/sales/', admin_sales_analytics, name='admin-sales-analytics'),
]

# IMPORTANTE: Agregar rutas de admin ViewSet (lista/detail) después para evitar
# que el patrón admin/(?P<pk>...) capture rutas como 'dashboard' o 'users'
urlpatterns += admin_router.urls

# Agregar rutas del router de órdenes normales al final
urlpatterns += router.urls