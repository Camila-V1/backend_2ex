# 📋 Sistema de Auditoría y Bitácora - SmartSales365

## 🎯 Descripción General

Sistema completo de auditoría que registra **automáticamente** todas las acciones en el sistema, incluyendo:

- ✅ **Todos los tipos de acciones**: Login, logout, CRUD de productos, órdenes, reportes, consultas NLP, etc.
- ✅ **Información de IP**: Captura la IP real del cliente (incluyendo X-Forwarded-For para proxies)
- ✅ **Filtros avanzados**: Por acción, severidad, usuario, IP, fechas, objetos, búsqueda de texto
- ✅ **Exportación a PDF**: Genera reportes en PDF con formato profesional
- ✅ **Exportación a Excel**: Genera archivos .xlsx con estilos y formato

## 📦 Componentes Implementados

### 1. Modelo de Datos (`audit_log/models.py`)

```python
class AuditLog(models.Model):
    # 17 tipos de acciones
    LOGIN, LOGOUT, LOGIN_FAILED
    USER_CREATE, USER_UPDATE, USER_DELETE
    PRODUCT_CREATE, PRODUCT_UPDATE, PRODUCT_DELETE, PRODUCT_VIEW
    ORDER_CREATE, ORDER_UPDATE, ORDER_DELETE, ORDER_PAYMENT, ORDER_CANCEL
    REPORT_GENERATE, REPORT_DOWNLOAD
    NLP_QUERY, SYSTEM_ERROR, PERMISSION_DENIED, DATA_EXPORT
    
    # 4 niveles de severidad
    INFO, WARNING, ERROR, CRITICAL
    
    # Campos principales
    - action: Tipo de acción realizada
    - severity: Nivel de severidad
    - user: Usuario que realizó la acción (opcional)
    - username: Nombre de usuario (guardado por si se elimina el usuario)
    - ip_address: Dirección IP del cliente
    - user_agent: Navegador/cliente utilizado
    - method: Método HTTP (GET, POST, PUT, DELETE)
    - path: Ruta de la URL accedida
    - description: Descripción detallada
    - object_type: Tipo de objeto afectado (Product, Order, etc.)
    - object_id: ID del objeto afectado
    - object_repr: Representación del objeto
    - extra_data: Datos adicionales en formato JSON
    - timestamp: Fecha y hora del registro
    - success: Si la acción fue exitosa
    - error_message: Mensaje de error si falló
```

### 2. Middleware Automático (`audit_log/middleware.py`)

El middleware captura **automáticamente** todas las peticiones HTTP y crea registros de auditoría:

- ✅ Extrae la IP real del cliente (soporta X-Forwarded-For)
- ✅ Determina el tipo de acción basado en la URL y método HTTP
- ✅ Determina la severidad basado en el código de respuesta
- ✅ Captura información del usuario autenticado
- ✅ Extrae información de objetos desde la URL
- ✅ Ignora archivos estáticos y media

**Mapeo automático de rutas:**
```
/api/token/ + POST + 200 → LOGIN
/api/token/ + POST + 401 → LOGIN_FAILED
/api/products/ + POST → PRODUCT_CREATE
/api/products/ + GET → PRODUCT_VIEW
/api/orders/ + POST → ORDER_CREATE
/api/orders/natural-language/ → NLP_QUERY
/api/reports/ → REPORT_GENERATE
```

### 3. API REST (`audit_log/views.py`)

**Endpoints disponibles:**

#### 📋 Listar logs
```
GET /api/audit/
```
Retorna lista paginada de logs con todos los filtros aplicables.

#### 🔍 Detalle de log
```
GET /api/audit/{id}/
```
Retorna información detallada de un log específico.

#### 📊 Estadísticas
```
GET /api/audit/stats/
```
Retorna estadísticas del sistema:
```json
{
  "total_logs": 1234,
  "last_24_hours": 156,
  "last_week": 789,
  "success_count": 1100,
  "error_count": 134,
  "by_action": [
    {"action": "LOGIN", "count": 245},
    {"action": "PRODUCT_VIEW", "count": 189},
    ...
  ],
  "by_severity": [...],
  "by_user": [top 10 usuarios],
  "by_ip": [top 10 IPs]
}
```

#### 📄 Exportar a PDF
```
GET /api/audit/export_pdf/?action=LOGIN&start_date=2025-01-01
```
Genera y descarga un PDF con los logs filtrados (máximo 1000 registros).
- Formato profesional con tabla
- Incluye: Fecha/Hora, Acción, Usuario, IP, Estado
- Nombre de archivo: `auditoria_YYYYMMDD_HHMMSS.pdf`

#### 📊 Exportar a Excel
```
GET /api/audit/export_excel/?severity=ERROR&start_date=2025-01-01
```
Genera y descarga un archivo Excel con los logs filtrados (máximo 5000 registros).
- 12 columnas con todos los datos
- Formato con estilos: encabezados azules, bordes, alineación
- Nombre de archivo: `auditoria_YYYYMMDD_HHMMSS.xlsx`

## 🔧 Parámetros de Filtrado

Todos los endpoints soportan los siguientes filtros (como query parameters):

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `action` | Tipo de acción | `?action=LOGIN` |
| `severity` | Nivel de severidad | `?severity=ERROR` |
| `user_id` | ID del usuario | `?user_id=1` |
| `username` | Nombre de usuario | `?username=admin` |
| `ip_address` | Dirección IP | `?ip_address=127.0.0.1` |
| `object_type` | Tipo de objeto | `?object_type=Product` |
| `object_id` | ID del objeto | `?object_id=5` |
| `start_date` | Fecha inicio | `?start_date=2025-01-01` |
| `end_date` | Fecha fin | `?end_date=2025-12-31` |
| `success` | Solo exitosos/fallidos | `?success=true` |
| `search` | Búsqueda de texto | `?search=error` |

**Ejemplos de uso combinado:**
```bash
# Logins fallidos de las últimas 24 horas
GET /api/audit/?action=LOGIN_FAILED&start_date=2025-01-24

# Todos los errores de un usuario específico
GET /api/audit/?severity=ERROR&username=admin

# Todas las acciones sobre un producto específico
GET /api/audit/?object_type=Product&object_id=10

# Búsqueda de texto en descripciones
GET /api/audit/?search=payment failed
```

## 🚀 Instalación y Configuración

### Paso 1: Ya está instalado! ✅

El sistema ya está completamente configurado:

1. ✅ App `audit_log` agregada a `INSTALLED_APPS`
2. ✅ Middleware `AuditMiddleware` agregado a `MIDDLEWARE`
3. ✅ URLs configuradas en `/api/audit/`
4. ✅ Dependencia `django-filter` instalada
5. ✅ Migraciones aplicadas a la base de datos

### Paso 2: Probar el sistema

```bash
# 1. Iniciar el servidor
python manage.py runserver

# 2. En otra terminal, ejecutar el script de pruebas
python test_audit_system.py
```

El script de pruebas (`test_audit_system.py`) realizará:
- ✅ Generación de actividad de prueba
- ✅ Consulta de logs
- ✅ Obtención de estadísticas
- ✅ Prueba de todos los filtros
- ✅ Generación de PDF
- ✅ Generación de Excel

## 📊 Acceso desde el Admin de Django

El sistema también está disponible en el panel de administración:

```
http://localhost:8000/admin/audit_log/auditlog/
```

Características del admin:
- ✅ Lista con campos importantes visibles
- ✅ Filtros por acción, severidad, fecha
- ✅ Búsqueda por usuario, IP, descripción
- ✅ Jerarquía por fecha
- ✅ Todos los campos en solo lectura (no se pueden modificar logs)
- ✅ Solo superusuarios pueden eliminar registros

## 📝 Uso desde el Frontend

### Ejemplo 1: Obtener lista de logs

```javascript
// Obtener logs con filtros
const response = await fetch('http://localhost:8000/api/audit/?action=LOGIN&start_date=2025-01-01', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

const data = await response.json();
console.log('Total logs:', data.count);
console.log('Logs:', data.results);
```

### Ejemplo 2: Obtener estadísticas

```javascript
const response = await fetch('http://localhost:8000/api/audit/stats/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const stats = await response.json();
console.log('Total de logs:', stats.total_logs);
console.log('Últimas 24h:', stats.last_24_hours);
console.log('Top acciones:', stats.by_action);
```

### Ejemplo 3: Descargar PDF

```javascript
// Descargar PDF con filtros
const response = await fetch('http://localhost:8000/api/audit/export_pdf/?severity=ERROR&start_date=2025-01-01', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const blob = await response.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'auditoria.pdf';
a.click();
```

### Ejemplo 4: Descargar Excel

```javascript
// Descargar Excel con filtros
const response = await fetch('http://localhost:8000/api/audit/export_excel/?action=ORDER_CREATE&start_date=2025-01-01', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const blob = await response.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'auditoria.xlsx';
a.click();
```

## 🔒 Seguridad y Permisos

- ✅ **Solo administradores**: Todos los endpoints requieren autenticación JWT y rol de administrador
- ✅ **Solo lectura**: No se pueden crear, editar o eliminar logs vía API
- ✅ **Logs inmutables**: Los campos son de solo lectura en el admin
- ✅ **Eliminación controlada**: Solo superusuarios pueden eliminar logs desde el admin

## 📈 Tipos de Acciones Registradas

| Acción | Cuándo se registra |
|--------|-------------------|
| `LOGIN` | Inicio de sesión exitoso |
| `LOGOUT` | Cierre de sesión |
| `LOGIN_FAILED` | Intento de login fallido |
| `USER_CREATE` | Creación de nuevo usuario |
| `USER_UPDATE` | Actualización de usuario |
| `USER_DELETE` | Eliminación de usuario |
| `PRODUCT_CREATE` | Creación de producto |
| `PRODUCT_UPDATE` | Actualización de producto |
| `PRODUCT_DELETE` | Eliminación de producto |
| `PRODUCT_VIEW` | Consulta de productos |
| `ORDER_CREATE` | Creación de orden |
| `ORDER_UPDATE` | Actualización de orden |
| `ORDER_DELETE` | Eliminación de orden |
| `ORDER_PAYMENT` | Procesamiento de pago |
| `ORDER_CANCEL` | Cancelación de orden |
| `REPORT_GENERATE` | Generación de reporte |
| `REPORT_DOWNLOAD` | Descarga de reporte |
| `NLP_QUERY` | Consulta con lenguaje natural |
| `SYSTEM_ERROR` | Error del sistema |
| `PERMISSION_DENIED` | Acceso denegado |
| `DATA_EXPORT` | Exportación de datos |

## 🎨 Niveles de Severidad

| Nivel | Cuándo se asigna |
|-------|-----------------|
| `INFO` | Operaciones normales (código 200-299) |
| `WARNING` | Operaciones con advertencias (código 300-399) |
| `ERROR` | Errores del cliente (código 400-499) |
| `CRITICAL` | Errores del servidor (código 500-599) |

## 🔍 Ejemplos de Uso Común

### Ver todos los logins fallidos de hoy
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/audit/?action=LOGIN_FAILED&start_date=$(date +%Y-%m-%d)"
```

### Ver todas las acciones de un usuario específico
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/audit/?username=admin"
```

### Ver todos los errores críticos
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/audit/?severity=CRITICAL"
```

### Ver todas las consultas NLP de la última semana
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/audit/?action=NLP_QUERY&start_date=$(date -d '7 days ago' +%Y-%m-%d)"
```

### Descargar PDF de todos los errores
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/audit/export_pdf/?severity=ERROR" \
  -o auditoria_errores.pdf
```

### Descargar Excel de actividad de un usuario
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/audit/export_excel/?username=admin" \
  -o auditoria_admin.xlsx
```

## 📞 Soporte

Si encuentras problemas:

1. Verifica que el servidor esté corriendo: `python manage.py runserver`
2. Verifica que tengas rol de administrador
3. Ejecuta el script de pruebas: `python test_audit_system.py`
4. Revisa los logs en el admin de Django

## 🎉 Características Destacadas

- ✅ **100% Automático**: No necesitas llamar manualmente a funciones de logging
- ✅ **IP Real**: Soporta proxies y load balancers (X-Forwarded-For)
- ✅ **Filtros Potentes**: 10+ parámetros de filtrado combinables
- ✅ **Exportación Profesional**: PDF y Excel con formato y estilos
- ✅ **Estadísticas**: Dashboard completo con métricas
- ✅ **Seguro**: Solo administradores, logs inmutables
- ✅ **Escalable**: Índices de base de datos para alto rendimiento
- ✅ **Extensible**: Campo JSON para datos adicionales

---

**Sistema implementado y listo para usar! 🚀**
