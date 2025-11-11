# ============================================================================
# VUE 3 + VITE - Variables de Entorno para Producción
# ============================================================================
# 📁 Guarda este archivo como: .env.production
# 📍 Ubicación: Raíz de tu proyecto Vue
# ============================================================================

# URL de la API del backend desplegado en AWS
VITE_API_URL=http://98.92.49.243/api

# URL base del backend (sin /api)
VITE_API_BASE_URL=http://98.92.49.243

# URL del panel de administración Django
VITE_ADMIN_URL=http://98.92.49.243/admin

# Entorno de ejecución
VITE_ENV=production


# ============================================================================
# Ejemplo de uso en Vue 3 con Vite:
# ============================================================================

# // En cualquier componente Vue o archivo JS:
# const API_URL = import.meta.env.VITE_API_URL;
# 
# // Con fetch:
# fetch(`${API_URL}/products/`)
#   .then(res => res.json())
#   .then(data => console.log(data));


# // Con axios:
# import axios from 'axios';
# 
# const api = axios.create({
#   baseURL: import.meta.env.VITE_API_URL,
# });
# 
# // Obtener productos
# api.get('/products/');
# 
# // Login
# api.post('/users/login/', {
#   username: 'admin',
#   password: 'admin123'
# });


# // En un archivo de configuración (src/config/api.js):
# export const API_CONFIG = {
#   baseURL: import.meta.env.VITE_API_URL,
#   timeout: 30000,
# };


# // Composable para API (src/composables/useApi.js):
# import { ref } from 'vue';
# 
# export function useApi() {
#   const API_URL = import.meta.env.VITE_API_URL;
#   const loading = ref(false);
#   const error = ref(null);
#   
#   const fetchProducts = async () => {
#     loading.value = true;
#     try {
#       const res = await fetch(`${API_URL}/products/`);
#       const data = await res.json();
#       return data;
#     } catch (err) {
#       error.value = err.message;
#       throw err;
#     } finally {
#       loading.value = false;
#     }
#   };
#   
#   return {
#     API_URL,
#     loading,
#     error,
#     fetchProducts
#   };
# }


# ============================================================================
# Configuración en Vercel Dashboard:
# ============================================================================

# 1. Ve a tu proyecto en Vercel
# 2. Settings → Environment Variables
# 3. Agrega la variable:
#    Name: VITE_API_URL
#    Value: http://98.92.49.243/api
#    Environment: ☑️ Production ☑️ Preview ☑️ Development
# 4. Click "Add"
# 5. Hacer Redeploy desde Deployments


# ============================================================================
# Credenciales de prueba:
# ============================================================================
# Cliente: juan_cliente / password123
# Manager: carlos_manager / manager123
# Admin: admin / admin123


# ============================================================================
# Nota sobre Vite:
# ============================================================================
# - TODAS las variables de entorno en Vite deben empezar con VITE_
# - Las variables son reemplazadas en tiempo de build (no en runtime)
# - Si cambias una variable, debes hacer rebuild de la aplicación
