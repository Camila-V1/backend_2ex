from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Category, Product


# Simplified serializers for order contexts (no reviews to avoid N+1 queries)
class SimpleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class SimpleProductSerializer(serializers.ModelSerializer):
    """Simplified product serializer for orders - optimized to use prefetched data"""
    category_details = SimpleCategorySerializer(source='category', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock',
            'category_details', 'image_url',
            'warranty_info', 'is_active'
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)  # Simplified product without reviews
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField()  # Muestra el username en lugar del ID
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, source='total_price', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'status', 'total_price', 'total_amount', 'items']


class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemCreateSerializer(many=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("El carrito no puede estar vacío.")
        return items


# ============================================================================
# SERIALIZERS PARA SCHEMA DE DOCUMENTACIÓN
# ============================================================================

class CheckoutSessionSerializer(serializers.Serializer):
    """Serializer para respuesta de sesión de checkout de Stripe"""
    checkout_url = serializers.URLField(help_text="URL de pago de Stripe")


class StripeWebhookSerializer(serializers.Serializer):
    """Serializer para webhook de Stripe (solo para documentación)"""
    type = serializers.CharField(help_text="Tipo de evento de Stripe")
    data = serializers.JSONField(help_text="Datos del evento")


class NLPCartRequestSerializer(serializers.Serializer):
    """Serializer para solicitud de carrito con lenguaje natural"""
    prompt = serializers.CharField(
        help_text="Comando en lenguaje natural, ej: 'Agrega 2 smartphones al carrito'"
    )


class NLPCartResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de carrito NLP"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    prompt = serializers.CharField()
    interpreted_action = serializers.CharField()
    order = OrderSerializer(required=False)
    items = serializers.ListField(required=False)
    error = serializers.CharField(required=False)


class ProductSuggestionSerializer(serializers.Serializer):
    """Serializer para sugerencias de productos"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    category = serializers.CharField()


class ProductSuggestionsResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de sugerencias"""
    query = serializers.CharField()
    count = serializers.IntegerField()
    suggestions = ProductSuggestionSerializer(many=True)


# ============================================================================
# SERIALIZERS PARA VISTAS ADMIN (@api_view)
# ============================================================================

class DashboardOverviewSerializer(serializers.Serializer):
    """Serializer para overview del dashboard"""
    total_orders = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_products = serializers.IntegerField()
    active_products = serializers.IntegerField()
    total_revenue = serializers.FloatField()


class DashboardSalesSerializer(serializers.Serializer):
    """Serializer para datos de ventas del dashboard"""
    current_month_revenue = serializers.FloatField()
    last_month_revenue = serializers.FloatField()
    growth_percentage = serializers.FloatField()


class TopProductSerializer(serializers.Serializer):
    """Serializer para productos más vendidos"""
    product__id = serializers.IntegerField()
    product__name = serializers.CharField()
    product__price = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_sold = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)


class LowStockProductSerializer(serializers.Serializer):
    """Serializer para productos con stock bajo"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    stock = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)


class DashboardResponseSerializer(serializers.Serializer):
    """Serializer para respuesta completa del dashboard"""
    overview = DashboardOverviewSerializer()
    sales = DashboardSalesSerializer()
    orders_by_status = serializers.ListField(child=serializers.DictField())
    top_products = TopProductSerializer(many=True)
    recent_orders = OrderSerializer(many=True)
    low_stock_products = LowStockProductSerializer(many=True)
    _from_cache = serializers.BooleanField()


class AdminUserSerializer(serializers.Serializer):
    """Serializer para usuario en lista de admin"""
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_active = serializers.BooleanField()
    date_joined = serializers.DateTimeField()
    total_orders = serializers.IntegerField()
    total_spent = serializers.FloatField()


class AdminUsersResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de lista de usuarios"""
    count = serializers.IntegerField()
    users = AdminUserSerializer(many=True)


class DailySalesSerializer(serializers.Serializer):
    """Serializer para ventas diarias"""
    day = serializers.DateField()
    orders_count = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)


class SalesAnalyticsResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de analytics de ventas"""
    daily_sales = DailySalesSerializer(many=True)