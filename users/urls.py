# users/urls.py

from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import UserViewSet, user_profile
from .wallet_views import WalletViewSet, WalletTransactionViewSet
from .device_token_views import (
    DeviceTokenViewSet,
    register_device_token,
    unregister_all_tokens
)

# Usar SimpleRouter
router = SimpleRouter()
router.register(r'wallets', WalletViewSet, basename='wallet')
router.register(r'wallet-transactions', WalletTransactionViewSet, basename='wallet-transaction')
router.register(r'device-tokens', DeviceTokenViewSet, basename='device-token')
# El UserViewSet va al final para no conflictuar con rutas específicas
router.register(r'', UserViewSet, basename='user')

# IMPORTANTE: Las URLs específicas DEBEN ir ANTES del router
# para evitar que el router las capture primero
urlpatterns = [
    # Rutas específicas PRIMERO
    path('profile/', user_profile, name='user-profile'),
    path('register-device-token/', register_device_token, name='register-device-token'),
    path('unregister-all-tokens/', unregister_all_tokens, name='unregister-all-tokens'),
]

# Agregamos las URLs del router AL FINAL
urlpatterns += router.urls