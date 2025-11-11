// ===================================================================
// CONFIGURACIÓN DE API PARA FRONTEND - PRODUCCIÓN
// ===================================================================
// Copia este archivo en tu proyecto frontend y ajústalo según tu framework

// ===================================================================
// 1. PARA REACT (Create React App)
// ===================================================================

// src/config/api.js
const API_CONFIG = {
  // URL base del backend desplegado en AWS
  baseURL: process.env.REACT_APP_API_URL || 'http://98.92.49.243/api',
  
  // Timeout para las peticiones (30 segundos)
  timeout: 30000,
  
  // Headers por defecto
  headers: {
    'Content-Type': 'application/json',
  },
};

export default API_CONFIG;

// src/services/api.js (con Axios)
import axios from 'axios';
import API_CONFIG from '../config/api';

const api = axios.create(API_CONFIG);

// Interceptor para agregar el token JWT a todas las peticiones
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

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si el token expiró (401) y no hemos intentado refrescar
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_CONFIG.baseURL}/users/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        // Reintentar la petición original con el nuevo token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Si falla el refresh, cerrar sesión
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;

// ===================================================================
// 2. PARA NEXT.JS
// ===================================================================

// lib/api.js
const API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://98.92.49.243/api',
  timeout: 30000,
};

export default API_CONFIG;

// lib/axios.js
import axios from 'axios';
import API_CONFIG from './api';

const api = axios.create(API_CONFIG);

api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;

// ===================================================================
// 3. PARA VUE 3 + VITE
// ===================================================================

// src/config/api.js
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_URL || 'http://98.92.49.243/api',
  timeout: 30000,
};

// src/services/api.js
import axios from 'axios';
import { API_CONFIG } from '@/config/api';

const api = axios.create(API_CONFIG);

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;

// ===================================================================
// 4. EJEMPLOS DE USO EN COMPONENTES
// ===================================================================

// Ejemplo: Login
/*
import api from './services/api';

const login = async (username, password) => {
  try {
    const response = await api.post('/users/login/', {
      username,
      password,
    });
    
    const { access, refresh, user } = response.data;
    
    // Guardar tokens
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('user', JSON.stringify(user));
    
    return user;
  } catch (error) {
    console.error('Error en login:', error.response?.data);
    throw error;
  }
};
*/

// Ejemplo: Obtener productos
/*
import api from './services/api';

const getProducts = async () => {
  try {
    const response = await api.get('/products/');
    return response.data;
  } catch (error) {
    console.error('Error obteniendo productos:', error);
    throw error;
  }
};
*/

// Ejemplo: Crear orden
/*
import api from './services/api';

const createOrder = async (orderData) => {
  try {
    const response = await api.post('/orders/', orderData);
    return response.data;
  } catch (error) {
    console.error('Error creando orden:', error.response?.data);
    throw error;
  }
};
*/

// Ejemplo: Solicitar devolución
/*
import api from './services/api';

const requestReturn = async (returnData) => {
  try {
    const response = await api.post('/returns/', returnData);
    return response.data;
  } catch (error) {
    console.error('Error solicitando devolución:', error.response?.data);
    throw error;
  }
};
*/

// ===================================================================
// 5. VARIABLES DE ENTORNO PARA VERCEL
// ===================================================================

// Crear archivo .env.production en la raíz del proyecto:

// Para React:
// REACT_APP_API_URL=http://98.92.49.243/api

// Para Next.js:
// NEXT_PUBLIC_API_URL=http://98.92.49.243/api

// Para Vue/Vite:
// VITE_API_URL=http://98.92.49.243/api

// ===================================================================
// 6. CONFIGURACIÓN EN VERCEL DASHBOARD
// ===================================================================

/*
1. Ve a tu proyecto en Vercel
2. Click en "Settings" → "Environment Variables"
3. Agrega la variable según tu framework:
   - Name: REACT_APP_API_URL (o NEXT_PUBLIC_API_URL o VITE_API_URL)
   - Value: http://98.92.49.243/api
   - Environment: Production (y opcionalmente Preview y Development)
4. Click "Save"
5. Ve a "Deployments" y haz "Redeploy"
*/

// ===================================================================
// 7. ENDPOINTS DISPONIBLES
// ===================================================================

const ENDPOINTS = {
  // Autenticación
  LOGIN: '/users/login/',
  REGISTER: '/users/register/',
  REFRESH_TOKEN: '/users/token/refresh/',
  LOGOUT: '/users/logout/',
  
  // Usuarios
  USERS: '/users/',
  USER_DETAIL: (id) => `/users/${id}/`,
  USER_PROFILE: '/users/profile/',
  
  // Productos
  PRODUCTS: '/products/',
  PRODUCT_DETAIL: (id) => `/products/${id}/`,
  CATEGORIES: '/categories/',
  
  // Órdenes
  ORDERS: '/orders/',
  ORDER_DETAIL: (id) => `/orders/${id}/`,
  ORDER_ITEMS: '/order-items/',
  
  // Devoluciones
  RETURNS: '/returns/',
  RETURN_DETAIL: (id) => `/returns/${id}/`,
  RETURN_APPROVE: (id) => `/returns/${id}/approve/`,
  RETURN_REJECT: (id) => `/returns/${id}/reject/`,
  
  // Billeteras
  WALLETS: '/wallets/',
  WALLET_DETAIL: (id) => `/wallets/${id}/`,
  WALLET_TRANSACTIONS: '/wallet-transactions/',
  
  // Entregas (Deliveries)
  DELIVERIES: '/deliveries/',
  DELIVERY_DETAIL: (id) => `/deliveries/${id}/`,
  
  // Auditoría
  AUDIT_LOG: '/audit-log/',
  
  // Reportes
  REPORTS_SALES: '/reports/sales/',
  REPORTS_RETURNS: '/reports/returns/',
  REPORTS_INVENTORY: '/reports/inventory/',
};

export { ENDPOINTS };

// ===================================================================
// 8. EJEMPLO COMPLETO DE SERVICIO DE AUTENTICACIÓN
// ===================================================================

// src/services/authService.js
/*
import api from './api';
import { ENDPOINTS } from '../config/endpoints';

class AuthService {
  async login(username, password) {
    const response = await api.post(ENDPOINTS.LOGIN, {
      username,
      password,
    });
    
    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    
    return response.data;
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }

  getToken() {
    return localStorage.getItem('access_token');
  }
}

export default new AuthService();
*/
