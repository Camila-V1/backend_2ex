# 💰 04. BILLETERA VIRTUAL (WALLET)

## 📝 Descripción General

La billetera virtual se crea **automáticamente** cuando se aprueba la primera devolución de un cliente con método `WALLET`. Permite al cliente acumular saldo y usarlo en futuras compras.

---

## 💳 ENDPOINTS DE BILLETERA

### 1. Ver Mi Saldo

**GET** `/api/users/wallets/my_balance/`

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "balance": "29999.95",
  "is_active": true,
  "wallet_id": 2
}
```

**Response (404) - Si no tiene billetera:**
```json
{
  "detail": "No tienes una billetera activa"
}
```

**Ejemplo JavaScript:**
```javascript
const getMyBalance = async () => {
  const response = await fetch('http://localhost:8000/api/users/wallets/my_balance/', {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
  });

  if (response.status === 404) {
    return { balance: '0.00', has_wallet: false };
  }

  const data = await response.json();
  return { ...data, has_wallet: true };
};

// Uso
const wallet = await getMyBalance();
console.log('Saldo:', wallet.balance);
```

---

### 2. Ver Mi Billetera (Detalle Completo)

**GET** `/api/users/wallets/`

**Response (200 OK):**
```json
{
  "count": 1,
  "results": [
    {
      "id": 2,
      "balance": "29999.95",
      "user": 49,
      "is_active": true,
      "created_at": "2025-11-10T22:22:41.103680Z",
      "updated_at": "2025-11-10T22:31:00.785123Z"
    }
  ]
}
```

---

## 📋 ENDPOINTS DE TRANSACCIONES

### 3. Ver Mis Transacciones

**GET** `/api/users/wallet-transactions/my_transactions/`

**Query Parameters:**
- `type` - Filtrar por tipo (`REFUND`, `DEPOSIT`, `WITHDRAWAL`, `PURCHASE`)
- `page` - Número de página
- `page_size` - Cantidad por página

**Response (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 6,
      "transaction_type": "REFUND",
      "transaction_type_display": "Reembolso de devolución",
      "amount": "5999.99",
      "balance_after": "29999.95",
      "status": "COMPLETED",
      "status_display": "Completada",
      "description": "Reembolso por devolución #21 - Tablet iPad Air",
      "reference_id": "RETURN-21",
      "is_credit": true,
      "is_debit": false,
      "created_at": "2025-11-10T22:31:00.777232Z",
      "updated_at": "2025-11-10T22:31:00.777239Z"
    },
    {
      "id": 5,
      "transaction_type": "REFUND",
      "transaction_type_display": "Reembolso de devolución",
      "amount": "5999.99",
      "balance_after": "23999.96",
      "status": "COMPLETED",
      "status_display": "Completada",
      "description": "Reembolso por devolución #20 - Tablet iPad Air",
      "reference_id": "RETURN-20",
      "is_credit": true,
      "is_debit": false,
      "created_at": "2025-11-10T22:28:48.694893Z",
      "updated_at": "2025-11-10T22:28:48.694898Z"
    }
  ]
}
```

**Ejemplo JavaScript:**
```javascript
const getMyTransactions = async (type = null) => {
  const params = type ? `?type=${type}` : '';
  
  const response = await fetch(
    `http://localhost:8000/api/users/wallet-transactions/my_transactions/${params}`,
    {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    }
  );

  return await response.json();
};

// Ver solo reembolsos
const refunds = await getMyTransactions('REFUND');
```

---

### 4. Estadísticas de Transacciones

**GET** `/api/users/wallet-transactions/statistics/`

**Response (200 OK):**
```json
{
  "current_balance": "29999.95",
  "total_credits": "29999.95",
  "total_debits": "0.00",
  "total_refunds": "29999.95",
  "transaction_count": 5
}
```

**Ejemplo JavaScript:**
```javascript
const getWalletStatistics = async () => {
  const response = await fetch(
    'http://localhost:8000/api/users/wallet-transactions/statistics/',
    {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    }
  );

  return await response.json();
};
```

---

## 📊 Tipos de Transacciones

| Tipo | Valor | Descripción | ¿Suma o Resta? |
|------|-------|-------------|----------------|
| Reembolso | `REFUND` | Devolución aprobada | ➕ Suma |
| Depósito | `DEPOSIT` | Recarga manual | ➕ Suma |
| Retiro | `WITHDRAWAL` | Retiro de fondos | ➖ Resta |
| Compra | `PURCHASE` | Uso en compra | ➖ Resta |

---

## 🎨 Componentes Frontend

### Componente: Resumen de Billetera

```jsx
import { useState, useEffect } from 'react';

const WalletSummary = () => {
  const [wallet, setWallet] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadWalletData();
  }, []);

  const loadWalletData = async () => {
    try {
      const [balanceData, statsData] = await Promise.all([
        getMyBalance(),
        getWalletStatistics()
      ]);
      
      setWallet(balanceData);
      setStats(statsData);
    } catch (error) {
      console.error('Error loading wallet:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando billetera...</div>;

  if (!wallet.has_wallet) {
    return (
      <div className="no-wallet">
        <h3>💰 Billetera Virtual</h3>
        <p>Aún no tienes una billetera.</p>
        <p>Se creará automáticamente cuando aprueban tu primera devolución.</p>
      </div>
    );
  }

  return (
    <div className="wallet-summary">
      <div className="wallet-header">
        <h2>💰 Mi Billetera</h2>
        <div className="balance">
          <span className="label">Saldo Disponible:</span>
          <span className="amount">${wallet.balance}</span>
        </div>
      </div>

      {stats && (
        <div className="wallet-stats">
          <div className="stat-card">
            <h4>Total Recibido</h4>
            <p className="stat-value green">${stats.total_credits}</p>
          </div>
          <div className="stat-card">
            <h4>Total Gastado</h4>
            <p className="stat-value red">${stats.total_debits}</p>
          </div>
          <div className="stat-card">
            <h4>Transacciones</h4>
            <p className="stat-value">{stats.transaction_count}</p>
          </div>
        </div>
      )}
    </div>
  );
};
```

---

### Componente: Lista de Transacciones

```jsx
const TransactionList = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState(null);

  useEffect(() => {
    loadTransactions();
  }, [filter]);

  const loadTransactions = async () => {
    try {
      const data = await getMyTransactions(filter);
      setTransactions(data.results);
    } catch (error) {
      console.error('Error loading transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTransactionIcon = (type) => {
    const icons = {
      'REFUND': '💰',
      'DEPOSIT': '➕',
      'WITHDRAWAL': '➖',
      'PURCHASE': '🛒'
    };
    return icons[type] || '💳';
  };

  if (loading) return <div>Cargando transacciones...</div>;

  return (
    <div className="transaction-list">
      <div className="list-header">
        <h3>📋 Historial de Transacciones</h3>
        <select
          value={filter || ''}
          onChange={(e) => setFilter(e.target.value || null)}
        >
          <option value="">Todas</option>
          <option value="REFUND">Reembolsos</option>
          <option value="DEPOSIT">Depósitos</option>
          <option value="WITHDRAWAL">Retiros</option>
          <option value="PURCHASE">Compras</option>
        </select>
      </div>

      {transactions.length === 0 ? (
        <p className="no-transactions">No hay transacciones</p>
      ) : (
        <div className="transactions">
          {transactions.map(tx => (
            <TransactionCard key={tx.id} transaction={tx} />
          ))}
        </div>
      )}
    </div>
  );
};

const TransactionCard = ({ transaction }) => {
  const isCredit = transaction.is_credit;
  
  return (
    <div className={`transaction-card ${isCredit ? 'credit' : 'debit'}`}>
      <div className="tx-icon">
        {getTransactionIcon(transaction.transaction_type)}
      </div>
      
      <div className="tx-info">
        <h4>{transaction.transaction_type_display}</h4>
        <p className="tx-description">{transaction.description}</p>
        <small className="tx-date">
          {new Date(transaction.created_at).toLocaleString()}
        </small>
      </div>
      
      <div className="tx-amount">
        <span className={isCredit ? 'amount-credit' : 'amount-debit'}>
          {isCredit ? '+' : '-'}${transaction.amount}
        </span>
        <small className="balance-after">
          Saldo: ${transaction.balance_after}
        </small>
      </div>
      
      <div className="tx-status">
        <span className={`status-badge status-${transaction.status.toLowerCase()}`}>
          {transaction.status_display}
        </span>
      </div>
    </div>
  );
};
```

---

## 💡 Integración con Compras

### Usar saldo de billetera en checkout:

```javascript
const createOrderWithWallet = async (orderData) => {
  const wallet = await getMyBalance();
  
  if (wallet.has_wallet && parseFloat(wallet.balance) >= orderData.total) {
    // Suficiente saldo, usar billetera
    return await fetch('http://localhost:8000/api/orders/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ...orderData,
        payment_method: 'WALLET',
        use_wallet_balance: true
      })
    });
  } else {
    // Saldo insuficiente, mostrar opciones
    alert(`Saldo insuficiente. Tu saldo: $${wallet.balance}`);
    return null;
  }
};
```

---

## 🎯 Widget de Saldo (Navbar)

```jsx
const WalletWidget = () => {
  const [balance, setBalance] = useState(null);

  useEffect(() => {
    loadBalance();
  }, []);

  const loadBalance = async () => {
    try {
      const wallet = await getMyBalance();
      if (wallet.has_wallet) {
        setBalance(wallet.balance);
      }
    } catch (error) {
      console.error('Error loading balance:', error);
    }
  };

  if (!balance) return null;

  return (
    <div className="wallet-widget" onClick={() => navigate('/wallet')}>
      <span className="wallet-icon">💰</span>
      <span className="wallet-balance">${balance}</span>
    </div>
  );
};
```

---

## 📱 Vista Completa de Billetera

```jsx
const WalletPage = () => {
  return (
    <div className="wallet-page">
      <WalletSummary />
      <TransactionList />
    </div>
  );
};
```

---

## ⚠️ Notas Importantes

1. **Creación Automática:** La billetera se crea cuando se aprueba la primera devolución con método `WALLET`
2. **Solo Lectura:** Los clientes solo pueden VER su billetera, no pueden recargarla manualmente (solo admins)
3. **Uso en Compras:** El saldo puede usarse en futuras compras (implementar en checkout)
4. **Sin Retiros:** Por ahora, no hay endpoint de retiro (solo admins pueden hacerlo)

---

**Siguiente:** Ver `06_EJEMPLOS_COMPLETOS.md` para ejemplos de código completo
