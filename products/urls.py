from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import CategoryViewSet, ProductViewSet

# Usar SimpleRouter que es más limpio
router = SimpleRouter()
router.register(r'categories', CategoryViewSet, basename='category')

# URLs manuales para productos en la raíz
urlpatterns = [
    path('', ProductViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-list'),
    path('<int:pk>/', ProductViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='product-detail'),
]

# Agregar las rutas del router (categories)
urlpatterns += router.urls
