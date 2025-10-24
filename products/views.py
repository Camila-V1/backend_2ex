from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from .models import Category, Product, Review
from .serializers import CategorySerializer, ProductSerializer, ReviewSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado: permite leer a cualquiera,
    pero solo los administradores pueden escribir (crear, editar, borrar).
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        """
        - Admin: ve todos los productos (activos e inactivos)
        - Usuarios normales: solo ven productos activos
        """
        if self.request.user and self.request.user.is_staff:
            return Product.objects.all()
        return Product.objects.filter(is_active=True)
    
    @action(detail=True, methods=['get', 'post'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def reviews(self, request, pk=None):
        """
        Endpoint para gestionar reseñas de un producto.
        GET /api/products/{id}/reviews/ - Lista todas las reseñas
        POST /api/products/{id}/reviews/ - Crear una reseña (requiere autenticación)
        """
        product = self.get_object()
        
        if request.method == 'GET':
            # Listar todas las reseñas del producto
            reviews = product.reviews.all()
            serializer = ReviewSerializer(reviews, many=True)
            return Response({
                'count': reviews.count(),
                'average_rating': product.average_rating,
                'reviews': serializer.data
            })
        
        elif request.method == 'POST':
            # Crear una nueva reseña
            # Verificar si el usuario ya tiene una reseña para este producto
            existing_review = Review.objects.filter(product=product, user=request.user).first()
            if existing_review:
                return Response(
                    {'error': 'Ya has dejado una reseña para este producto. Puedes editarla en su lugar.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, product=product)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def recommendations(self, request, pk=None):
        """
        Sistema de recomendación simple: productos comprados junto con este.
        GET /api/products/{id}/recommendations/
        """
        product = self.get_object()
        
        # Productos comprados junto con el producto actual
        # Usa 'order_items' (related_name en OrderItem)
        recommended = Product.objects.filter(
            order_items__order__items__product_id=pk,
            is_active=True
        ).exclude(
            id=pk
        ).annotate(
            times_bought_together=Count('id')
        ).order_by('-times_bought_together')[:5]
        
        serializer = ProductSerializer(recommended, many=True)
        return Response({
            'product': product.name,
            'recommendations': serializer.data
        })


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar reseñas.
    Solo el autor o un admin pueden editar/eliminar una reseña.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Lista todas las reseñas o filtra por producto si se pasa ?product=ID"""
        queryset = Review.objects.all()
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset
    
    def perform_create(self, serializer):
        """Al crear, asigna automáticamente el usuario actual."""
        serializer.save(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """Solo el autor o admin pueden actualizar."""
        review = self.get_object()
        if review.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'No tienes permiso para editar esta reseña.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Solo el autor o admin pueden eliminar."""
        review = self.get_object()
        if review.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'No tienes permiso para eliminar esta reseña.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

