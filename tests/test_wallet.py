"""
Tests unitarios para el sistema de billetera virtual
Tests de operaciones: consulta, depósito, retiro, transacciones, estadísticas
"""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.core.exceptions import ValidationError

from users.wallet_models import Wallet, WalletTransaction

User = get_user_model()


@pytest.fixture
def api_client():
    """Cliente de API para requests"""
    return APIClient()


@pytest.fixture
def admin_user(db):
    """Crea usuario admin"""
    return User.objects.create_user(
        username='admin_wallet',
        email='admin@wallet.com',
        password='admin123',
        role='ADMIN'
    )


@pytest.fixture
def manager_user(db):
    """Crea usuario manager"""
    return User.objects.create_user(
        username='manager_wallet',
        email='manager@wallet.com',
        password='manager123',
        role='MANAGER'
    )


@pytest.fixture
def client_user(db):
    """Crea usuario cliente"""
    return User.objects.create_user(
        username='client_wallet',
        email='client@wallet.com',
        password='client123',
        role='CLIENTE'
    )


@pytest.fixture
def wallet_with_balance(db, client_user):
    """Crea billetera con saldo inicial"""
    wallet = Wallet.objects.create(
        user=client_user,
        balance=Decimal('500.00')
    )
    return wallet


@pytest.mark.django_db
class TestWalletCreation:
    """Tests para creación de billeteras"""

    def test_wallet_created_automatically(self, api_client, client_user):
        """Billetera se crea automáticamente al consultarla"""
        api_client.force_authenticate(user=client_user)
        
        # Verificar que no existe
        assert not Wallet.objects.filter(user=client_user).exists()
        
        # Consultar mi billetera
        response = api_client.get('/api/users/wallets/my_wallet/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['balance'] == '0.00'
        
        # Verificar que se creó
        assert Wallet.objects.filter(user=client_user).exists()

    def test_only_one_wallet_per_user(self, db, client_user):
        """Solo puede existir una billetera por usuario"""
        # Crear primera billetera
        wallet1 = Wallet.objects.create(user=client_user)
        
        # Intentar crear segunda billetera debe fallar
        with pytest.raises(Exception):  # Violación de unique constraint
            Wallet.objects.create(user=client_user)

    def test_wallet_balance_cannot_be_negative(self, db, client_user):
        """Balance de billetera no puede ser negativo"""
        wallet = Wallet.objects.create(user=client_user)
        wallet.balance = Decimal('-10.00')
        
        # Debe fallar la validación
        with pytest.raises(ValidationError):
            wallet.full_clean()


@pytest.mark.django_db
class TestWalletQueries:
    """Tests para consultas de billetera"""

    def test_user_can_view_own_wallet(self, api_client, client_user, wallet_with_balance):
        """Usuario puede ver su propia billetera"""
        api_client.force_authenticate(user=client_user)
        
        response = api_client.get('/api/users/wallets/my_wallet/')
        
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data['balance']) == Decimal('500.00')
        assert response.data['user'] == client_user.id

    def test_user_can_view_own_balance(self, api_client, client_user, wallet_with_balance):
        """Usuario puede consultar su saldo"""
        api_client.force_authenticate(user=client_user)
        
        response = api_client.get('/api/users/wallets/my_balance/')
        
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data['balance']) == Decimal('500.00')

    def test_user_cannot_view_others_wallet(self, api_client, client_user):
        """Usuario no puede ver billetera de otro usuario"""
        # Crear otro usuario con billetera
        other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='pass123'
        )
        other_wallet = Wallet.objects.create(
            user=other_user,
            balance=Decimal('1000.00')
        )
        
        api_client.force_authenticate(user=client_user)
        
        # Intentar acceder a billetera de otro usuario
        response = api_client.get(f'/api/users/wallets/{other_wallet.id}/')
        
        # Debe retornar 404 o no incluir en queryset
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]


@pytest.mark.django_db
class TestWalletDeposit:
    """Tests para depósitos en billetera"""

    def test_manager_can_deposit_funds(self, api_client, manager_user, client_user):
        """Manager puede depositar fondos a billetera de usuario"""
        wallet = Wallet.objects.create(user=client_user)
        
        api_client.force_authenticate(user=manager_user)
        
        data = {
            'amount': '250.00',
            'description': 'Bonificación por promoción'
        }
        
        response = api_client.post(f'/api/users/wallets/{wallet.id}/deposit/', data)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar saldo actualizado
        wallet.refresh_from_db()
        assert wallet.balance == Decimal('250.00')

    def test_deposit_creates_transaction(self, api_client, manager_user, client_user):
        """Depósito crea transacción en historial"""
        wallet = Wallet.objects.create(user=client_user)
        
        api_client.force_authenticate(user=manager_user)
        
        data = {
            'amount': '100.00',
            'description': 'Crédito de prueba'
        }
        
        response = api_client.post(f'/api/users/wallets/{wallet.id}/deposit/', data)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar transacción creada
        transaction = WalletTransaction.objects.filter(
            wallet=wallet,
            transaction_type='DEPOSIT'
        ).first()
        
        assert transaction is not None
        assert transaction.amount == Decimal('100.00')
        assert transaction.balance_after == Decimal('100.00')
        assert 'Crédito de prueba' in transaction.description

    def test_client_cannot_deposit(self, api_client, client_user):
        """Cliente no puede depositar (solo managers)"""
        wallet = Wallet.objects.create(user=client_user)
        
        api_client.force_authenticate(user=client_user)
        
        data = {
            'amount': '100.00',
            'description': 'Test'
        }
        
        response = api_client.post(f'/api/users/wallets/{wallet.id}/deposit/', data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_deposit_negative_amount(self, api_client, manager_user, client_user):
        """No se puede depositar cantidad negativa"""
        wallet = Wallet.objects.create(user=client_user)
        
        api_client.force_authenticate(user=manager_user)
        
        data = {
            'amount': '-50.00',
            'description': 'Test'
        }
        
        response = api_client.post(f'/api/users/wallets/{wallet.id}/deposit/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestWalletWithdrawal:
    """Tests para retiros de billetera"""

    def test_user_can_withdraw_funds(self, api_client, client_user, wallet_with_balance):
        """Usuario puede retirar fondos de su billetera"""
        api_client.force_authenticate(user=client_user)
        
        data = {
            'amount': '200.00',
            'description': 'Retiro a cuenta bancaria'
        }
        
        response = api_client.post(f'/api/users/wallets/{wallet_with_balance.id}/withdraw/', data)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar saldo actualizado (500 - 200 = 300)
        wallet_with_balance.refresh_from_db()
        assert wallet_with_balance.balance == Decimal('300.00')

    def test_withdrawal_creates_transaction(self, api_client, client_user, wallet_with_balance):
        """Retiro crea transacción negativa en historial"""
        api_client.force_authenticate(user=client_user)
        
        data = {
            'amount': '100.00',
            'description': 'Retiro de prueba'
        }
        
        response = api_client.post(f'/api/users/wallets/{wallet_with_balance.id}/withdraw/', data)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar transacción creada
        transaction = WalletTransaction.objects.filter(
            wallet=wallet_with_balance,
            transaction_type='WITHDRAWAL'
        ).first()
        
        assert transaction is not None
        assert transaction.amount == Decimal('-100.00')  # Negativo
        assert transaction.balance_after == Decimal('400.00')

    def test_cannot_withdraw_more_than_balance(self, api_client, client_user, wallet_with_balance):
        """No se puede retirar más del saldo disponible"""
        api_client.force_authenticate(user=client_user)
        
        # Intentar retirar más de 500.00
        data = {
            'amount': '1000.00',
            'description': 'Retiro excesivo'
        }
        
        response = api_client.post(f'/api/users/wallets/{wallet_with_balance.id}/withdraw/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'insuficiente' in str(response.data).lower()

    def test_cannot_withdraw_from_others_wallet(self, api_client, client_user):
        """Usuario no puede retirar de billetera ajena"""
        # Crear otro usuario con billetera
        other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='pass123'
        )
        other_wallet = Wallet.objects.create(
            user=other_user,
            balance=Decimal('1000.00')
        )
        
        api_client.force_authenticate(user=client_user)
        
        data = {
            'amount': '100.00',
            'description': 'Test'
        }
        
        response = api_client.post(f'/api/users/wallets/{other_wallet.id}/withdraw/', data)
        
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]


@pytest.mark.django_db
class TestWalletTransactions:
    """Tests para transacciones y historial"""

    def test_user_can_view_own_transactions(self, api_client, client_user, wallet_with_balance):
        """Usuario puede ver su historial de transacciones"""
        # Crear algunas transacciones
        WalletTransaction.objects.create(
            wallet=wallet_with_balance,
            transaction_type='REFUND',
            amount=Decimal('500.00'),
            balance_after=Decimal('500.00'),
            description='Reembolso inicial'
        )
        WalletTransaction.objects.create(
            wallet=wallet_with_balance,
            transaction_type='PURCHASE',
            amount=Decimal('-100.00'),
            balance_after=Decimal('400.00'),
            description='Compra de producto'
        )
        
        api_client.force_authenticate(user=client_user)
        
        response = api_client.get('/api/users/wallet-transactions/my_transactions/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_transactions_ordered_by_date_desc(self, api_client, client_user, wallet_with_balance):
        """Transacciones ordenadas por fecha descendente (más reciente primero)"""
        # Crear transacciones
        tx1 = WalletTransaction.objects.create(
            wallet=wallet_with_balance,
            transaction_type='DEPOSIT',
            amount=Decimal('100.00'),
            balance_after=Decimal('100.00'),
            description='Primera'
        )
        tx2 = WalletTransaction.objects.create(
            wallet=wallet_with_balance,
            transaction_type='DEPOSIT',
            amount=Decimal('50.00'),
            balance_after=Decimal('150.00'),
            description='Segunda'
        )
        
        api_client.force_authenticate(user=client_user)
        
        response = api_client.get('/api/users/wallet-transactions/my_transactions/')
        
        assert response.status_code == status.HTTP_200_OK
        # La más reciente (tx2) debe aparecer primero
        assert response.data[0]['description'] == 'Segunda'

    def test_user_cannot_view_others_transactions(self, api_client, client_user):
        """Usuario no puede ver transacciones de otros"""
        # Crear otro usuario con transacciones
        other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='pass123'
        )
        other_wallet = Wallet.objects.create(user=other_user)
        WalletTransaction.objects.create(
            wallet=other_wallet,
            transaction_type='DEPOSIT',
            amount=Decimal('1000.00'),
            balance_after=Decimal('1000.00'),
            description='No debería verse'
        )
        
        api_client.force_authenticate(user=client_user)
        
        response = api_client.get('/api/users/wallet-transactions/my_transactions/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0  # No debe ver transacciones ajenas


@pytest.mark.django_db
class TestWalletStatistics:
    """Tests para estadísticas de billetera"""

    def test_statistics_calculation(self, api_client, client_user, wallet_with_balance):
        """Estadísticas calculan correctamente créditos, débitos y reembolsos"""
        # Crear transacciones variadas
        WalletTransaction.objects.create(
            wallet=wallet_with_balance,
            transaction_type='REFUND',
            amount=Decimal('300.00'),
            balance_after=Decimal('300.00'),
            description='Reembolso 1'
        )
        WalletTransaction.objects.create(
            wallet=wallet_with_balance,
            transaction_type='REFUND',
            amount=Decimal('200.00'),
            balance_after=Decimal('500.00'),
            description='Reembolso 2'
        )
        WalletTransaction.objects.create(
            wallet=wallet_with_balance,
            transaction_type='PURCHASE',
            amount=Decimal('-150.00'),
            balance_after=Decimal('350.00'),
            description='Compra 1'
        )
        WalletTransaction.objects.create(
            wallet=wallet_with_balance,
            transaction_type='WITHDRAWAL',
            amount=Decimal('-50.00'),
            balance_after=Decimal('300.00'),
            description='Retiro 1'
        )
        
        api_client.force_authenticate(user=client_user)
        
        response = api_client.get('/api/users/wallet-transactions/statistics/')
        
        assert response.status_code == status.HTTP_200_OK
        
        stats = response.data
        
        # Total créditos (REFUND + DEPOSIT positivos)
        assert Decimal(stats['total_credits']) == Decimal('500.00')
        
        # Total débitos (negativos)
        assert Decimal(stats['total_debits']) == Decimal('-200.00')
        
        # Total reembolsos
        assert Decimal(stats['total_refunds']) == Decimal('500.00')
        
        # Número de transacciones
        assert stats['transaction_count'] == 4

    def test_statistics_with_no_transactions(self, api_client, client_user):
        """Estadísticas con billetera vacía retorna ceros"""
        Wallet.objects.create(user=client_user)
        
        api_client.force_authenticate(user=client_user)
        
        response = api_client.get('/api/users/wallet-transactions/statistics/')
        
        assert response.status_code == status.HTTP_200_OK
        
        stats = response.data
        assert Decimal(stats['total_credits']) == Decimal('0.00')
        assert Decimal(stats['total_debits']) == Decimal('0.00')
        assert Decimal(stats['total_refunds']) == Decimal('0.00')
        assert stats['transaction_count'] == 0


@pytest.mark.django_db
class TestWalletAddFundsMethod:
    """Tests para método add_funds() del modelo Wallet"""

    def test_add_funds_increases_balance(self, db, client_user):
        """add_funds() incrementa el saldo correctamente"""
        wallet = Wallet.objects.create(
            user=client_user,
            balance=Decimal('100.00')
        )
        
        wallet.add_funds(
            amount=Decimal('50.00'),
            transaction_type='DEPOSIT',
            description='Test deposit'
        )
        
        wallet.refresh_from_db()
        assert wallet.balance == Decimal('150.00')

    def test_add_funds_creates_transaction(self, db, client_user):
        """add_funds() crea registro de transacción"""
        wallet = Wallet.objects.create(user=client_user)
        
        wallet.add_funds(
            amount=Decimal('200.00'),
            transaction_type='REFUND',
            description='Refund test',
            reference_id='RETURN-123'
        )
        
        transaction = WalletTransaction.objects.filter(wallet=wallet).first()
        
        assert transaction is not None
        assert transaction.amount == Decimal('200.00')
        assert transaction.transaction_type == 'REFUND'
        assert transaction.reference_id == 'RETURN-123'
        assert transaction.balance_after == Decimal('200.00')


@pytest.mark.django_db
class TestWalletDeductFundsMethod:
    """Tests para método deduct_funds() del modelo Wallet"""

    def test_deduct_funds_decreases_balance(self, db, client_user):
        """deduct_funds() decrementa el saldo correctamente"""
        wallet = Wallet.objects.create(
            user=client_user,
            balance=Decimal('100.00')
        )
        
        wallet.deduct_funds(
            amount=Decimal('30.00'),
            transaction_type='PURCHASE',
            description='Test purchase'
        )
        
        wallet.refresh_from_db()
        assert wallet.balance == Decimal('70.00')

    def test_deduct_funds_with_insufficient_balance_raises_error(self, db, client_user):
        """deduct_funds() con saldo insuficiente genera error"""
        wallet = Wallet.objects.create(
            user=client_user,
            balance=Decimal('50.00')
        )
        
        with pytest.raises(ValidationError) as exc_info:
            wallet.deduct_funds(
                amount=Decimal('100.00'),
                transaction_type='PURCHASE',
                description='Test'
            )
        
        assert 'Saldo insuficiente' in str(exc_info.value)

    def test_deduct_funds_creates_negative_transaction(self, db, client_user):
        """deduct_funds() crea transacción con monto negativo"""
        wallet = Wallet.objects.create(
            user=client_user,
            balance=Decimal('100.00')
        )
        
        wallet.deduct_funds(
            amount=Decimal('25.00'),
            transaction_type='WITHDRAWAL',
            description='Withdrawal test'
        )
        
        transaction = WalletTransaction.objects.filter(wallet=wallet).first()
        
        assert transaction is not None
        assert transaction.amount == Decimal('-25.00')  # Negativo
        assert transaction.balance_after == Decimal('75.00')
