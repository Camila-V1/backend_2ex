# 📊 Guía: Predicciones de Ventas con IA - React Frontend

## 🎯 Objetivo

Integrar el sistema de predicción de ventas futuras (Machine Learning) en el frontend React para que ADMIN y MANAGER puedan visualizar:
- Predicciones de ventas para los próximos 30 días
- Gráfica de tendencias
- Análisis por día de la semana
- Exportación de datos

---

## 📋 Requisitos Previos

- ✅ Backend con modelo entrenado: `python manage.py train_sales_model`
- ✅ Endpoint funcionando: `GET /api/predictions/sales/`
- ✅ Usuario con rol ADMIN o MANAGER
- ✅ React con Chart.js o Recharts instalado

---

## PARTE 1: Componente de Predicciones

### Paso 1.1: Instalar Dependencias

```bash
cd web_2ex
npm install recharts date-fns
# O si usas yarn:
yarn add recharts date-fns
```

### Paso 1.2: Crear Servicio de API

Crea o actualiza `src/services/api.js`:

```javascript
// src/services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://backend-2ex-ecommerce.onrender.com/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Función para obtener predicciones de ventas
export const getSalesPredictions = async () => {
  try {
    const response = await api.get('/predictions/sales/');
    return response.data;
  } catch (error) {
    if (error.response?.status === 404) {
      throw new Error('El modelo de predicción no ha sido entrenado. Contacte al administrador.');
    }
    throw error;
  }
};

export default api;
```

### Paso 1.3: Crear Componente de Predicciones

Crea `src/components/SalesPredictions.jsx`:

```jsx
// src/components/SalesPredictions.jsx
import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';
import { getSalesPredictions } from '../services/api';
import './SalesPredictions.css';

const SalesPredictions = () => {
  const [predictions, setPredictions] = useState([]);
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('line'); // 'line' o 'bar'
  const [stats, setStats] = useState({
    totalPredicted: 0,
    avgDaily: 0,
    maxDay: null,
    minDay: null,
  });

  useEffect(() => {
    fetchPredictions();
  }, []);

  const fetchPredictions = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await getSalesPredictions();
      
      // Procesar datos para la gráfica
      const processedData = data.predictions.map(pred => ({
        date: pred.date,
        sales: pred.predicted_sales,
        dayOfWeek: pred.day_of_week,
        formattedDate: format(parseISO(pred.date), 'dd MMM', { locale: es }),
      }));
      
      setPredictions(processedData);
      setModelInfo(data.model_info);
      
      // Calcular estadísticas
      const total = processedData.reduce((sum, p) => sum + p.sales, 0);
      const avg = total / processedData.length;
      const maxDay = processedData.reduce((max, p) => p.sales > max.sales ? p : max);
      const minDay = processedData.reduce((min, p) => p.sales < min.sales ? p : min);
      
      setStats({
        totalPredicted: total.toFixed(2),
        avgDaily: avg.toFixed(2),
        maxDay: maxDay,
        minDay: minDay,
      });
      
    } catch (err) {
      setError(err.message || 'Error al cargar las predicciones');
      console.error('Error fetching predictions:', err);
    } finally {
      setLoading(false);
    }
  };

  const exportToCSV = () => {
    const headers = ['Fecha', 'Ventas Predichas', 'Día de la Semana'];
    const rows = predictions.map(p => [p.date, p.sales, p.dayOfWeek]);
    
    const csv = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `predicciones-ventas-${format(new Date(), 'yyyy-MM-dd')}.csv`;
    a.click();
  };

  if (loading) {
    return (
      <div className="predictions-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Cargando predicciones...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="predictions-container">
        <div className="error-message">
          <h3>⚠️ Error</h3>
          <p>{error}</p>
          <button onClick={fetchPredictions} className="retry-button">
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="predictions-container">
      {/* Header */}
      <div className="predictions-header">
        <div className="header-content">
          <h1>📊 Predicciones de Ventas (IA)</h1>
          <p className="subtitle">
            Predicciones generadas con Machine Learning para los próximos 30 días
          </p>
        </div>
        
        <div className="header-actions">
          <button onClick={exportToCSV} className="export-button">
            📥 Exportar CSV
          </button>
          <button onClick={fetchPredictions} className="refresh-button">
            🔄 Actualizar
          </button>
        </div>
      </div>

      {/* Estadísticas */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <p className="stat-label">Total Predicho (30 días)</p>
            <p className="stat-value">{stats.totalPredicted}</p>
            <p className="stat-unit">unidades</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <p className="stat-label">Promedio Diario</p>
            <p className="stat-value">{stats.avgDaily}</p>
            <p className="stat-unit">unidades/día</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🔝</div>
          <div className="stat-content">
            <p className="stat-label">Día con Mayor Demanda</p>
            <p className="stat-value">{stats.maxDay?.formattedDate}</p>
            <p className="stat-unit">{stats.maxDay?.sales.toFixed(2)} unidades</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📉</div>
          <div className="stat-content">
            <p className="stat-label">Día con Menor Demanda</p>
            <p className="stat-value">{stats.minDay?.formattedDate}</p>
            <p className="stat-unit">{stats.minDay?.sales.toFixed(2)} unidades</p>
          </div>
        </div>
      </div>

      {/* Controles de Vista */}
      <div className="chart-controls">
        <div className="view-toggle">
          <button
            className={`toggle-button ${viewMode === 'line' ? 'active' : ''}`}
            onClick={() => setViewMode('line')}
          >
            📈 Línea
          </button>
          <button
            className={`toggle-button ${viewMode === 'bar' ? 'active' : ''}`}
            onClick={() => setViewMode('bar')}
          >
            📊 Barras
          </button>
        </div>
      </div>

      {/* Gráfica */}
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={400}>
          {viewMode === 'line' ? (
            <LineChart data={predictions}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="formattedDate" 
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis 
                label={{ value: 'Unidades Predichas', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip 
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="custom-tooltip">
                        <p className="tooltip-date">{data.formattedDate}</p>
                        <p className="tooltip-day">{data.dayOfWeek}</p>
                        <p className="tooltip-value">
                          <strong>{data.sales.toFixed(2)}</strong> unidades
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="sales" 
                stroke="#8884d8" 
                strokeWidth={2}
                name="Ventas Predichas"
                dot={{ fill: '#8884d8', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          ) : (
            <BarChart data={predictions}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="formattedDate" 
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis 
                label={{ value: 'Unidades Predichas', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip 
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="custom-tooltip">
                        <p className="tooltip-date">{data.formattedDate}</p>
                        <p className="tooltip-day">{data.dayOfWeek}</p>
                        <p className="tooltip-value">
                          <strong>{data.sales.toFixed(2)}</strong> unidades
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend />
              <Bar 
                dataKey="sales" 
                fill="#82ca9d" 
                name="Ventas Predichas"
              />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* Tabla de Datos */}
      <div className="data-table-container">
        <h3>📋 Datos Detallados</h3>
        <div className="table-wrapper">
          <table className="predictions-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Día de la Semana</th>
                <th>Ventas Predichas</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map((pred, index) => (
                <tr key={index}>
                  <td>{pred.formattedDate}</td>
                  <td>{pred.dayOfWeek}</td>
                  <td className="sales-value">{pred.sales.toFixed(2)} unidades</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Información del Modelo */}
      {modelInfo && (
        <div className="model-info">
          <h3>🤖 Información del Modelo</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Estado:</span>
              <span className="info-value">
                {modelInfo.trained ? '✅ Entrenado' : '❌ No entrenado'}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Período de Predicción:</span>
              <span className="info-value">{modelInfo.prediction_period}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Fecha Inicio:</span>
              <span className="info-value">
                {format(parseISO(modelInfo.start_date), 'dd/MM/yyyy', { locale: es })}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Fecha Fin:</span>
              <span className="info-value">
                {format(parseISO(modelInfo.end_date), 'dd/MM/yyyy', { locale: es })}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SalesPredictions;
```

### Paso 1.4: Crear Estilos CSS

Crea `src/components/SalesPredictions.css`:

```css
/* src/components/SalesPredictions.css */
.predictions-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  background: #f5f7fa;
  min-height: 100vh;
}

/* Header */
.predictions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content h1 {
  margin: 0 0 8px 0;
  color: #1a202c;
  font-size: 28px;
}

.subtitle {
  margin: 0;
  color: #718096;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.export-button,
.refresh-button {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.export-button {
  background: #48bb78;
  color: white;
}

.export-button:hover {
  background: #38a169;
  transform: translateY(-2px);
}

.refresh-button {
  background: #4299e1;
  color: white;
}

.refresh-button:hover {
  background: #3182ce;
  transform: translateY(-2px);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 40px;
}

.stat-content {
  flex: 1;
}

.stat-label {
  margin: 0 0 8px 0;
  color: #718096;
  font-size: 13px;
  font-weight: 500;
}

.stat-value {
  margin: 0 0 4px 0;
  color: #1a202c;
  font-size: 28px;
  font-weight: bold;
}

.stat-unit {
  margin: 0;
  color: #a0aec0;
  font-size: 12px;
}

/* Chart Controls */
.chart-controls {
  background: white;
  padding: 16px 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.view-toggle {
  display: flex;
  gap: 12px;
}

.toggle-button {
  padding: 8px 16px;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
  transition: all 0.3s ease;
}

.toggle-button.active {
  background: #4299e1;
  color: white;
  border-color: #4299e1;
}

.toggle-button:hover:not(.active) {
  border-color: #4299e1;
  color: #4299e1;
}

/* Chart Container */
.chart-container {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.custom-tooltip {
  background: rgba(0, 0, 0, 0.85);
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.tooltip-date {
  margin: 0 0 4px 0;
  color: white;
  font-size: 14px;
  font-weight: bold;
}

.tooltip-day {
  margin: 0 0 8px 0;
  color: #cbd5e0;
  font-size: 12px;
}

.tooltip-value {
  margin: 0;
  color: white;
  font-size: 16px;
}

/* Data Table */
.data-table-container {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.data-table-container h3 {
  margin: 0 0 20px 0;
  color: #1a202c;
  font-size: 20px;
}

.table-wrapper {
  overflow-x: auto;
}

.predictions-table {
  width: 100%;
  border-collapse: collapse;
}

.predictions-table th {
  background: #f7fafc;
  padding: 12px;
  text-align: left;
  color: #4a5568;
  font-weight: 600;
  font-size: 14px;
  border-bottom: 2px solid #e2e8f0;
}

.predictions-table td {
  padding: 12px;
  border-bottom: 1px solid #e2e8f0;
  color: #2d3748;
  font-size: 14px;
}

.predictions-table tbody tr:hover {
  background: #f7fafc;
}

.sales-value {
  font-weight: 600;
  color: #48bb78;
}

/* Model Info */
.model-info {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.model-info h3 {
  margin: 0 0 20px 0;
  color: #1a202c;
  font-size: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  color: #718096;
  font-size: 13px;
  font-weight: 500;
}

.info-value {
  color: #1a202c;
  font-size: 15px;
  font-weight: 600;
}

/* Loading & Error States */
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4299e1;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background: #fff5f5;
  border: 2px solid #fc8181;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
}

.error-message h3 {
  margin: 0 0 12px 0;
  color: #c53030;
}

.error-message p {
  margin: 0 0 16px 0;
  color: #742a2a;
}

.retry-button {
  padding: 10px 20px;
  background: #fc8181;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.retry-button:hover {
  background: #f56565;
}

/* Responsive */
@media (max-width: 768px) {
  .predictions-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
  }
  
  .export-button,
  .refresh-button {
    flex: 1;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
```

---

## PARTE 2: Integración en el Router

### Paso 2.1: Agregar Ruta

En `src/App.jsx` o tu archivo de rutas:

```jsx
import SalesPredictions from './components/SalesPredictions';

// Dentro de tus rutas protegidas (ADMIN/MANAGER)
<Route 
  path="/predictions" 
  element={
    <ProtectedRoute roles={['ADMIN', 'MANAGER']}>
      <SalesPredictions />
    </ProtectedRoute>
  } 
/>
```

### Paso 2.2: Agregar al Menú de Navegación

```jsx
// En tu componente de Sidebar o Navbar
<NavLink to="/predictions" className="nav-item">
  <span className="nav-icon">📊</span>
  <span className="nav-text">Predicciones IA</span>
</NavLink>
```

---

## PARTE 3: Entrenar el Modelo (Backend)

Antes de usar el frontend, entrena el modelo:

```bash
cd backend_2ex
python manage.py train_sales_model
```

Verás:
```
✓ Modelo entrenado exitosamente
✓ MSE: 1.23
✓ Muestras usadas: 313
✓ Guardado en: predictions/sales_model.joblib
```

---

## 🧪 PRUEBAS

### 1. Probar Endpoint con Postman

```bash
# Login
POST /api/token/
{
  "username": "admin",
  "password": "admin123"
}

# Obtener predicciones
GET /api/predictions/sales/
Authorization: Bearer <token>
```

### 2. Verificar en React

1. Inicia el frontend: `npm start`
2. Login como admin o manager
3. Navega a `/predictions`
4. Deberías ver:
   - 4 tarjetas de estadísticas
   - Gráfica de línea/barras
   - Tabla con datos detallados
   - Información del modelo

---

## 🎨 CARACTERÍSTICAS

### Funcionalidades Implementadas

✅ **Gráfica interactiva** (línea y barras)  
✅ **Estadísticas clave** (total, promedio, máximo, mínimo)  
✅ **Exportación a CSV**  
✅ **Tabla de datos detallados**  
✅ **Información del modelo ML**  
✅ **Tooltip con detalles al pasar mouse**  
✅ **Responsive design**  
✅ **Loading y error states**  
✅ **Actualización manual**

### Próximas Mejoras (Opcional)

- [ ] Filtros por rango de fechas
- [ ] Comparación con ventas reales
- [ ] Predicciones por producto/categoría
- [ ] Alertas de stock bajo basadas en predicciones
- [ ] Notificaciones de días de alta demanda

---

## 📊 RESULTADO ESPERADO

La pantalla mostrará:

1. **Header** con título y botones de acción
2. **4 Tarjetas** con métricas clave
3. **Gráfica interactiva** con selector línea/barras
4. **Tabla detallada** con todos los datos
5. **Info del modelo** con fechas y estado

---

## 🚀 DESPLIEGUE

Para producción (Vercel/Netlify):

```bash
# Build
npm run build

# Variables de entorno (.env.production)
REACT_APP_API_URL=https://backend-2ex-ecommerce.onrender.com/api
```

---

## ✅ CHECKLIST

- [ ] Dependencias instaladas (`recharts`, `date-fns`)
- [ ] Servicio API creado con función `getSalesPredictions()`
- [ ] Componente `SalesPredictions.jsx` creado
- [ ] CSS importado y aplicado
- [ ] Ruta agregada en el router
- [ ] Enlace en menú de navegación
- [ ] Modelo entrenado en backend
- [ ] Probado con usuario ADMIN/MANAGER

---

**¡Listo! 🎉 Ahora tienes un dashboard completo de predicciones con IA.**
