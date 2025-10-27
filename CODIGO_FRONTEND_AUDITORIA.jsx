// ========================================
// 🔧 CÓDIGO LISTO PARA COPIAR Y PEGAR
// ========================================

// ==========================================
// 1️⃣ SERVICIO DE AUTENTICACIÓN
// Archivo: src/services/authService.js
// ==========================================

const API_URL = 'http://localhost:8000';

class AuthService {
  /**
   * Login - Autentica usuario y guarda tokens
   */
  async login(username, password) {
    console.log('🔐 Intentando login...');
    
    const response = await fetch(`${API_URL}/api/token/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login fallido');
    }

    const data = await response.json();
    
    // Guardar tokens en localStorage
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    
    console.log('✅ Login exitoso, tokens guardados');
    
    return data;
  }

  /**
   * Logout - Elimina tokens
   */
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    console.log('👋 Logout completado');
  }

  /**
   * Obtener token de acceso
   */
  getToken() {
    return localStorage.getItem('access_token');
  }

  /**
   * Verificar si está autenticado
   */
  isAuthenticated() {
    const token = this.getToken();
    return !!token;
  }

  /**
   * Obtener headers con autorización
   */
  getAuthHeaders() {
    const token = this.getToken();
    
    if (!token) {
      console.warn('⚠️ No hay token disponible');
    }
    
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    };
  }

  /**
   * Refresh token - Renueva el access token
   */
  async refreshToken() {
    const refresh = localStorage.getItem('refresh_token');
    
    if (!refresh) {
      throw new Error('No refresh token disponible');
    }

    console.log('🔄 Renovando token...');

    const response = await fetch(`${API_URL}/api/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh })
    });

    if (!response.ok) {
      this.logout();
      throw new Error('Token expirado, vuelve a iniciar sesión');
    }

    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    
    console.log('✅ Token renovado');
    
    return data.access;
  }

  /**
   * Fetch con manejo automático de token expirado
   */
  async fetchWithAuth(url, options = {}) {
    // Primera petición con token actual
    let response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        ...this.getAuthHeaders()
      }
    });

    // Si es 401, intentar renovar token y reintentar
    if (response.status === 401) {
      console.log('⚠️ Token expirado, intentando renovar...');
      
      try {
        await this.refreshToken();
        
        // Reintentar petición con nuevo token
        response = await fetch(url, {
          ...options,
          headers: {
            ...options.headers,
            ...this.getAuthHeaders()
          }
        });
      } catch (error) {
        console.error('❌ No se pudo renovar token');
        throw error;
      }
    }

    return response;
  }
}

export default new AuthService();


// ==========================================
// 2️⃣ COMPONENTE DE LOGIN
// Archivo: src/components/Login.jsx
// ==========================================

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      console.log('🔐 Iniciando login...');
      
      // Usar el servicio de autenticación
      await authService.login(username, password);
      
      // Verificar que el token se guardó
      const token = authService.getToken();
      console.log('✅ Token guardado:', token ? 'Sí' : 'No');
      
      if (!token) {
        throw new Error('Token no se guardó correctamente');
      }
      
      console.log('✅ Login exitoso, redirigiendo...');
      
      // Redirigir al dashboard
      navigate('/dashboard');
      
    } catch (error) {
      console.error('❌ Error en login:', error);
      setError(error.message || 'Usuario o contraseña incorrectos');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h2>Iniciar Sesión</h2>
      
      {error && (
        <div className="error-message" style={{ color: 'red', marginBottom: '10px' }}>
          {error}
        </div>
      )}
      
      <form onSubmit={handleLogin}>
        <div className="form-group">
          <label>Usuario:</label>
          <input
            type="text"
            placeholder="admin"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            disabled={loading}
          />
        </div>
        
        <div className="form-group">
          <label>Contraseña:</label>
          <input
            type="password"
            placeholder="admin123"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={loading}
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
        </button>
      </form>
    </div>
  );
};

export default Login;


// ==========================================
// 3️⃣ COMPONENTE ADMINAUDIT (ACTUALIZADO)
// Archivo: src/components/AdminAudit.jsx
// ==========================================

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';

const API_URL = 'http://localhost:8000/api';

const AdminAudit = () => {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [totalLogs, setTotalLogs] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Verificar autenticación al montar
  useEffect(() => {
    console.log('🔍 Verificando autenticación...');
    
    if (!authService.isAuthenticated()) {
      console.error('❌ Usuario no autenticado');
      navigate('/login');
      return;
    }
    
    console.log('✅ Usuario autenticado');
    fetchLogs();
    fetchStats();
  }, [currentPage]);

  /**
   * Obtener logs de auditoría
   */
  const fetchLogs = async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('📡 Obteniendo logs página', currentPage);

      // Usar el método fetchWithAuth que maneja token expirado automáticamente
      const response = await authService.fetchWithAuth(
        `${API_URL}/audit/?page=${currentPage}`
      );

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ Logs obtenidos:', data);

      setLogs(data.results || []);
      setTotalLogs(data.count || 0);

    } catch (error) {
      console.error('❌ Error al obtener logs:', error);
      setError(error.message);

      // Si el error es de autenticación, redirigir a login
      if (error.message.includes('Token expirado')) {
        authService.logout();
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * Obtener estadísticas
   */
  const fetchStats = async () => {
    try {
      console.log('📊 Obteniendo estadísticas...');

      const response = await authService.fetchWithAuth(
        `${API_URL}/audit/stats/`
      );

      if (!response.ok) {
        throw new Error(`Error ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Estadísticas obtenidas:', data);

      setStats(data);

    } catch (error) {
      console.error('❌ Error al obtener stats:', error);
    }
  };

  /**
   * Descargar PDF
   */
  const handleDownloadPDF = async () => {
    try {
      console.log('📄 Descargando PDF...');

      const response = await authService.fetchWithAuth(
        `${API_URL}/audit/export_pdf/`
      );

      if (!response.ok) {
        throw new Error('Error al descargar PDF');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `auditoria_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      console.log('✅ PDF descargado');

    } catch (error) {
      console.error('❌ Error al descargar PDF:', error);
      alert('Error al descargar el PDF');
    }
  };

  /**
   * Descargar Excel
   */
  const handleDownloadExcel = async () => {
    try {
      console.log('📊 Descargando Excel...');

      const response = await authService.fetchWithAuth(
        `${API_URL}/audit/export_excel/`
      );

      if (!response.ok) {
        throw new Error('Error al descargar Excel');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `auditoria_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      console.log('✅ Excel descargado');

    } catch (error) {
      console.error('❌ Error al descargar Excel:', error);
      alert('Error al descargar el Excel');
    }
  };

  if (loading) {
    return <div>Cargando logs de auditoría...</div>;
  }

  if (error) {
    return (
      <div style={{ color: 'red' }}>
        <h3>Error al cargar auditoría</h3>
        <p>{error}</p>
        <button onClick={fetchLogs}>Reintentar</button>
      </div>
    );
  }

  return (
    <div className="admin-audit">
      <h2>📋 Sistema de Auditoría</h2>

      {/* Panel de estadísticas */}
      {stats && (
        <div className="stats-panel">
          <div className="stat-card">
            <h3>Total de Logs</h3>
            <p>{stats.total_logs}</p>
          </div>
          <div className="stat-card">
            <h3>Últimas 24 horas</h3>
            <p>{stats.last_24_hours}</p>
          </div>
          <div className="stat-card">
            <h3>Última semana</h3>
            <p>{stats.last_week}</p>
          </div>
        </div>
      )}

      {/* Botones de descarga */}
      <div className="download-buttons">
        <button onClick={handleDownloadPDF}>📄 Descargar PDF</button>
        <button onClick={handleDownloadExcel}>📊 Descargar Excel</button>
      </div>

      {/* Tabla de logs */}
      <div className="logs-table">
        <h3>Registros de Auditoría ({totalLogs} total)</h3>
        
        {logs.length === 0 ? (
          <p>No hay logs registrados</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Acción</th>
                <th>Usuario</th>
                <th>Fecha/Hora</th>
                <th>IP</th>
                <th>Severidad</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td>{log.id}</td>
                  <td>{log.action}</td>
                  <td>{log.username || 'Anónimo'}</td>
                  <td>{new Date(log.timestamp).toLocaleString()}</td>
                  <td>{log.ip_address}</td>
                  <td>{log.severity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {/* Paginación */}
        <div className="pagination">
          <button
            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            disabled={currentPage === 1}
          >
            ← Anterior
          </button>
          
          <span>Página {currentPage}</span>
          
          <button
            onClick={() => setCurrentPage(p => p + 1)}
            disabled={logs.length < 20}
          >
            Siguiente →
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminAudit;


// ==========================================
// 4️⃣ RUTA PROTEGIDA (OPCIONAL)
// Archivo: src/components/ProtectedRoute.jsx
// ==========================================

import React from 'react';
import { Navigate } from 'react-router-dom';
import authService from '../services/authService';

const ProtectedRoute = ({ children }) => {
  if (!authService.isAuthenticated()) {
    console.warn('⚠️ Ruta protegida: usuario no autenticado');
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;


// ==========================================
// 5️⃣ CONFIGURACIÓN DE RUTAS
// Archivo: src/App.jsx
// ==========================================

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import AdminAudit from './components/AdminAudit';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Ruta pública */}
        <Route path="/login" element={<Login />} />
        
        {/* Rutas protegidas */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <div>Dashboard</div>
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/audit"
          element={
            <ProtectedRoute>
              <AdminAudit />
            </ProtectedRoute>
          }
        />
        
        {/* Redirección por defecto */}
        <Route path="/" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;


// ==========================================
// 6️⃣ PRUEBA MANUAL EN CONSOLA DEL NAVEGADOR
// Ejecutar en DevTools (F12 → Console)
// ==========================================

// Verificar token guardado
console.log('Token:', localStorage.getItem('access_token'));

// Probar petición manual
const token = localStorage.getItem('access_token');

if (token) {
  fetch('http://localhost:8000/api/audit/?page=1', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
    .then(res => {
      console.log('Status:', res.status);
      return res.json();
    })
    .then(data => console.log('✅ Respuesta:', data))
    .catch(err => console.error('❌ Error:', err));
} else {
  console.error('❌ No hay token en localStorage');
}


// ==========================================
// 7️⃣ CREDENCIALES DE PRUEBA
// ==========================================

/*
Usuario: admin
Contraseña: admin123

Endpoint de login: http://localhost:8000/api/token/
Endpoint de auditoría: http://localhost:8000/api/audit/
Endpoint de stats: http://localhost:8000/api/audit/stats/
*/
