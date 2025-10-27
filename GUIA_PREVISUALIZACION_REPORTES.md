# 👁️ Sistema de Previsualización de Reportes

## 🎯 ¿Qué se agregó?

Sistema completo de **previsualización** que permite ver los datos del reporte **ANTES de descargar** el PDF/Excel.

### ✅ Nuevos Endpoints (Retornan JSON)

```bash
# 1. Previsualizar reporte de ventas
GET /api/reports/sales/preview/?start_date=2025-01-01&end_date=2025-01-31

# 2. Previsualizar reporte de productos
GET /api/reports/products/preview/

# 3. Previsualizar reporte dinámico (con lenguaje natural)
POST /api/reports/dynamic-parser/preview/
Body: {"prompt": "ventas del mes de octubre agrupado por producto"}
```

### 📊 Endpoints Originales (Descargan PDF/Excel)

Estos **siguen funcionando exactamente igual**:

```bash
# Descargar reporte de ventas
GET /api/reports/sales/?start_date=2025-01-01&end_date=2025-01-31&format=pdf
GET /api/reports/sales/?start_date=2025-01-01&end_date=2025-01-31&format=excel

# Descargar reporte de productos
GET /api/reports/products/?format=pdf
GET /api/reports/products/?format=excel

# Descargar reporte dinámico
POST /api/reports/dynamic-parser/
Body: {"prompt": "ventas del mes de octubre en PDF"}
```

---

## 📡 Detalle de los Nuevos Endpoints

### 1️⃣ Previsualizar Reporte de Ventas

**Endpoint:** `GET /api/reports/sales/preview/`

**Parámetros requeridos:**
- `start_date`: Fecha inicio (formato: YYYY-MM-DD)
- `end_date`: Fecha fin (formato: YYYY-MM-DD)

**Ejemplo de petición:**
```javascript
const response = await fetch(
  'http://localhost:8000/api/reports/sales/preview/?start_date=2025-10-01&end_date=2025-10-31',
  {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }
);

const data = await response.json();
console.log(data);
```

**Respuesta JSON:**
```json
{
  "start_date": "2025-10-01",
  "end_date": "2025-10-31",
  "total_orders": 25,
  "total_revenue": 15750.50,
  "orders": [
    {
      "order_id": 145,
      "date": "2025-10-15 14:30:25",
      "customer": "Juan Pérez",
      "customer_email": "juan@email.com",
      "total": 1250.00,
      "items_count": 3,
      "items": [
        {
          "product": "Laptop Dell XPS 13",
          "quantity": 1,
          "price": 999.99,
          "subtotal": 999.99
        },
        {
          "product": "Mouse Logitech",
          "quantity": 2,
          "price": 25.00,
          "subtotal": 50.00
        }
      ]
    },
    // ... más órdenes
  ]
}
```

**Uso en el Frontend:**
1. Llamar al endpoint de preview
2. Mostrar los datos en una tabla o cards
3. Botón "Descargar PDF" → llama a `/api/reports/sales/?format=pdf&start_date=...&end_date=...`
4. Botón "Descargar Excel" → llama a `/api/reports/sales/?format=excel&start_date=...&end_date=...`

---

### 2️⃣ Previsualizar Reporte de Productos

**Endpoint:** `GET /api/reports/products/preview/`

**Sin parámetros requeridos** (muestra todos los productos activos)

**Ejemplo de petición:**
```javascript
const response = await fetch(
  'http://localhost:8000/api/reports/products/preview/',
  {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }
);

const data = await response.json();
console.log(data);
```

**Respuesta JSON:**
```json
{
  "total_products": 35,
  "total_stock": 450,
  "total_value": 45250.75,
  "products": [
    {
      "id": 1,
      "name": "Laptop Dell XPS 13",
      "category": "Laptops",
      "price": 999.99,
      "stock": 10,
      "value": 9999.90,
      "description": "Laptop ultraportátil con procesador Intel Core i7..."
    },
    {
      "id": 2,
      "name": "iPhone 13 Pro",
      "category": "Celulares",
      "price": 1099.00,
      "stock": 15,
      "value": 16485.00,
      "description": "Smartphone Apple con cámara triple..."
    },
    // ... más productos
  ]
}
```

**Uso en el Frontend:**
1. Llamar al endpoint de preview
2. Mostrar los productos en una tabla con:
   - Nombre, Categoría, Precio, Stock, Valor Total
   - Resumen: Total productos, Total stock, Valor total del inventario
3. Botón "Descargar PDF" → llama a `/api/reports/products/?format=pdf`
4. Botón "Descargar Excel" → llama a `/api/reports/products/?format=excel`

---

### 3️⃣ Previsualizar Reporte Dinámico

**Endpoint:** `POST /api/reports/dynamic-parser/preview/`

**Body JSON:**
```json
{
  "prompt": "ventas del mes de octubre agrupado por producto"
}
```

**Ejemplo de petición:**
```javascript
const response = await fetch(
  'http://localhost:8000/api/reports/dynamic-parser/preview/',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      prompt: "ventas del mes de octubre agrupado por producto"
    })
  }
);

const data = await response.json();
console.log(data);
```

**Respuesta JSON:**
```json
{
  "title": "Ventas por Producto (2025-10-01 a 2025-10-31)",
  "start_date": "2025-10-01",
  "end_date": "2025-10-31",
  "headers": ["Producto", "Cantidad Vendida", "Total Ventas"],
  "data": [
    {
      "Producto": "Laptop Dell XPS 13",
      "Cantidad Vendida": "15",
      "Total Ventas": "$14999.85"
    },
    {
      "Producto": "iPhone 13 Pro",
      "Cantidad Vendida": "22",
      "Total Ventas": "$24178.00"
    },
    // ... más productos
  ],
  "total_records": 18
}
```

**Prompts soportados:**
- "ventas del mes de octubre"
- "ventas del 01/10/2025 al 31/10/2025"
- "ventas agrupado por producto del mes de octubre"
- "ventas agrupado por cliente con nombres"
- "reporte de productos"

**Uso en el Frontend:**
1. Input de texto para el prompt
2. Botón "Vista Previa" → llama a `/api/reports/dynamic-parser/preview/`
3. Mostrar los datos en tabla dinámica usando `headers` y `data`
4. Botón "Descargar PDF" → llama a `/api/reports/dynamic-parser/` con `prompt + " en PDF"`
5. Botón "Descargar Excel" → llama a `/api/reports/dynamic-parser/` con `prompt + " en Excel"`

---

## 🎨 Ejemplo de Implementación en React

### Componente de Reporte de Ventas

```jsx
import React, { useState } from 'react';

function SalesReportComponent() {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [previewData, setPreviewData] = useState(null);
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem('access_token');

  // Función para previsualizar
  const handlePreview = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/reports/sales/preview/?start_date=${startDate}&end_date=${endDate}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      const data = await response.json();
      setPreviewData(data);
    } catch (error) {
      console.error('Error:', error);
      alert('Error al cargar preview');
    }
    setLoading(false);
  };

  // Función para descargar PDF
  const handleDownloadPDF = async () => {
    const response = await fetch(
      `http://localhost:8000/api/reports/sales/?start_date=${startDate}&end_date=${endDate}&format=pdf`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reporte_ventas_${startDate}_${endDate}.pdf`;
    a.click();
  };

  // Función para descargar Excel
  const handleDownloadExcel = async () => {
    const response = await fetch(
      `http://localhost:8000/api/reports/sales/?start_date=${startDate}&end_date=${endDate}&format=excel`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reporte_ventas_${startDate}_${endDate}.xlsx`;
    a.click();
  };

  return (
    <div className="sales-report">
      <h2>Reporte de Ventas</h2>
      
      {/* Formulario */}
      <div className="form">
        <input 
          type="date" 
          value={startDate} 
          onChange={(e) => setStartDate(e.target.value)}
          placeholder="Fecha inicio"
        />
        <input 
          type="date" 
          value={endDate} 
          onChange={(e) => setEndDate(e.target.value)}
          placeholder="Fecha fin"
        />
        <button onClick={handlePreview} disabled={loading}>
          {loading ? 'Cargando...' : '👁️ Vista Previa'}
        </button>
      </div>

      {/* Preview */}
      {previewData && (
        <div className="preview">
          <div className="summary">
            <h3>Resumen</h3>
            <p><strong>Período:</strong> {previewData.start_date} a {previewData.end_date}</p>
            <p><strong>Total Órdenes:</strong> {previewData.total_orders}</p>
            <p><strong>Total Ventas:</strong> ${previewData.total_revenue}</p>
          </div>

          {/* Tabla */}
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Fecha</th>
                <th>Cliente</th>
                <th>Email</th>
                <th>Items</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {previewData.orders.map((order) => (
                <tr key={order.order_id}>
                  <td>{order.order_id}</td>
                  <td>{order.date}</td>
                  <td>{order.customer}</td>
                  <td>{order.customer_email}</td>
                  <td>{order.items_count}</td>
                  <td>${order.total}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Botones de descarga */}
          <div className="download-buttons">
            <button onClick={handleDownloadPDF}>
              📄 Descargar PDF
            </button>
            <button onClick={handleDownloadExcel}>
              📊 Descargar Excel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default SalesReportComponent;
```

---

## 📝 Flujo de Uso Recomendado

### Flujo de Usuario:

1. **Usuario selecciona parámetros** (fechas, tipo de reporte, etc.)
2. **Usuario hace clic en "Vista Previa"**
3. **Frontend llama a `/preview/` endpoint** → Recibe JSON
4. **Frontend muestra tabla/gráficos** con los datos
5. **Usuario revisa los datos** y decide si:
   - ✅ Está correcto → Hace clic en "Descargar PDF" o "Descargar Excel"
   - ❌ No es lo que esperaba → Cambia parámetros y repite

### Ventajas:

- ✅ **Usuario ve exactamente qué va a descargar**
- ✅ **Ahorra descargas innecesarias** (ancho de banda)
- ✅ **Mejor UX** - feedback visual inmediato
- ✅ **Validación** - detectar errores antes de generar PDF
- ✅ **Flexibilidad** - elegir formato después de ver datos

---

## 🔒 Permisos

**Todos los endpoints requieren:**
- ✅ Autenticación JWT (`Bearer token`)
- ✅ Rol de administrador (`is_staff=True`)

---

## 🧪 Testing

### Probar con cURL:

```bash
# 1. Obtener token
TOKEN=$(curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r .access)

# 2. Preview de ventas
curl -X GET "http://localhost:8000/api/reports/sales/preview/?start_date=2025-10-01&end_date=2025-10-31" \
  -H "Authorization: Bearer $TOKEN" \
  | jq

# 3. Preview de productos
curl -X GET "http://localhost:8000/api/reports/products/preview/" \
  -H "Authorization: Bearer $TOKEN" \
  | jq

# 4. Preview dinámico
curl -X POST "http://localhost:8000/api/reports/dynamic-parser/preview/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"ventas del mes de octubre"}' \
  | jq
```

---

## 📊 Resumen de Endpoints

| Endpoint | Método | Descripción | Retorna |
|----------|--------|-------------|---------|
| `/api/reports/sales/preview/` | GET | Preview ventas | JSON con órdenes |
| `/api/reports/products/preview/` | GET | Preview productos | JSON con productos |
| `/api/reports/dynamic-parser/preview/` | POST | Preview dinámico | JSON con datos |
| `/api/reports/sales/` | GET | Descargar ventas | PDF/Excel file |
| `/api/reports/products/` | GET | Descargar productos | PDF/Excel file |
| `/api/reports/dynamic-parser/` | POST | Descargar dinámico | PDF/Excel file |

---

## ✨ Características

- ✅ **JSON estructurado** - Fácil de parsear en frontend
- ✅ **Datos completos** - Toda la información necesaria
- ✅ **Resúmenes** - Totales, conteos, agregaciones
- ✅ **Compatible** - Funciona con endpoints originales
- ✅ **Rápido** - Solo consulta DB, no genera archivos
- ✅ **Flexible** - Mismo parser que reportes originales

---

**¡Sistema de previsualización implementado y listo! 🚀**

El backend ahora soporta:
1. ✅ **Ver datos antes** (endpoints `/preview/`)
2. ✅ **Descargar después** (endpoints originales)
3. ✅ **Mejor UX** para el usuario final
