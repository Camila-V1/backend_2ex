# users/urls.py

from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import UserViewSet, user_profile

# Usar SimpleRouter
router = SimpleRouter()
router.register(r'', UserViewSet, basename='user')

# Las URLs de la API
urlpatterns = [
    path('profile/', user_profile, name='user-profile'),
]

# Agregamos las URLs del router
urlpatterns += router.urls