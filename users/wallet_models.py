"""
Modelos para el sistema de billetera virtual.

Este módulo maneja:
- Saldo de billetera de usuarios
- Historial de transacciones
- Reembolsos automáticos
- Retiros y depósitos
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class Wallet(models.Model):
    """
    Billetera virtual del usuario.
    Cada usuario tiene UNA billetera con su saldo.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet',
        help_text="Usuario dueño de la billetera"
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Saldo actual en la billetera"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Si la billetera está activa"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Billetera'
        verbose_name_plural = 'Billeteras'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Billetera de {self.user.username} - ${self.balance}"
    
    def add_funds(self, amount, transaction_type, description='', reference_id=None):
        """
        Agregar fondos a la billetera.
        
        Args:
            amount: Monto a agregar
            transaction_type: Tipo de transacción
            description: Descripción opcional
            reference_id: ID de referencia (ej: Return ID)
        
        Returns:
            WalletTransaction: La transacción creada
        """
        if amount <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        
        # Actualizar saldo
        self.balance += Decimal(str(amount))
        self.save()
        
        # Crear transacción
        transaction = WalletTransaction.objects.create(
            wallet=self,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=self.balance,
            description=description,
            reference_id=reference_id
        )
        
        return transaction
    
    def deduct_funds(self, amount, transaction_type, description='', reference_id=None):
        """
        Deducir fondos de la billetera.
        
        Args:
            amount: Monto a deducir
            transaction_type: Tipo de transacción
            description: Descripción opcional
            reference_id: ID de referencia
        
        Returns:
            WalletTransaction: La transacción creada
        
        Raises:
            ValueError: Si no hay fondos suficientes
        """
        if amount <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        
        if self.balance < Decimal(str(amount)):
            raise ValueError(f"Fondos insuficientes. Saldo actual: ${self.balance}")
        
        # Actualizar saldo
        self.balance -= Decimal(str(amount))
        self.save()
        
        # Crear transacción
        transaction = WalletTransaction.objects.create(
            wallet=self,
            transaction_type=transaction_type,
            amount=-amount,  # Negativo para indicar deducción
            balance_after=self.balance,
            description=description,
            reference_id=reference_id
        )
        
        return transaction


class WalletTransaction(models.Model):
    """
    Transacción de billetera.
    Registro de todos los movimientos (créditos y débitos).
    """
    
    class TransactionType(models.TextChoices):
        REFUND = 'REFUND', 'Reembolso de devolución'
        PURCHASE = 'PURCHASE', 'Compra con billetera'
        WITHDRAWAL = 'WITHDRAWAL', 'Retiro de fondos'
        DEPOSIT = 'DEPOSIT', 'Depósito manual'
        BONUS = 'BONUS', 'Bono o promoción'
        CORRECTION = 'CORRECTION', 'Corrección de saldo'
    
    class TransactionStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        COMPLETED = 'COMPLETED', 'Completada'
        FAILED = 'FAILED', 'Fallida'
        REVERSED = 'REVERSED', 'Revertida'
    
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions',
        help_text="Billetera asociada"
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        help_text="Tipo de transacción"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Monto (positivo=crédito, negativo=débito)"
    )
    balance_after = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Saldo después de la transacción"
    )
    status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.COMPLETED,
        help_text="Estado de la transacción"
    )
    description = models.TextField(
        blank=True,
        help_text="Descripción de la transacción"
    )
    reference_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="ID de referencia (ej: Return ID, Order ID)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Transacción de Billetera'
        verbose_name_plural = 'Transacciones de Billetera'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['wallet', '-created_at']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['reference_id']),
        ]
    
    def __str__(self):
        sign = '+' if self.amount >= 0 else ''
        return f"{self.wallet.user.username} - {sign}${self.amount} ({self.get_transaction_type_display()})"
    
    @property
    def is_credit(self):
        """Retorna True si es un crédito (dinero entrante)"""
        return self.amount > 0
    
    @property
    def is_debit(self):
        """Retorna True si es un débito (dinero saliente)"""
        return self.amount < 0
