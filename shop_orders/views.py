import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Sum, Q, F
from datetime import datetime, timedelta

from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer
from products.models import Product
from .nlp_service import CartNLPService


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permite el acceso solo al dueño del objeto o a un admin."""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ver órdenes. La creación se manejará en un endpoint aparte.
    - list: Un usuario ve sus propias órdenes. Un admin ve todas.
    - retrieve: Un usuario ve el detalle de su orden. Un admin ve cualquiera.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)


class CreateOrderView(APIView):
    """
    Vista para crear una nueva orden a partir del carrito de compras.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cart_items = serializer.validated_data['items']
        
        try:
            # Usamos una transacción para asegurar que todas las operaciones de BD 
            # se completen exitosamente o ninguna lo haga.
            with transaction.atomic():
                # 1. Crear la Orden principal
                order = Order.objects.create(user=request.user)
                
                total_order_price = 0

                for item_data in cart_items:
                    product = Product.objects.get(id=item_data['product_id'])
                    quantity = item_data['quantity']

                    # 2. Validar stock
                    if product.stock < quantity:
                        raise ValueError(f"Stock insuficiente para {product.name}. Disponible: {product.stock}")

                    # 3. Crear el OrderItem
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price  # Guardamos el precio actual del producto
                    )
                    
                    # 4. Actualizar el stock del producto
                    product.stock -= quantity
                    product.save()

                    total_order_price += order_item.price * order_item.quantity
                
                # 5. Actualizar el precio total de la orden
                order.total_price = total_order_price
                order.save()

            # Devolver la orden creada y serializada
            final_order_serializer = OrderSerializer(order)
            return Response(final_order_serializer.data, status=status.HTTP_201_CREATED)
        
        except Product.DoesNotExist:
            return Response({"error": "Uno de los productos no fue encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreateCheckoutSessionView(APIView):
    """
    Crea una sesión de pago en Stripe para una orden específica.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        order_id = self.kwargs.get("order_id")
        try:
            order = Order.objects.get(id=order_id, user=request.user, status=Order.OrderStatus.PENDING)
        except Order.DoesNotExist:
            return Response({"error": "Orden no encontrada o ya ha sido procesada."}, status=status.HTTP_404_NOT_FOUND)

        # URLs a las que Stripe redirigirá al usuario
        # Usa la URL del frontend configurada en settings
        frontend_url = settings.FRONTEND_URL
        success_url = f'{frontend_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}'
        cancel_url = f'{frontend_url}/payment-cancelled'

        # Prepara los items para la API de Stripe
        line_items = []
        for item in order.items.all():
            line_items.append({
                'price_data': {
                    'currency': 'usd',  # o la moneda que uses
                    'product_data': {
                        'name': item.product.name,
                    },
                    'unit_amount': int(item.price * 100),  # Stripe usa centavos
                },
                'quantity': item.quantity,
            })

        try:
            # Crea la sesión de Checkout en Stripe
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                # Guardamos el ID de nuestra orden en los metadatos de Stripe
                # para saber qué orden actualizar cuando el pago se complete.
                metadata={
                    'order_id': order.id
                }
            )
            # Devolvemos la URL de pago al frontend
            return Response({'checkout_url': checkout_session.url})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StripeWebhookView(APIView):
    """
    Escucha los eventos de Stripe. Específicamente, cuando una sesión de checkout se completa,
    actualiza el estado de la orden correspondiente a 'PAGADO'.
    """
    permission_classes = [permissions.AllowAny]  # Los webhooks vienen de Stripe, no de un usuario

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        if not sig_header:
            return Response({'error': 'Missing Stripe signature header'}, status=status.HTTP_400_BAD_REQUEST)
        
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Payload inválido
            return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            # Firma inválida
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        # Manejar el evento checkout.session.completed
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            order_id = session.get('metadata', {}).get('order_id')
            
            if order_id is None:
                return Response({'error': 'Falta order_id en los metadatos de Stripe'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                order = Order.objects.get(id=order_id)
                # Verificar que la orden no esté ya pagada para evitar reprocesarla
                if order.status == Order.OrderStatus.PENDING:
                    order.status = Order.OrderStatus.PAID
                    order.save()
            except Order.DoesNotExist:
                return Response({'error': 'Orden no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_200_OK)


# =============================================================================
# ADMIN VIEWS - Solo para administradores
# =============================================================================


class AdminOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet para administración completa de órdenes (solo admins)
    - GET /api/admin/orders/ - Lista todas las órdenes
    - GET /api/admin/orders/{id}/ - Detalle de una orden
    - PATCH /api/admin/orders/{id}/ - Actualizar estado de orden
    - DELETE /api/admin/orders/{id}/ - Eliminar orden
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Order.objects.all().order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Endpoint especial para cambiar el estado de una orden
        POST /api/admin/orders/{id}/update_status/
        Body: {"status": "shipped"}
        """
        order = self.get_object()
        new_status = request.data.get('status')
        
        valid_statuses = ['pending', 'paid', 'shipped', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Estado inválido. Debe ser uno de: {", ".join(valid_statuses)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_dashboard(request):
    """
    Dashboard con estadísticas para el administrador
    GET /api/admin/dashboard/
    """
    # Periodo de tiempo para estadísticas
    today = datetime.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    # Estadísticas generales
    total_orders = Order.objects.count()
    total_users = get_user_model().objects.filter(is_staff=False).count()
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    
    # Órdenes por estado
    orders_by_status = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Ventas totales
    total_revenue = Order.objects.filter(
        status__in=['PAID', 'SHIPPED', 'DELIVERED']
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    # Ventas del mes actual
    current_month_revenue = Order.objects.filter(
        status__in=['PAID', 'SHIPPED', 'DELIVERED'],
        created_at__gte=this_month_start
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    # Ventas del mes anterior
    last_month_revenue = Order.objects.filter(
        status__in=['PAID', 'SHIPPED', 'DELIVERED'],
        created_at__gte=last_month_start,
        created_at__lt=this_month_start
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    # Productos más vendidos (top 10)
    top_products = OrderItem.objects.filter(
        order__status__in=['PAID', 'SHIPPED', 'DELIVERED']
    ).values(
        'product__id',
        'product__name',
        'product__price'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('price'))
    ).order_by('-total_sold')[:10]
    
    # Órdenes recientes (últimas 10)
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    recent_orders_data = OrderSerializer(recent_orders, many=True).data
    
    # Productos con stock bajo (menos de 10 unidades)
    low_stock_products = Product.objects.filter(
        stock__lt=10,
        is_active=True
    ).values('id', 'name', 'stock', 'price')
    
    # Calcular crecimiento mensual
    growth_percentage = 0
    if last_month_revenue > 0:
        growth_percentage = ((current_month_revenue - last_month_revenue) / last_month_revenue) * 100
    
    return Response({
        'overview': {
            'total_orders': total_orders,
            'total_users': total_users,
            'total_products': total_products,
            'active_products': active_products,
            'total_revenue': float(total_revenue),
        },
        'sales': {
            'current_month_revenue': float(current_month_revenue),
            'last_month_revenue': float(last_month_revenue),
            'growth_percentage': round(growth_percentage, 2),
        },
        'orders_by_status': list(orders_by_status),
        'top_products': list(top_products),
        'recent_orders': recent_orders_data,
        'low_stock_products': list(low_stock_products),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_users_list(request):
    """
    Lista de todos los usuarios (excepto admins)
    GET /api/admin/users/
    """
    User = get_user_model()
    users = User.objects.filter(is_staff=False).values(
        'id', 'username', 'email', 'first_name', 'last_name', 
        'is_active', 'date_joined'
    )
    
    # Agregar estadísticas de órdenes por usuario
    users_data = []
    for user in users:
        user_orders = Order.objects.filter(user_id=user['id'])
        user_data = dict(user)
        user_data['total_orders'] = user_orders.count()
        user_data['total_spent'] = float(
            user_orders.filter(
                status__in=['PAID', 'SHIPPED', 'DELIVERED']
            ).aggregate(total=Sum('total_price'))['total'] or 0
        )
        users_data.append(user_data)
    
    return Response({
        'count': len(users_data),
        'users': users_data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_sales_analytics(request):
    """
    Análisis detallado de ventas por día, semana, mes
    GET /api/admin/analytics/sales/
    """
    # Ventas por día (últimos 30 días)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    daily_sales = Order.objects.filter(
        status__in=['PAID', 'SHIPPED', 'DELIVERED'],
        created_at__gte=thirty_days_ago
    ).extra(
        select={'day': 'DATE(created_at)'}
    ).values('day').annotate(
        orders_count=Count('id'),
        revenue=Sum('total_price')
    ).order_by('day')
    
    return Response({
        'daily_sales': list(daily_sales),
    })


# ============================================================================
# NUEVAS FUNCIONALIDADES: CARRITO CON LENGUAJE NATURAL
# ============================================================================


class CartNaturalLanguageView(APIView):
    """
    🎤 Vista para agregar productos al carrito usando lenguaje natural (texto o voz)
    POST /api/cart/add-natural-language/
    
    Ejemplos de comandos:
    - "Agrega 2 smartphones al carrito"
    - "Quiero 3 laptops y 1 mouse"
    - "Añade el curso de Python"
    - "Comprar 5 auriculares bluetooth"
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        prompt = request.data.get('prompt', '').strip()
        
        if not prompt:
            return Response(
                {'error': 'El campo "prompt" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Procesar comando con NLP
        result = CartNLPService.parse_cart_command(prompt)
        
        if result['error']:
            return Response(
                {
                    'success': False,
                    'error': result['error'],
                    'prompt': prompt
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Si la acción es 'add', crear la orden
        if result['action'] == 'add' and result['items']:
            try:
                with transaction.atomic():
                    # Validar stock para cada producto
                    for item in result['items']:
                        product = Product.objects.get(id=item['product_id'])
                        if product.stock < item['quantity']:
                            return Response(
                                {
                                    'success': False,
                                    'error': f'Stock insuficiente para "{product.name}". Stock disponible: {product.stock}',
                                    'prompt': prompt
                                },
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    
                    # Crear orden con status PENDING
                    order = Order.objects.create(
                        user=request.user,
                        status='PENDING'
                    )
                    
                    # Crear items de la orden y calcular total
                    total_price = 0
                    for item in result['items']:
                        product = Product.objects.get(id=item['product_id'])
                        
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=item['quantity'],
                            price=product.price
                        )
                        
                        # Actualizar stock
                        product.stock -= item['quantity']
                        product.save()
                        
                        total_price += product.price * item['quantity']
                    
                    order.total_price = total_price
                    order.save()
                    
                    return Response(
                        {
                            'success': True,
                            'message': 'Orden creada exitosamente',
                            'prompt': prompt,
                            'interpreted_action': result['action'],
                            'order': {
                                'id': order.id,
                                'total': str(order.total_price),
                                'status': order.status,
                                'items': result['items']
                            }
                        },
                        status=status.HTTP_201_CREATED
                    )
            
            except Product.DoesNotExist:
                return Response(
                    {
                        'success': False,
                        'error': 'Uno de los productos no existe',
                        'prompt': prompt
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {
                        'success': False,
                        'error': f'Error al crear la orden: {str(e)}',
                        'prompt': prompt
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Si la acción es 'clear' o 'remove', devolver mensaje
        return Response(
            {
                'success': True,
                'message': f'Acción interpretada: {result["action"]}',
                'prompt': prompt,
                'interpreted_action': result['action'],
                'items': result['items']
            }
        )


class ProductSuggestionsView(APIView):
    """
    🔍 Vista para obtener sugerencias de productos (autocompletado)
    GET /api/cart/suggestions/?q=smart
    """
    permission_classes = [permissions.AllowAny]  # Público para mejor UX
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return Response(
                {'suggestions': []},
                status=status.HTTP_200_OK
            )
        
        suggestions = CartNLPService.get_suggestions(query)
        
        return Response(
            {
                'query': query,
                'count': len(suggestions),
                'suggestions': suggestions
            }
        )

