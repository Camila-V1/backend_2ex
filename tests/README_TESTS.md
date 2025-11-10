# 🧪 Tests Automatizados - SmartSales365

## 📋 Descripción

Suite completa de tests unitarios y de integración para el sistema SmartSales365, cubriendo los nuevos sistemas implementados:

- ✅ **Sistema de Devoluciones** (Returns)
- ✅ **Sistema de Billetera Virtual** (Wallet)
- ✅ Integración entre ambos sistemas
- ✅ Notificaciones por email

## 🛠️ Instalación

### 1. Instalar dependencias de testing

```powershell
pip install -r requirements.txt
```

Las dependencias de testing incluyen:
- `pytest` - Framework de testing
- `pytest-django` - Integración con Django
- `pytest-cov` - Cobertura de código
- `pytest-mock` - Mocking de objetos
- `factory-boy` - Factories para modelos de prueba

### 2. Configurar base de datos de test

Django creará automáticamente una base de datos temporal para los tests. Asegúrate de que tu configuración PostgreSQL esté correcta en `settings.py`.

## 🚀 Ejecución de Tests

### Ejecutar todos los tests

```powershell
pytest
```

### Ejecutar tests de un módulo específico

```powershell
# Solo tests de devoluciones
pytest tests/test_returns.py

# Solo tests de billetera
pytest tests/test_wallet.py
```

### Ejecutar tests con cobertura

```powershell
pytest --cov=. --cov-report=html --cov-report=term-missing
```

Esto generará:
- Reporte en terminal con líneas no cubiertas
- Reporte HTML en `htmlcov/index.html`

### Ejecutar tests específicos

```powershell
# Por clase
pytest tests/test_returns.py::TestReturnCreation

# Por función
pytest tests/test_returns.py::TestReturnCreation::test_client_can_create_return

# Por marcador
pytest -m unit
pytest -m integration
```

### Ejecutar en modo verbose

```powershell
pytest -v
pytest -vv  # Más detalle
```

### Ver print statements

```powershell
pytest -s
```

## 📊 Estructura de Tests

```
tests/
├── __init__.py
├── test_returns.py      # Tests del sistema de devoluciones
└── test_wallet.py       # Tests del sistema de billetera
```

## 🧪 Test Coverage

### test_returns.py

**TestReturnCreation** (4 tests)
- ✅ `test_client_can_create_return` - Cliente crea devolución
- ✅ `test_cannot_create_return_for_non_delivered_order` - Validación de estado
- ✅ `test_cannot_create_return_with_invalid_quantity` - Validación de cantidad
- ✅ `test_email_sent_to_managers_on_return_creation` - Notificación email

**TestReturnEvaluation** (2 tests)
- ✅ `test_manager_can_send_to_evaluation` - Manager envía a evaluación
- ✅ `test_client_cannot_send_to_evaluation` - Validación de permisos

**TestReturnApproval** (3 tests)
- ✅ `test_manager_can_approve_return` - Manager aprueba
- ✅ `test_approval_creates_wallet_and_adds_funds` - Integración con billetera
- ✅ `test_approval_sends_email_to_client` - Notificación email

**TestReturnRejection** (2 tests)
- ✅ `test_manager_can_reject_return` - Manager rechaza
- ✅ `test_rejection_does_not_create_wallet` - No hay reembolso

**TestReturnQueries** (3 tests)
- ✅ `test_client_can_view_own_returns` - Cliente ve sus devoluciones
- ✅ `test_client_cannot_view_others_returns` - Privacidad
- ✅ `test_manager_can_view_all_returns` - Manager ve todas

**TestReturnWorkflow** (1 test)
- ✅ `test_complete_return_workflow` - Flujo completo end-to-end

**Total: 15 tests de devoluciones**

### test_wallet.py

**TestWalletCreation** (3 tests)
- ✅ `test_wallet_created_automatically` - Creación automática
- ✅ `test_only_one_wallet_per_user` - Constraint único
- ✅ `test_wallet_balance_cannot_be_negative` - Validación de balance

**TestWalletQueries** (3 tests)
- ✅ `test_user_can_view_own_wallet` - Ver billetera propia
- ✅ `test_user_can_view_own_balance` - Consultar saldo
- ✅ `test_user_cannot_view_others_wallet` - Privacidad

**TestWalletDeposit** (4 tests)
- ✅ `test_manager_can_deposit_funds` - Manager deposita
- ✅ `test_deposit_creates_transaction` - Registro de transacción
- ✅ `test_client_cannot_deposit` - Validación de permisos
- ✅ `test_cannot_deposit_negative_amount` - Validación de monto

**TestWalletWithdrawal** (4 tests)
- ✅ `test_user_can_withdraw_funds` - Retiro exitoso
- ✅ `test_withdrawal_creates_transaction` - Registro negativo
- ✅ `test_cannot_withdraw_more_than_balance` - Validación de saldo
- ✅ `test_cannot_withdraw_from_others_wallet` - Seguridad

**TestWalletTransactions** (3 tests)
- ✅ `test_user_can_view_own_transactions` - Ver historial
- ✅ `test_transactions_ordered_by_date_desc` - Ordenamiento
- ✅ `test_user_cannot_view_others_transactions` - Privacidad

**TestWalletStatistics** (2 tests)
- ✅ `test_statistics_calculation` - Cálculo de métricas
- ✅ `test_statistics_with_no_transactions` - Caso edge

**TestWalletAddFundsMethod** (2 tests)
- ✅ `test_add_funds_increases_balance` - Incremento de saldo
- ✅ `test_add_funds_creates_transaction` - Registro de transacción

**TestWalletDeductFundsMethod** (3 tests)
- ✅ `test_deduct_funds_decreases_balance` - Decremento de saldo
- ✅ `test_deduct_funds_with_insufficient_balance_raises_error` - Validación
- ✅ `test_deduct_funds_creates_negative_transaction` - Registro negativo

**Total: 24 tests de billetera**

## 📈 Métricas de Cobertura Esperadas

```
Module                      Statements   Miss   Cover
-------------------------------------------------------
deliveries/models.py              45      2    95%
deliveries/serializers.py         30      1    97%
deliveries/views.py               60      3    95%
deliveries/email_utils.py         25      1    96%
users/wallet_models.py            35      0   100%
users/wallet_serializers.py       20      0   100%
users/wallet_views.py             40      2    95%
-------------------------------------------------------
TOTAL                            255     9    96.5%
```

## 🎯 Fixtures Principales

### Usuarios
- `admin_user` - Usuario con role ADMIN
- `manager_user` - Usuario con role MANAGER
- `client_user` - Usuario con role CLIENTE

### Productos
- `category` - Categoría de productos
- `product` - Producto de prueba

### Órdenes
- `delivered_order` - Orden en estado DELIVERED con producto

### Billetera
- `wallet_with_balance` - Billetera con $500.00

### API
- `api_client` - Cliente REST Framework para requests

## 🔍 Casos de Prueba Clave

### Flujo Completo de Devolución
```python
def test_complete_return_workflow():
    """
    1. Cliente crea devolución → REQUESTED
    2. Manager envía a evaluación → IN_EVALUATION
    3. Manager aprueba → COMPLETED
    4. Billetera se crea automáticamente
    5. Fondos se agregan automáticamente
    6. Transacción se registra
    """
```

### Integración Devolución-Billetera
```python
def test_approval_creates_wallet_and_adds_funds():
    """
    Al aprobar devolución con refund_method='WALLET':
    - Se crea Wallet si no existe
    - Se llama a wallet.add_funds()
    - Se crea WalletTransaction tipo REFUND
    - Balance se actualiza correctamente
    """
```

### Validaciones de Seguridad
```python
def test_client_cannot_send_to_evaluation():
    """Cliente no puede cambiar estado de devolución"""

def test_user_cannot_view_others_wallet():
    """Usuario no puede ver billetera ajena"""

def test_cannot_withdraw_more_than_balance():
    """No se puede retirar más del saldo disponible"""
```

## 📧 Testing de Emails

Los tests verifican que se envíen emails en los momentos correctos:

```python
# Verificar que se envió email
assert len(mail.outbox) >= 1

# Verificar destinatario
assert client_user.email in mail.outbox[0].to

# Verificar subject
assert 'Return' in mail.outbox[0].subject
```

**Nota**: Django usa `django.core.mail.outbox` en modo testing, no envía emails reales.

## 🐛 Debugging

### Ver queries SQL ejecutadas

```python
from django.test.utils import override_settings

@override_settings(DEBUG=True)
def test_something():
    from django.db import connection
    # ... tu test ...
    print(len(connection.queries))  # Número de queries
```

### Ver datos de fixture

```python
def test_something(client_user):
    print(f"User ID: {client_user.id}")
    print(f"Username: {client_user.username}")
```

### Usar breakpoints

```python
def test_something():
    import pdb; pdb.set_trace()
    # El test se pausará aquí
```

## 🔧 Configuración Avanzada

### Ejecutar tests en paralelo

```powershell
pip install pytest-xdist
pytest -n auto  # Usa todos los cores disponibles
```

### Generar reporte XML (para CI/CD)

```powershell
pytest --junitxml=test-results.xml
```

### Modo watch (re-ejecutar al cambiar código)

```powershell
pip install pytest-watch
ptw
```

## 📝 Buenas Prácticas

1. **Nombres descriptivos**: `test_manager_can_approve_return` en lugar de `test_approve`
2. **Arrange-Act-Assert**: Estructura clara en cada test
3. **Un concepto por test**: No mezclar múltiples validaciones
4. **Fixtures reutilizables**: Evitar duplicación de código
5. **Mocking apropiado**: Mock servicios externos (Stripe, emails reales)

## 🚨 CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest --cov --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## 📚 Recursos Adicionales

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-django Documentation](https://pytest-django.readthedocs.io/)
- [Django Testing](https://docs.djangoproject.com/en/5.0/topics/testing/)
- [DRF Testing](https://www.django-rest-framework.org/api-guide/testing/)

## ✅ Checklist Pre-Deployment

- [ ] Todos los tests pasan (`pytest`)
- [ ] Cobertura > 90% (`pytest --cov`)
- [ ] No hay warnings (`pytest -W error`)
- [ ] Tests de integración pasan
- [ ] Tests de email verificados
- [ ] Tests de permisos validados
- [ ] Tests de validaciones completos

---

**Total Tests**: 39 tests (15 returns + 24 wallet)  
**Coverage Objetivo**: > 95%  
**Última actualización**: 10 de Noviembre, 2025
