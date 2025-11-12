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
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def personalized(self, request):
        """
        🎯 Recomendaciones personalizadas para el cliente actual.
        GET /api/products/personalized/
        
        Estrategia de IA:
        1. Analiza historial de compras del cliente
        2. Encuentra productos similares (misma categoría)
        3. Productos comprados por usuarios con gustos similares (collaborative filtering)
        4. Productos populares si no hay historial
        """
        from shop_orders.models import OrderItem, Order
        from django.db.models import Q, F, Sum
        
        user = request.user
        limit = int(request.GET.get('limit', 10))  # Número de productos a retornar
        
        # 1. Obtener categorías favoritas del usuario (basado en historial)
        user_categories = OrderItem.objects.filter(
            order__user=user,
            order__status__in=[Order.OrderStatus.PAID, Order.OrderStatus.DELIVERED]
        ).values('product__category').annotate(
            total_spent=Sum(F('quantity') * F('price'))
        ).order_by('-total_spent')[:3]
        
        favorite_category_ids = [cat['product__category'] for cat in user_categories if cat['product__category']]
        
        # 2. Productos ya comprados por el usuario (para excluirlos)
        purchased_product_ids = OrderItem.objects.filter(
            order__user=user
        ).values_list('product_id', flat=True).distinct()
        
        recommended_products = []
        
        # ESTRATEGIA 1: Si tiene historial - Productos de sus categorías favoritas
        if favorite_category_ids:
            category_products = Product.objects.filter(
                category_id__in=favorite_category_ids,
                is_active=True
            ).exclude(
                id__in=purchased_product_ids
            ).order_by('-created_at')[:limit]
            
            recommended_products.extend(category_products)
        
        # ESTRATEGIA 2: Collaborative Filtering - Usuarios con gustos similares
        if len(recommended_products) < limit:
            # Encontrar usuarios que compraron productos similares
            similar_users = OrderItem.objects.filter(
                product_id__in=purchased_product_ids
            ).exclude(
                order__user=user
            ).values('order__user').annotate(
                similarity=Count('id')
            ).order_by('-similarity')[:5]
            
            similar_user_ids = [u['order__user'] for u in similar_users]
            
            if similar_user_ids:
                collaborative_products = Product.objects.filter(
                    order_items__order__user_id__in=similar_user_ids,
                    is_active=True
                ).exclude(
                    id__in=purchased_product_ids
                ).annotate(
                    popularity=Count('id')
                ).order_by('-popularity')[:limit - len(recommended_products)]
                
                recommended_products.extend(collaborative_products)
        
        # ESTRATEGIA 3: Productos populares (fallback si no hay suficientes recomendaciones)
        if len(recommended_products) < limit:
            popular_products = Product.objects.filter(
                is_active=True
            ).exclude(
                id__in=purchased_product_ids
            ).annotate(
                times_sold=Count('order_items')
            ).order_by('-times_sold', '-created_at')[:limit - len(recommended_products)]
            
            recommended_products.extend(popular_products)
        
        # Eliminar duplicados y limitar
        unique_products = []
        seen_ids = set()
        for product in recommended_products:
            if product.id not in seen_ids:
                unique_products.append(product)
                seen_ids.add(product.id)
                if len(unique_products) >= limit:
                    break
        
        serializer = ProductSerializer(unique_products, many=True)
        
        return Response({
            'user': user.username,
            'count': len(unique_products),
            'strategy_used': 'personalized_ai' if favorite_category_ids else 'popular_products',
            'favorite_categories': list(Category.objects.filter(id__in=favorite_category_ids).values_list('name', flat=True)),
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

