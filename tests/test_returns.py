"""
Tests unitarios para el sistema de devoluciones
Tests completos del flujo: REQUESTED → IN_EVALUATION → APPROVED/REJECTED → COMPLETED
"""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.core import mail

from products.models import Product, Category
from shop_orders.models import Order, OrderItem
from deliveries.models import Return
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
        username='admin_test',
        email='admin@test.com',
        password='admin123',
        role='ADMIN'
    )


@pytest.fixture
def manager_user(db):
    """Crea usuario manager"""
    return User.objects.create_user(
        username='manager_test',
        email='manager@test.com',
        password='manager123',
        role='MANAGER'
    )


@pytest.fixture
def client_user(db):
    """Crea usuario cliente"""
    return User.objects.create_user(
        username='client_test',
        email='client@test.com',
        password='client123',
        role='CLIENTE'
    )


@pytest.fixture
def category(db):
    """Crea categoría de prueba"""
    return Category.objects.create(
        name='Electrónica',
        description='Productos electrónicos'
    )


@pytest.fixture
def product(db, category):
    """Crea producto de prueba"""
    return Product.objects.create(
        name='Laptop Test',
        description='Laptop para testing',
        price=Decimal('999.99'),
        stock=100,
        category=category,
        warranty_info='1 año'
    )


@pytest.fixture
def delivered_order(db, client_user, product):
    """Crea orden entregada con producto"""
    order = Order.objects.create(
        user=client_user,
        status='DELIVERED',
        total_price=Decimal('999.99')
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price
    )
    return order


@pytest.mark.django_db
class TestReturnCreation:
    """Tests para creación de devoluciones"""

    def test_client_can_create_return(self, api_client, client_user, delivered_order, product):
        """Cliente puede crear solicitud de devolución"""
        api_client.force_authenticate(user=client_user)
        
        data = {
            'order': delivered_order.id,
            'product': product.id,
            'quantity': 1,
            'reason': 'Producto defectuoso'
        }
        
        response = api_client.post('/api/deliveries/returns/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'REQUESTED'
        assert response.data['reason'] == 'Producto defectuoso'
        assert response.data['user'] == client_user.id
        
        # Verificar que se creó en BD
        assert Return.objects.filter(order=delivered_order).exists()

    def test_cannot_create_return_for_non_delivered_order(self, api_client, client_user, product, category):
        """No se puede crear devolución de orden no entregada"""
        api_client.force_authenticate(user=client_user)
        
        # Crear orden en estado PENDING
        order = Order.objects.create(
            user=client_user,
            status='PENDING',
            total_price=Decimal('999.99')
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            price=product.price
        )
        
        data = {
            'order': order.id,
            'product': product.id,
            'quantity': 1,
            'reason': 'Test'
        }
        
        response = api_client.post('/api/deliveries/returns/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'debe estar en estado DELIVERED' in str(response.data)

    def test_cannot_create_return_with_invalid_quantity(self, api_client, client_user, delivered_order, product):
        """No se puede devolver más cantidad de la comprada"""
        api_client.force_authenticate(user=client_user)
        
        data = {
            'order': delivered_order.id,
            'product': product.id,
            'quantity': 10,  # Solo se compraron 1
            'reason': 'Test'
        }
        
        response = api_client.post('/api/deliveries/returns/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_email_sent_to_managers_on_return_creation(self, api_client, client_user, manager_user, 
                                                        admin_user, delivered_order, product):
        """Se envía email a managers al crear devolución"""
        api_client.force_authenticate(user=client_user)
        
        data = {
            'order': delivered_order.id,
            'product': product.id,
            'quantity': 1,
            'reason': 'Producto defectuoso'
        }
        
        # Limpiar bandeja de emails
        mail.outbox = []
        
        response = api_client.post('/api/deliveries/returns/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verificar que se enviaron emails (2: manager + admin)
        assert len(mail.outbox) >= 1
        
        # Verificar que el subject contiene "Return"
        assert 'Return' in mail.outbox[0].subject or 'Devolución' in mail.outbox[0].subject


@pytest.mark.django_db
class TestReturnEvaluation:
    """Tests para enviar devolución a evaluación"""

    def test_manager_can_send_to_evaluation(self, api_client, manager_user, client_user, 
                                             delivered_order, product):
        """Manager puede enviar devolución a evaluación"""
        # Crear devolución
        return_obj = Return.objects.create(
            user=client_user,
            order=delivered_order,
            product=product,
            quantity=1,
            reason='Test',
            status='REQUESTED'
        )
        
        api_client.force_authenticate(user=manager_user)
        
        data = {
            'manager_notes': 'Producto recibido en bodega'
        }
        
        response = api_client.post(f'/api/deliveries/returns/{return_obj.id}/send_to_evaluation/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'IN_EVALUATION'
        assert response.data['manager_notes'] == 'Producto recibido en bodega'
        
        # Verificar en BD
        return_obj.refresh_from_db()
        assert return_obj.status == 'IN_EVALUATION'
        assert return_obj.evaluated_at is not None

    def test_client_cannot_send_to_evaluation(self, api_client, client_user, delivered_order, product):
        """Cliente no puede enviar a evaluación"""
        return_obj = Return.objects.create(
            user=client_user,
            order=delivered_order,
            product=product,
            quantity=1,
            reason='Test',
            status='REQUESTED'
        )
        
        api_client.force_authenticate(user=client_user)
        
        data = {'manager_notes': 'Test'}
        
        response = api_client.post(f'/api/deliveries/returns/{return_obj.id}/send_to_evaluation/', data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestReturnApproval:
    """Tests para aprobación de devoluciones"""

    def test_manager_can_approve_return(self, api_client, manager_user, client_user, 
                                        delivered_order, product):
        """Manager puede aprobar devolución"""
        return_obj = Return.objects.create(
            user=client_user,
            order=delivered_order,
            product=product,
            quantity=1,
            reason='Defectuoso',
            status='IN_EVALUATION'
        )
        
        api_client.force_authenticate(user=manager_user)
        
        data = {
            'evaluation_notes': 'Producto confirmado defectuoso',
            'refund_amount': '999.99',
            'refund_method': 'WALLET'
        }
        
        response = api_client.post(f'/api/deliveries/returns/{return_obj.id}/approve/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'COMPLETED'
        assert response.data['refund_method'] == 'WALLET'
        
        # Verificar en BD
        return_obj.refresh_from_db()
        assert return_obj.status == 'COMPLETED'
        assert return_obj.refund_amount == Decimal('999.99')
        assert return_obj.completed_at is not None

    def test_approval_creates_wallet_and_adds_funds(self, api_client, manager_user, client_user,
                                                     delivered_order, product):
        """Aprobar devolución crea billetera y agrega fondos"""
        return_obj = Return.objects.create(
            user=client_user,
            order=delivered_order,
            product=product,
            quantity=1,
            reason='Defectuoso',
            status='IN_EVALUATION'
        )
        
        api_client.force_authenticate(user=manager_user)
        
        # Verificar que no existe billetera
        assert not Wallet.objects.filter(user=client_user).exists()
        
        data = {
            'evaluation_notes': 'Aprobado',
            'refund_amount': '500.00',
            'refund_method': 'WALLET'
        }
        
        response = api_client.post(f'/api/deliveries/returns/{return_obj.id}/approve/', data)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar que se creó billetera
        wallet = Wallet.objects.get(user=client_user)
        assert wallet.balance == Decimal('500.00')
        
        # Verificar que se creó transacción
        transaction = WalletTransaction.objects.filter(wallet=wallet).first()
        assert transaction is not None
        assert transaction.transaction_type == 'REFUND'
        assert transaction.amount == Decimal('500.00')
        assert f'RETURN-{return_obj.id}' in transaction.reference_id

    def test_approval_sends_email_to_client(self, api_client, manager_user, client_user,
                                            delivered_order, product):
        """Aprobar devolución envía email al cliente"""
        return_obj = Return.objects.create(
            user=client_user,
            order=delivered_order,
            product=product,
            quantity=1,
            reason='Defectuoso',
            status='IN_EVALUATION'
        )
        
        api_client.force_authenticate(user=manager_user)
        
        mail.outbox = []
        
        data = {
            'evaluation_notes': 'Aprobado',
            'refund_amount': '500.00',
            'refund_method': 'WALLET'
        }
        
        response = api_client.post(f'/api/deliveries/returns/{return_obj.id}/approve/', data)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar email enviado
        assert len(mail.outbox) >= 1
        assert client_user.email in mail.outbox[0].to


@pytest.mark.django_db
class TestReturnRejection:
    """Tests para rechazo de devoluciones"""

    def test_manager_can_reject_return(self, api_client, manager_user, client_user,
                                       delivered_order, product):
        """Manager puede rechazar devolución"""
        return_obj = Return.objects.create(
            user=client_user,
            order=delivered_order,
            product=product,
            quantity=1,
            reason='Defectuoso',
            status='IN_EVALUATION'
        )
        
        api_client.force_authenticate(user=manager_user)
        
        data = {
            'evaluation_notes': 'Producto no presenta defectos. Daño por mal uso.'
        }
        
        response = api_client.post(f'/api/deliveries/returns/{return_obj.id}/reject/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'REJECTED'
        
        # Verificar en BD
        return_obj.refresh_from_db()
        assert return_obj.status == 'REJECTED'
        assert return_obj.processed_at is not None

    def test_rejection_does_not_create_wallet(self, api_client, manager_user, client_user,
                                              delivered_order, product):
        """Rechazar devolución NO crea billetera ni fondos"""
        return_obj = Return.objects.create(
            user=client_user,
            order=delivered_order,
            product=product,
            quantity=1,
            reason='Defectuoso',
            status='IN_EVALUATION'
        )
        
        api_client.force_authenticate(user=manager_user)
        
        data = {
            'evaluation_notes': 'Rechazado'
        }
        
        response = api_client.post(f'/api/deliveries/returns/{return_obj.id}/reject/', data)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar que NO se creó billetera
        assert not Wallet.objects.filter(user=client_user).exists()


@pytest.mark.django_db
class TestReturnQueries:
    """Tests para consultas de devoluciones"""

    def test_client_can_view_own_returns(self, api_client, client_user, delivered_order, product):
        """Cliente puede ver sus propias devoluciones"""
        # Crear devolución
        Return.objects.create(
            user=client_user,
            order=delivered_order,
            product=product,
            quantity=1,
            reason='Test',
            status='REQUESTED'
        )
        
        api_client.force_authenticate(user=client_user)
        
        response = api_client.get('/api/deliveries/returns/my_returns/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['reason'] == 'Test'

    def test_client_cannot_view_others_returns(self, api_client, client_user):
        """Cliente solo ve sus propias devoluciones"""
        # Crear otro usuario y su devolución
        other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='pass123'
        )
        
        category = Category.objects.create(name='Test')
        product = Product.objects.create(
            name='Test',
            price=Decimal('100.00'),
            stock=10,
            category=category
        )
        
        order = Order.objects.create(
            user=other_user,
            status='DELIVERED',
            total_price=Decimal('100.00')
        )
        
        Return.objects.create(
            user=other_user,
            order=order,
            product=product,
            quantity=1,
            reason='Other user return',
            status='REQUESTED'
        )
        
        api_client.force_authenticate(user=client_user)
        
        response = api_client.get('/api/deliveries/returns/my_returns/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0  # No debe ver la devolución del otro usuario

    def test_manager_can_view_all_returns(self, api_client, manager_user, client_user,
                                          delivered_order, product):
        """Manager puede ver todas las devoluciones"""
        Return.objects.create(
            user=client_user,
            order=delivered_order,
            product=product,
            quantity=1,
            reason='Test',
            status='REQUESTED'
        )
        
        api_client.force_authenticate(user=manager_user)
        
        response = api_client.get('/api/deliveries/returns/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1


@pytest.mark.django_db
class TestReturnWorkflow:
    """Tests del flujo completo de devolución"""

    def test_complete_return_workflow(self, api_client, manager_user, client_user,
                                      delivered_order, product):
        """Test del flujo completo: REQUESTED → IN_EVALUATION → APPROVED → COMPLETED"""
        
        # 1. Cliente crea devolución
        api_client.force_authenticate(user=client_user)
        
        data = {
            'order': delivered_order.id,
            'product': product.id,
            'quantity': 1,
            'reason': 'Producto defectuoso'
        }
        
        response = api_client.post('/api/deliveries/returns/', data)
        assert response.status_code == status.HTTP_201_CREATED
        return_id = response.data['id']
        assert response.data['status'] == 'REQUESTED'
        
        # 2. Manager envía a evaluación
        api_client.force_authenticate(user=manager_user)
        
        response = api_client.post(
            f'/api/deliveries/returns/{return_id}/send_to_evaluation/',
            {'manager_notes': 'Recibido en bodega'}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'IN_EVALUATION'
        
        # 3. Manager aprueba
        response = api_client.post(
            f'/api/deliveries/returns/{return_id}/approve/',
            {
                'evaluation_notes': 'Aprobado',
                'refund_amount': '999.99',
                'refund_method': 'WALLET'
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'COMPLETED'
        
        # 4. Verificar billetera
        wallet = Wallet.objects.get(user=client_user)
        assert wallet.balance == Decimal('999.99')
        
        # 5. Verificar transacción
        transaction = WalletTransaction.objects.filter(
            wallet=wallet,
            transaction_type='REFUND'
        ).first()
        assert transaction is not None
        assert transaction.amount == Decimal('999.99')
