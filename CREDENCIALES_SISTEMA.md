# 🔐 Credenciales del Sistema

Este documento contiene todas las credenciales de usuarios creadas por el script `seed_complete_database.py`.

---

## 📋 Índice
- [👥 Clientes (CLIENTE)](#-clientes-cliente)
- [👔 Managers (MANAGER)](#-managers-manager)
- [⚙️ Administradores (ADMIN)](#️-administradores-admin)
- [📊 Resumen](#-resumen)
- [🔑 Información Importante](#-información-importante)

---

## 👥 Clientes (CLIENTE)

Los clientes pueden:
- ✅ Ver y comprar productos
- ✅ Crear órdenes
- ✅ Solicitar devoluciones
- ✅ Ver su billetera virtual
- ✅ Consultar sus transacciones

### Lista de Clientes

| #  | Usuario          | Contraseña   | Email                           | Nombre Completo  |
|----|------------------|--------------|---------------------------------|------------------|
| 1  | `juan_cliente`   | `password123`| juan.cliente@example.com        | Juan Cliente     |
| 2  | `maria_gomez`    | `password123`| maria.gomez@example.com         | María Gómez      |
| 3  | `pedro_lopez`    | `password123`| pedro.lopez@example.com         | Pedro López      |
| 4  | `ana_martinez`   | `password123`| ana.martinez@example.com        | Ana Martínez     |
| 5  | `luis_rodriguez` | `password123`| luis.rodriguez@example.com      | Luis Rodríguez   |
| 6  | `carmen_sanchez` | `password123`| carmen.sanchez@example.com      | Carmen Sánchez   |
| 7  | `jorge_ramirez`  | `password123`| jorge.ramirez@example.com       | Jorge Ramírez    |
| 8  | `sofia_torres`   | `password123`| sofia.torres@example.com        | Sofía Torres     |
| 9  | `diego_flores`   | `password123`| diego.flores@example.com        | Diego Flores     |
| 10 | `laura_rivera`   | `password123`| laura.rivera@example.com        | Laura Rivera     |

### 🎯 Ejemplo de Uso (Cliente)

```bash
# Login
POST /api/users/login/
{
    "username": "juan_cliente",
    "password": "password123"
}

# Ver mis órdenes
GET /api/orders/my_orders/
Authorization: Bearer <token>

# Solicitar devolución
POST /api/returns/
Authorization: Bearer <token>
{
    "order_id": 1,
    "product_id": 5,
    "reason": "DEFECTIVE",
    "description": "El producto no funciona correctamente",
    "refund_method": "WALLET"
}
```

---

## 👔 Managers (MANAGER)

Los managers pueden:
- ✅ Todo lo que pueden hacer los clientes
- ✅ Ver todas las devoluciones del sistema
- ✅ Aprobar/rechazar devoluciones
- ✅ Solicitar evaluación física de productos
- ✅ Recibir notificaciones por email de nuevas devoluciones

### Lista de Managers

| #  | Usuario          | Contraseña   | Email                           | Nombre Completo  |
|----|------------------|--------------|---------------------------------|------------------|
| 1  | `carlos_manager` | `manager123` | carlos_manager@example.com      | Carlos Manager   |
| 2  | `ana_manager`    | `manager123` | ana_manager@example.com         | Ana Manager      |
| 3  | `luis_manager`   | `manager123` | luis_manager@example.com        | Luis Manager     |
| 4  | `sofia_manager`  | `manager123` | sofia_manager@example.com       | Sofia Manager    |
| 5  | `miguel_manager` | `manager123` | miguel_manager@example.com      | Miguel Manager   |
| 6  | `laura_manager`  | `manager123` | laura_manager@example.com       | Laura Manager    |

### 🎯 Ejemplo de Uso (Manager)

```bash
# Login
POST /api/users/login/
{
    "username": "carlos_manager",
    "password": "manager123"
}

# Ver todas las devoluciones
GET /api/returns/
Authorization: Bearer <token>

# Aprobar una devolución
POST /api/returns/{id}/approve/
Authorization: Bearer <token>
{
    "comments": "Producto defectuoso verificado. Reembolso aprobado."
}

# Rechazar una devolución
POST /api/returns/{id}/reject/
Authorization: Bearer <token>
{
    "comments": "El producto está en perfectas condiciones. Solicitud rechazada."
}

# Solicitar evaluación física
POST /api/returns/{id}/request_physical_evaluation/
Authorization: Bearer <token>
{
    "comments": "Se requiere revisión física para determinar el origen del defecto."
}
```

---

## ⚙️ Administradores (ADMIN)

Los administradores tienen:
- ✅ Acceso completo al sistema
- ✅ Permisos de superusuario
- ✅ Acceso al panel de Django Admin (`/admin/`)
- ✅ Todo lo que pueden hacer managers y clientes

### Lista de Administradores

| #  | Usuario       | Contraseña | Email                    | Nombre Completo |
|----|---------------|------------|--------------------------|-----------------|
| 1  | `admin`       | `admin123` | admin@example.com        | Admin System    |
| 2  | `superadmin`  | `admin123` | superadmin@example.com   | Super Admin     |

### 🎯 Ejemplo de Uso (Admin)

```bash
# Login
POST /api/users/login/
{
    "username": "admin",
    "password": "admin123"
}

# Acceder al panel de administración de Django
http://localhost:8000/admin/
Usuario: admin
Contraseña: admin123
```

---

## 📊 Resumen

| Rol      | Cantidad | Contraseña por Defecto | Permisos                                          |
|----------|----------|------------------------|---------------------------------------------------|
| CLIENTE  | 10       | `password123`          | Comprar, solicitar devoluciones, ver billetera   |
| MANAGER  | 6        | `manager123`           | Todo lo anterior + gestionar devoluciones        |
| ADMIN    | 2        | `admin123`             | Acceso completo + Django Admin                   |
| **TOTAL**| **18**   | -                      | -                                                 |

---

## 🔑 Información Importante

### 🔒 Seguridad

⚠️ **IMPORTANTE**: Estas credenciales son **solo para desarrollo y pruebas**. 

**Nunca uses estas contraseñas en producción:**
- ❌ `password123`
- ❌ `manager123`
- ❌ `admin123`

En producción, debes:
1. ✅ Usar contraseñas fuertes y únicas
2. ✅ Implementar políticas de cambio de contraseña
3. ✅ Activar autenticación de dos factores (2FA)
4. ✅ Limitar intentos de login
5. ✅ Usar variables de entorno para credenciales sensibles

### 📧 Emails

Todos los emails siguen el patrón:
- **Clientes**: `{username}@example.com`
- **Managers**: `{username}@example.com`
- **Admins**: `{username}@example.com`

Los managers reciben notificaciones por email cuando:
- ✉️ Un cliente crea una nueva devolución
- ✉️ Se requiere una evaluación física
- ✉️ Hay cambios de estado en devoluciones

### 🎭 Roles y Permisos

```python
# Jerarquía de permisos
ADMIN > MANAGER > CLIENTE

# Ejemplo de verificación en el backend:
if user.role == 'ADMIN':
    # Acceso total
elif user.role == 'MANAGER':
    # Puede gestionar devoluciones
elif user.role == 'CLIENTE':
    # Solo sus propios recursos
```

### 🧪 Testing Rápido

Para probar el sistema rápidamente, usa estos usuarios recomendados:

```bash
# Cliente para hacer compras y devoluciones
Usuario: juan_cliente
Password: password123

# Manager para aprobar/rechazar
Usuario: carlos_manager
Password: manager123

# Admin para acceso total
Usuario: admin
Password: admin123
```

### 💾 Datos Generados

Cuando ejecutas `seed_complete_database.py`, se crean:

- ✅ **10 categorías** de productos
- ✅ **37 productos** con precios y stock realistas
- ✅ **18 usuarios** (distribuidos en 3 roles)
- ✅ **80+ órdenes** con diferentes estados
- ✅ **20+ devoluciones** en varios estados
- ✅ **5+ billeteras** con saldo y transacciones
- ✅ **Garantías automáticas** para órdenes entregadas

### 🔄 Regenerar Credenciales

Para volver a poblar la base de datos:

```bash
# Ejecutar el poblador
python seed_complete_database.py

# Responder "SI" cuando pregunte si deseas limpiar la BD
¿Deseas limpiar la base de datos antes de poblar? (SI/NO): SI
```

### 📚 Documentación Relacionada

- **Autenticación**: `frontend_docs/01_AUTENTICACION.md`
- **Sistema de Devoluciones**: `frontend_docs/03_DEVOLUCIONES.md`
- **Billetera Virtual**: `frontend_docs/04_BILLETERA_VIRTUAL.md`
- **Errores Comunes**: `frontend_docs/09_ERRORES_COMUNES.md`

---

## 📞 Contacto y Soporte

Si tienes problemas con las credenciales:

1. 🔄 Verifica que la base de datos esté poblada: `python seed_complete_database.py`
2. 🔍 Revisa los logs del servidor: `python manage.py runserver`
3. 🧪 Prueba el endpoint de login con Postman o cURL
4. 📖 Consulta la documentación en `frontend_docs/`

---

**Última actualización**: 10 de noviembre de 2025  
**Script de generación**: `seed_complete_database.py` (v1.0)  
**Commit**: `4260333`
