import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from django.core.cache import cache
from datetime import datetime, timedelta

from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Order, OrderItem
from users.permissions import IsAdminOrManager

from .serializers import (
    OrderSerializer, OrderCreateSerializer,
    CheckoutSessionSerializer, StripeWebhookSerializer,
    NLPCartRequestSerializer, NLPCartResponseSerializer,
    ProductSuggestionsResponseSerializer,
    DashboardResponseSerializer, AdminUsersResponseSerializer,
    SalesAnalyticsResponseSerializer
)
from products.models import Product
from .nlp_service import CartNLPService
from users.permissions import IsAdminUser, IsManagerUser, IsCajeroUser, IsAdminOrManager


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
    Permisos: CAJERO, MANAGER o ADMIN pueden crear órdenes.
    
    Soporta dos métodos de pago:
    - Stripe: Crea orden en PENDING, se procesa con webhook
    - Wallet: Paga inmediatamente con billetera virtual
    """
    permission_classes = [permissions.IsAuthenticated]  # Cualquier usuario autenticado puede crear órdenes
    serializer_class = OrderCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cart_items = serializer.validated_data['items']
        payment_method = request.data.get('payment_method', 'stripe')  # 'stripe' o 'wallet'
        
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

                    total_order_price += order_item.price * order_item.quantity
                
                # 4. Actualizar el precio total de la orden
                order.total_price = total_order_price
                order.save()

                # 5. SI EL PAGO ES CON BILLETERA, PROCESARLO INMEDIATAMENTE
                if payment_method == 'wallet':
                    try:
                        from users.wallet_models import Wallet, WalletTransaction
                        
                        # Obtener o crear billetera del usuario
                        wallet, created = Wallet.objects.get_or_create(user=request.user)
                        
                        # Verificar saldo suficiente
                        if wallet.balance < order.total_price:
                            raise ValueError(
                                f"Saldo insuficiente. Necesitas ${order.total_price}, tienes ${wallet.balance}"
                            )
                        
                        # Deducir fondos de la billetera
                        wallet.deduct_funds(
                            amount=order.total_price,
                            transaction_type=WalletTransaction.TransactionType.PURCHASE,
                            description=f"Compra - Orden #{order.id}",
                            reference_id=str(order.id)
                        )
                        
                        # Actualizar estado de la orden a PAID
                        order.status = Order.OrderStatus.PAID
                        order.save()
                        
                        # Reducir stock de los productos
                        for item in order.items.all():
                            product = item.product
                            product.stock -= item.quantity
                            product.save()
                        
                        print(f"✅ Orden #{order.id} pagada con billetera. Saldo restante: ${wallet.balance}")
                    
                    except ValueError as e:
                        # Error de saldo insuficiente o validación
                        raise ValueError(str(e))
                    except Exception as e:
                        print(f"❌ Error procesando pago con billetera: {str(e)}")
                        raise ValueError(f"Error procesando pago con billetera: {str(e)}")

            # Devolver la orden creada y serializada
            final_order_serializer = OrderSerializer(order)
            response_data = final_order_serializer.data
            
            # Agregar información adicional si fue pago con billetera
            if payment_method == 'wallet':
                response_data['paid_with_wallet'] = True
                response_data['message'] = 'Orden pagada exitosamente con billetera virtual'
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        except Product.DoesNotExist:
            return Response({"error": "Uno de los productos no fue encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreateCheckoutSessionView(APIView):
    """
    Crea una sesión de pago en Stripe para una orden específica.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderCreateSerializer

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


class CreatePaymentIntentView(APIView):
    """
    📱 Crea un PaymentIntent de Stripe para uso en SDK móvil (Flutter).
    
    Este endpoint está diseñado para apps móviles que usan el Stripe SDK nativo.
    En lugar de crear una sesión de checkout web, crea un PaymentIntent que
    puede ser usado con Stripe.instance.presentPaymentSheet() en Flutter.
    
    Request:
        POST /api/orders/create-payment-intent/
        Body: {
            "order_id": int,           # ID de la orden existente (PENDING)
            "currency": "usd"          # Opcional, por defecto "usd"
        }
    
    Response:
        {
            "client_secret": string,   # Para inicializar el payment sheet
            "publishable_key": string, # Clave pública de Stripe
            "customer_id": string,     # ID del customer de Stripe (opcional)
            "ephemeral_key": string    # Para autenticación (opcional)
        }
    
    Uso en Flutter:
        1. Llamar a este endpoint para obtener client_secret
        2. Inicializar payment sheet con Stripe.instance.initPaymentSheet()
        3. Mostrar sheet con Stripe.instance.presentPaymentSheet()
        4. El webhook confirmará el pago y actualizará la orden
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            # 1. Obtener datos de la request
            order_id = request.data.get('order_id')
            currency = request.data.get('currency', 'usd')
            
            if not order_id:
                return Response(
                    {'error': 'order_id es requerido'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 2. Verificar que la orden existe y pertenece al usuario
            try:
                order = Order.objects.get(
                    id=order_id, 
                    user=request.user, 
                    status=Order.OrderStatus.PENDING
                )
            except Order.DoesNotExist:
                return Response(
                    {'error': 'Orden no encontrada o ya ha sido procesada'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 3. Calcular el monto total en centavos
            total_amount = int(order.total_price * 100)
            
            if total_amount <= 0:
                return Response(
                    {'error': 'El monto de la orden debe ser mayor a 0'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 4. Crear descripción de los items
            items_description = ', '.join([
                f"{item.product.name} x{item.quantity}" 
                for item in order.items.all()[:3]  # Limitar a 3 items para la descripción
            ])
            if order.items.count() > 3:
                items_description += f' (+{order.items.count() - 3} más)'
            
            # 5. Crear el Payment Intent en Stripe
            payment_intent = stripe.PaymentIntent.create(
                amount=total_amount,
                currency=currency,
                description=f'Orden #{order.id}: {items_description}',
                metadata={
                    'order_id': str(order.id),
                    'user_id': str(request.user.id),
                    'username': request.user.username,
                    'integration_check': 'mobile_payment_intent_v1'
                },
                # Configuración recomendada para mobile
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            
            # 6. Devolver el client_secret y datos necesarios para Flutter
            return Response({
                'client_secret': payment_intent.client_secret,
                'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
                'order_id': order.id,
                'amount': total_amount,
                'currency': currency,
            }, status=status.HTTP_200_OK)
            
        except stripe.error.StripeError as e:
            return Response(
                {'error': f'Error de Stripe: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error interno: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StripeWebhookView(APIView):
    """
    Escucha los eventos de Stripe. Específicamente, cuando una sesión de checkout se completa,
    actualiza el estado de la orden correspondiente a 'PAGADO'.
    """
    permission_classes = [permissions.AllowAny]  # Los webhooks vienen de Stripe, no de un usuario
    serializer_class = StripeWebhookSerializer

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

        # Función auxiliar para procesar el pago de una orden
        def process_order_payment(order_id):
            """Procesa el pago de una orden: reduce stock y actualiza estado"""
            try:
                order = Order.objects.get(id=order_id)
                # Verificar que la orden no esté ya pagada para evitar reprocesarla
                if order.status == Order.OrderStatus.PENDING:
                    # ✅ Reducir stock SOLO cuando se confirma el pago
                    for item in order.items.all():
                        if item.product:
                            product = item.product
                            # Verificar que haya stock suficiente
                            if product.stock >= item.quantity:
                                product.stock -= item.quantity
                                product.save()
                            else:
                                # Si no hay stock, cancelar la orden y reembolsar
                                order.status = Order.OrderStatus.CANCELLED
                                order.save()
                                # TODO: Implementar reembolso automático en Stripe
                                return Response(
                                    {'error': f'Stock insuficiente para {product.name}'},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                    
                    # Cambiar estado a PAID después de reducir stock
                    order.status = Order.OrderStatus.PAID
                    order.save()
                    return Response(status=status.HTTP_200_OK)
                return Response(status=status.HTTP_200_OK)
            except Order.DoesNotExist:
                return Response({'error': 'Orden no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        # Manejar el evento checkout.session.completed (para pagos web)
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            order_id = session.get('metadata', {}).get('order_id')
            
            if order_id is None:
                return Response({'error': 'Falta order_id en los metadatos de Stripe'}, status=status.HTTP_400_BAD_REQUEST)
            
            return process_order_payment(order_id)
        
        # 📱 Manejar el evento payment_intent.succeeded (para pagos móviles con Payment Intent)
        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            order_id = payment_intent.get('metadata', {}).get('order_id')
            
            if order_id is None:
                return Response({'error': 'Falta order_id en los metadatos del PaymentIntent'}, status=status.HTTP_400_BAD_REQUEST)
            
            return process_order_payment(order_id)

        return Response(status=status.HTTP_200_OK)


# =============================================================================
# ADMIN VIEWS - Solo para administradores
# =============================================================================


class AdminOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet para administración completa de órdenes (solo admins y managers)
    - GET /api/admin/orders/ - Lista todas las órdenes
    - GET /api/admin/orders/{id}/ - Detalle de una orden
    - PATCH /api/admin/orders/{id}/ - Actualizar estado de orden
    - DELETE /api/admin/orders/{id}/ - Eliminar orden
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrManager]
    # Forzar que el lookup de detail use solo IDs numéricos para evitar colisiones
    # con rutas estáticas como 'dashboard' o 'users' que de otro modo podrían
    # coincidir con el patrón <pk> y producir 404.
    lookup_value_regex = r"\d+"
    queryset = Order.objects.all().order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Endpoint especial para cambiar el estado de una orden
        POST /api/admin/orders/{id}/update_status/
        Body: {"status": "PAID"} o {"status": "paid"} (case-insensitive)
        """
        order = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {
                    'error': 'El campo "status" es requerido',
                    'received_data': request.data
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Convertir a MAYÚSCULAS para que coincida con el modelo
        new_status = new_status.upper()
        
        # Validar contra las opciones del modelo
        valid_statuses = [choice[0] for choice in Order.OrderStatus.choices]
        if new_status not in valid_statuses:
            return Response(
                {
                    'error': f'Estado inválido. Debe ser uno de: {", ".join(valid_statuses)}',
                    'received_status': new_status,
                    'valid_statuses': valid_statuses
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)


@extend_schema(
    responses=DashboardResponseSerializer,
    description="Dashboard con estadísticas administrativas. Incluye overview, ventas, productos top, órdenes recientes y stock bajo.",
    tags=['Admin']
)
@api_view(['GET'])
@permission_classes([IsAdminOrManager])
def admin_dashboard(request):
    """
    Dashboard con estadísticas para el administrador.
    GET /api/admin/dashboard/
    
    Implementa caching con Redis para mejorar el rendimiento.
    Cache TTL: 5 minutos
    """
    cache_key = 'admin_dashboard_data'
    
    # Intentar obtener del cache
    cached_data = cache.get(cache_key)
    if cached_data:
        # Agregar header para indicar que viene del cache
        cached_data['_from_cache'] = True
        return Response(cached_data)
    
    # Si no está en cache, calcular
    # Periodo de tiempo para estadísticas
    today = timezone.now().date()
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
        created_at__gte=timezone.make_aware(datetime.combine(this_month_start, datetime.min.time()))
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    # Ventas del mes anterior
    last_month_revenue = Order.objects.filter(
        status__in=['PAID', 'SHIPPED', 'DELIVERED'],
        created_at__gte=timezone.make_aware(datetime.combine(last_month_start, datetime.min.time())),
        created_at__lt=timezone.make_aware(datetime.combine(this_month_start, datetime.min.time()))
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
    
    dashboard_data = {
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
        '_from_cache': False
    }
    
    # Guardar en cache por 5 minutos
    cache.set(cache_key, dashboard_data, timeout=300)
    
    return Response(dashboard_data)


@extend_schema(
    responses=AdminUsersResponseSerializer,
    description="Lista de todos los usuarios del sistema (excepto administradores) con sus estadísticas de compras",
    tags=['Admin']
)
@api_view(['GET'])
@permission_classes([IsAdminOrManager])
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


@extend_schema(
    responses=SalesAnalyticsResponseSerializer,
    description="Análisis detallado de ventas diarias (últimos 30 días)",
    tags=['Admin']
)
@api_view(['GET'])
@permission_classes([IsAdminOrManager])
def admin_sales_analytics(request):
    """
    Análisis detallado de ventas por día, semana, mes
    GET /api/admin/analytics/sales/
    """
    # Ventas por día (últimos 30 días)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
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
    serializer_class = NLPCartRequestSerializer
    
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
        
        # Si la acción es 'add', devolver productos para agregar al carrito
        if result['action'] == 'add' and result['items']:
            try:
                # Validar stock y obtener información de productos
                items_data = []
                total_price = 0
                
                for item in result['items']:
                    try:
                        product = Product.objects.get(id=item['product_id'])
                        
                        # Validar stock disponible
                        if product.stock < item['quantity']:
                            return Response(
                                {
                                    'success': False,
                                    'error': f'Stock insuficiente para "{product.name}". Stock disponible: {product.stock}',
                                    'prompt': prompt
                                },
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        
                        # Agregar información del producto
                        items_data.append({
                            'product_id': product.id,
                            'name': product.name,
                            'description': product.description,
                            'price': str(product.price),
                            'quantity': item['quantity'],
                            'subtotal': str(product.price * item['quantity']),
                            'stock_available': product.stock,
                            'image_url': product.image_url if hasattr(product, 'image_url') else None
                        })
                        
                        total_price += product.price * item['quantity']
                    
                    except Product.DoesNotExist:
                        return Response(
                            {
                                'success': False,
                                'error': f'Producto con ID {item["product_id"]} no encontrado',
                                'prompt': prompt
                            },
                            status=status.HTTP_404_NOT_FOUND
                        )
                
                # Devolver productos para que el frontend los agregue al carrito
                return Response(
                    {
                        'success': True,
                        'message': f'Se encontraron {len(items_data)} producto(s) para agregar al carrito',
                        'prompt': prompt,
                        'interpreted_action': result['action'],
                        'items': items_data,
                        'total': str(total_price),
                        'cart_action': 'add_to_cart'  # Indica al frontend que agregue al carrito
                    },
                    status=status.HTTP_200_OK
                )
            
            except Exception as e:
                return Response(
                    {
                        'success': False,
                        'error': f'Error al procesar la solicitud: {str(e)}',
                        'prompt': prompt
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
    serializer_class = ProductSuggestionsResponseSerializer
    
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

