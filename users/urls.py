# users/urls.py

from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import UserViewSet, user_profile
from .wallet_views import WalletViewSet, WalletTransactionViewSet

# Usar SimpleRouter
router = SimpleRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'wallets', WalletViewSet, basename='wallet')
router.register(r'wallet-transactions', WalletTransactionViewSet, basename='wallet-transaction')

# Las URLs de la API
urlpatterns = [
    path('profile/', user_profile, name='user-profile'),
]

# Agregamos las URLs del router
urlpatterns += router.urls