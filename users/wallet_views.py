"""
Vistas para el sistema de billetera virtual.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .wallet_models import Wallet, WalletTransaction
from .wallet_serializers import (
    WalletSerializer,
    WalletTransactionSerializer,
    WalletDepositSerializer,
    WalletWithdrawalSerializer
)
from .permissions import IsAdminOrManager


class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para gestionar billeteras.
    
    - Usuarios: Solo pueden ver su propia billetera
    - Managers/Admins: Pueden ver todas las billeteras
    """
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['balance', 'created_at']
    ordering = ['-balance']
    
    def get_queryset(self):
        """
        Filtrar billeteras según el rol del usuario.
        """
        user = self.request.user
        
        # Base queryset
        queryset = Wallet.objects.select_related('user').prefetch_related('transactions').all()
        
        # Si es usuario normal, solo ver su billetera
        if user.role not in ['MANAGER', 'ADMIN']:
            queryset = queryset.filter(user=user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_wallet(self, request):
        """
        Obtener la billetera del usuario autenticado.
        Si no existe, se crea automáticamente.
        """
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        
        if created:
            print(f"✅ Billetera creada para {request.user.username}")
        
        serializer = self.get_serializer(wallet)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_balance(self, request):
        """Obtener solo el saldo del usuario"""
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        
        return Response({
            'balance': str(wallet.balance),
            'is_active': wallet.is_active,
            'wallet_id': wallet.id
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsAdminOrManager])
    def deposit(self, request):
        """
        Realizar un depósito manual a una billetera.
        Solo managers/admins.
        """
        serializer = WalletDepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Obtener usuario objetivo
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'Debe proporcionar user_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener o crear billetera
        wallet, created = Wallet.objects.get_or_create(user=target_user)
        
        # Agregar fondos
        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', 'Depósito manual')
        
        try:
            transaction = wallet.add_funds(
                amount=amount,
                transaction_type=WalletTransaction.TransactionType.DEPOSIT,
                description=description
            )
            
            return Response({
                'message': f'Depósito de ${amount} realizado exitosamente',
                'wallet': WalletSerializer(wallet).data,
                'transaction': WalletTransactionSerializer(transaction).data
            })
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def withdraw(self, request):
        """
        Realizar un retiro de la billetera del usuario.
        """
        serializer = WalletWithdrawalSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        try:
            wallet = request.user.wallet
        except Wallet.DoesNotExist:
            return Response(
                {'error': 'No tienes una billetera activa'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', 'Retiro de fondos')
        
        try:
            transaction = wallet.deduct_funds(
                amount=amount,
                transaction_type=WalletTransaction.TransactionType.WITHDRAWAL,
                description=description
            )
            
            return Response({
                'message': f'Retiro de ${amount} procesado exitosamente',
                'wallet': WalletSerializer(wallet).data,
                'transaction': WalletTransactionSerializer(transaction).data
            })
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class WalletTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar transacciones de billetera.
    
    - Usuarios: Solo ven sus propias transacciones
    - Managers/Admins: Ven todas las transacciones
    """
    serializer_class = WalletTransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['transaction_type', 'status']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Filtrar transacciones según el rol del usuario.
        """
        user = self.request.user
        
        # Base queryset
        queryset = WalletTransaction.objects.select_related('wallet', 'wallet__user').all()
        
        # Si es usuario normal, solo ver sus transacciones
        if user.role not in ['MANAGER', 'ADMIN']:
            try:
                wallet = user.wallet
                queryset = queryset.filter(wallet=wallet)
            except Wallet.DoesNotExist:
                return queryset.none()
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_transactions(self, request):
        """
        Obtener las transacciones del usuario autenticado.
        """
        try:
            wallet = request.user.wallet
        except Wallet.DoesNotExist:
            return Response([])
        
        queryset = self.get_queryset().filter(wallet=wallet)
        
        # Filtrar por tipo si se proporciona
        transaction_type = request.query_params.get('type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Obtener estadísticas de transacciones del usuario.
        """
        try:
            wallet = request.user.wallet
        except Wallet.DoesNotExist:
            return Response({
                'total_credits': '0.00',
                'total_debits': '0.00',
                'total_refunds': '0.00',
                'transaction_count': 0
            })
        
        transactions = wallet.transactions.all()
        
        # Calcular estadísticas
        credits = transactions.filter(amount__gt=0).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        debits = transactions.filter(amount__lt=0).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        refunds = transactions.filter(
            transaction_type=WalletTransaction.TransactionType.REFUND
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        return Response({
            'current_balance': str(wallet.balance),
            'total_credits': str(credits),
            'total_debits': str(abs(debits)),
            'total_refunds': str(refunds),
            'transaction_count': transactions.count()
        })
