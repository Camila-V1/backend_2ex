"""
Serializers para el sistema de billetera virtual.
"""

from rest_framework import serializers
from .wallet_models import Wallet, WalletTransaction


class WalletTransactionSerializer(serializers.ModelSerializer):
    """Serializer para transacciones de billetera"""
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_credit = serializers.BooleanField(read_only=True)
    is_debit = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = WalletTransaction
        fields = [
            'id', 'transaction_type', 'transaction_type_display',
            'amount', 'balance_after', 'status', 'status_display',
            'description', 'reference_id', 'is_credit', 'is_debit',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'balance_after', 'created_at', 'updated_at']


class WalletSerializer(serializers.ModelSerializer):
    """Serializer para billetera"""
    user_details = serializers.SerializerMethodField()
    recent_transactions = serializers.SerializerMethodField()
    
    class Meta:
        model = Wallet
        fields = [
            'id', 'user', 'user_details', 'balance', 'is_active',
            'recent_transactions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'balance', 'created_at', 'updated_at']
    
    def get_user_details(self, obj):
        """Información básica del usuario"""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'full_name': obj.user.get_full_name()
        }
    
    def get_recent_transactions(self, obj):
        """Últimas 5 transacciones"""
        transactions = obj.transactions.all()[:5]
        return WalletTransactionSerializer(transactions, many=True).data


class WalletDepositSerializer(serializers.Serializer):
    """Serializer para depósitos manuales"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    description = serializers.CharField(required=False, allow_blank=True)
    
    def validate_amount(self, value):
        """Validar que el monto sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        return value


class WalletWithdrawalSerializer(serializers.Serializer):
    """Serializer para retiros"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    description = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validar que haya fondos suficientes"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            try:
                wallet = request.user.wallet
                if wallet.balance < data['amount']:
                    raise serializers.ValidationError({
                        'amount': f"Fondos insuficientes. Saldo actual: ${wallet.balance}"
                    })
            except Wallet.DoesNotExist:
                raise serializers.ValidationError("No tienes una billetera activa")
        
        return data
