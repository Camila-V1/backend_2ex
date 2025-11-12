from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import CategoryViewSet, ProductViewSet, ReviewViewSet

# Usar SimpleRouter que es más limpio
router = SimpleRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'reviews', ReviewViewSet, basename='review')

# URLs manuales para productos en la raíz
urlpatterns = [
    path('', ProductViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-list'),
    path('personalized/', ProductViewSet.as_view({'get': 'personalized'}), name='product-personalized'),
    path('<int:pk>/', ProductViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='product-detail'),
    path('<int:pk>/reviews/', ProductViewSet.as_view({'get': 'reviews', 'post': 'reviews'}), name='product-reviews'),
    path('<int:pk>/recommendations/', ProductViewSet.as_view({'get': 'recommendations'}), name='product-recommendations'),
]

# Agregar las rutas del router (categories, reviews)
urlpatterns += router.urls

