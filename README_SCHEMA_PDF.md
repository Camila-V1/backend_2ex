# 📄 Schema OpenAPI - SmartSales365 API

## Descripción

Este documento contiene el **schema OpenAPI completo** de la API SmartSales365 en formato PDF extendido, diseñado para ser compartido con el equipo de **Frontend** y facilitar la integración.

## 📦 Contenido del PDF

El archivo `API_SCHEMA.pdf` incluye:

### 1. **Portada**
- Nombre del proyecto
- Versión de la API
- Descripción general
- Estadísticas (total de endpoints, rutas, componentes)

### 2. **Tabla de Contenidos**
- Organización por categorías
- Contador de endpoints por categoría

### 3. **Endpoints Detallados** (53 endpoints)
Para cada endpoint se documenta:
- **Método HTTP** (GET, POST, PUT, PATCH, DELETE)
- **Ruta** (path)
- **Resumen** (summary)
- **Descripción detallada**
- **Parámetros** (query, path, header)
- **Cuerpo de solicitud** (request body) con Content-Type
- **Respuestas** (códigos de estado con descripciones)

### 4. **Modelos de Datos (Schemas)**
- Definición de todos los schemas/modelos
- Campos con tipos y descripciones
- Validaciones y restricciones

### 5. **Categorías de Endpoints**

#### 📦 Autenticación (3 endpoints)
- Login JWT
- Refresh token
- Verify token

#### 👥 Usuarios (7 endpoints)
- CRUD completo de usuarios
- Perfil de usuario autenticado

#### 🛍️ Productos (6 endpoints)
- CRUD de productos
- Listado y búsqueda

#### 📁 Categorías (6 endpoints)
- CRUD de categorías de productos

#### 🛒 Órdenes Cliente (5 endpoints)
- Crear orden
- Listar mis órdenes
- Ver detalle

#### 💳 Stripe Payments (2 endpoints)
- Crear sesión de checkout
- Webhook de pagos

#### 🎤 NLP Cart (2 endpoints)
- Agregar productos con lenguaje natural
- Sugerencias de productos

#### 👨‍💼 Admin Panel (6 endpoints)
- Dashboard con estadísticas
- Lista de todas las órdenes
- Gestión de usuarios
- Analytics de ventas

#### 📊 Reportes (6 endpoints)
- Reportes de ventas (PDF/Excel)
- Reportes de productos (PDF/Excel)
- Parser dinámico con IA
- Facturas/comprobantes

#### 🤖 ML Predictions (1 endpoint)
- Predicciones de ventas futuras

#### 📚 Documentación (3 endpoints)
- Swagger UI
- ReDoc
- Schema JSON

#### ⭐ Reseñas (5 endpoints)
- CRUD de reseñas de productos
- Rating de 1-5 estrellas

#### 🎯 Recomendaciones (1 endpoint)
- Productos recomendados (collaborative filtering)

#### ⚡ Cache (endpoints con Redis)
- Dashboard con caché de 5min
- Auto-invalidación

## 🚀 Cómo se Generó

El PDF fue generado automáticamente usando:

```bash
python generate_schema_pdf.py
```

### Tecnologías Utilizadas:
- **drf-spectacular**: Para generar el schema OpenAPI
- **ReportLab**: Para crear el PDF con formato profesional
- **Django REST Framework**: Framework base

## 📝 Uso para Frontend

### 1. **Consulta Rápida**
- Abre `API_SCHEMA.pdf`
- Busca el endpoint que necesitas (Ctrl+F)
- Copia la ruta y el formato de request/response

### 2. **Ejemplos de Request**

Cada endpoint incluye:
- Parámetros requeridos
- Formato del body (JSON)
- Headers necesarios (Authorization: Bearer TOKEN)

### 3. **Ejemplos de Response**

Cada endpoint documenta:
- Códigos de estado (200, 201, 400, 404, etc.)
- Estructura de la respuesta JSON
- Campos disponibles

### 4. **Tipos de Datos**

Consulta la sección "Modelos de Datos" para ver:
- Estructura exacta de cada modelo
- Tipos de cada campo (string, integer, boolean, etc.)
- Validaciones (required, min, max, etc.)

## 🔄 Actualización

Para regenerar el PDF con cambios recientes:

```bash
# Asegúrate de que el servidor Django esté configurado
python generate_schema_pdf.py
```

El script generará un nuevo `API_SCHEMA.pdf` con todos los endpoints actualizados.

## 📊 Estadísticas Actuales

- **Total de Endpoints**: 53
- **Categorías**: 13
- **Tasa de Éxito de Tests**: 98.2%
- **Versión**: 1.0.0
- **Última Actualización**: Octubre 2025

## 🎨 Características del PDF

### Visual
- **Código de colores** por método HTTP:
  - GET: Azul (#61affe)
  - POST: Verde (#49cc90)
  - PUT: Naranja (#fca130)
  - PATCH: Turquesa (#50e3c2)
  - DELETE: Rojo (#f93e3e)

### Navegación
- **Tabla de contenidos** con categorías
- **Separadores de sección** para fácil lectura
- **Formato profesional** con tablas y estilos

### Información Completa
- **Parámetros detallados** (nombre, tipo, requerido, descripción)
- **Respuestas documentadas** (código, descripción, schema)
- **Request body schemas** (Content-Type, estructura)

## 🔗 Recursos Adicionales

### Documentación Interactiva (localhost)
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema JSON**: http://localhost:8000/api/schema/

### Casos de Uso
Consulta `CASOS_DE_USO.md` para ejemplos completos de uso con:
- Flujos de trabajo
- JSON de ejemplo
- Casos especiales
- Mejores prácticas

## 💡 Tips para Frontend

1. **Autenticación**: Todos los endpoints (excepto login y registro) requieren:
   ```
   Authorization: Bearer <access_token>
   ```

2. **Content-Type**: La mayoría de endpoints usan:
   ```
   Content-Type: application/json
   ```

3. **CORS**: Configurado para aceptar requests desde el frontend

4. **Paginación**: Endpoints de lista incluyen paginación automática

5. **Filtros**: Muchos endpoints GET aceptan parámetros de filtrado

## 📞 Soporte

Si tienes dudas sobre algún endpoint:
1. Revisa el PDF
2. Consulta la documentación interactiva (Swagger)
3. Revisa `CASOS_DE_USO.md`
4. Ejecuta los tests: `.\test_api.ps1`

---

**Generado automáticamente por SmartSales365**  
*Documentación técnica completa para integración con Frontend*
