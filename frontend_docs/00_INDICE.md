# 📚 DOCUMENTACIÓN PARA FRONTEND - SISTEMA DE DEVOLUCIONES

## 📋 Índice de Documentación

Esta carpeta contiene toda la información necesaria para que el equipo de frontend pueda integrar el sistema de devoluciones y garantías.

### 📂 Archivos Disponibles:

1. **`01_AUTENTICACION.md`** - Sistema de login y tokens JWT
2. **`02_PRODUCTOS_Y_ORDENES.md`** - Endpoints de productos y órdenes
3. **`03_DEVOLUCIONES.md`** - Sistema completo de devoluciones (PRINCIPAL)
4. **`04_BILLETERA_VIRTUAL.md`** - Wallet y transacciones
5. **`05_EMAILS.md`** - Sistema de notificaciones por email
6. **`06_EJEMPLOS_COMPLETOS.md`** - Ejemplos de código JavaScript/React
7. **`07_FLUJO_USUARIO.md`** - Diagramas de flujo para cada rol
8. **`08_ESTADOS_Y_VALIDACIONES.md`** - Reglas de negocio y validaciones
9. **`09_ERRORES_COMUNES.md`** - Manejo de errores y troubleshooting

---

## 🚀 Inicio Rápido

### URLs Base:
- **Desarrollo:** `http://localhost:8000/api`
- **Producción:** `TU_SERVIDOR/api`

### Autenticación:
Todos los endpoints requieren token JWT en el header:
```javascript
headers: {
  'Authorization': 'Bearer TU_TOKEN_AQUI',
  'Content-Type': 'application/json'
}
```

### Roles de Usuario:
- **CLIENTE** - Puede solicitar devoluciones, ver sus propias devoluciones
- **MANAGER** - Puede gestionar todas las devoluciones, aprobar/rechazar
- **ADMIN** - Acceso completo al sistema

---

## 📊 Endpoints Principales (Resumen)

| Categoría | Método | Endpoint | Descripción |
|-----------|--------|----------|-------------|
| Auth | POST | `/token/` | Login (obtener token) |
| Auth | GET | `/users/profile/` | Perfil del usuario |
| Productos | GET | `/products/` | Listar productos |
| Órdenes | GET | `/orders/` | Mis órdenes |
| Devoluciones | POST | `/deliveries/returns/` | Solicitar devolución |
| Devoluciones | GET | `/deliveries/returns/` | Listar devoluciones |
| Devoluciones | GET | `/deliveries/returns/{id}/` | Ver detalles |
| Devoluciones | POST | `/deliveries/returns/{id}/send_to_evaluation/` | Enviar a evaluación |
| Devoluciones | POST | `/deliveries/returns/{id}/approve/` | Aprobar devolución |
| Billetera | GET | `/users/wallets/my_balance/` | Ver saldo |
| Billetera | GET | `/users/wallet-transactions/my_transactions/` | Ver transacciones |

---

## 🎯 Casos de Uso Implementados

✅ **Cliente puede:**
1. Ver sus órdenes entregadas
2. Solicitar devolución de un producto
3. Ver el estado de sus devoluciones
4. Ver su billetera y transacciones

✅ **Manager puede:**
1. Ver todas las devoluciones pendientes
2. Enviar devoluciones a evaluación física
3. Aprobar devoluciones con reembolso
4. Rechazar devoluciones con justificación

✅ **Sistema automático:**
1. Crear billetera virtual al aprobar primera devolución
2. Procesar reembolso automáticamente
3. Enviar emails a managers al crear devolución
4. Actualizar estados y timestamps

---

## 📱 Pantallas Sugeridas para el Frontend

### Para Cliente:
1. **Mis Órdenes** - Lista de órdenes con botón "Solicitar Devolución"
2. **Solicitar Devolución** - Formulario con razón y descripción
3. **Mis Devoluciones** - Lista con estados y tracking
4. **Detalle de Devolución** - Ver progreso completo
5. **Mi Billetera** - Ver saldo y transacciones

### Para Manager:
1. **Dashboard Devoluciones** - Ver todas las pendientes
2. **Evaluar Devolución** - Ver detalles y enviar a evaluación
3. **Aprobar/Rechazar** - Formulario con notas y monto

---

## 🔗 Links Útiles

- **API Schema PDF:** Ver `API_SCHEMA.pdf` en la raíz del proyecto
- **Test de Flujo Completo:** Ver `test_flujo_completo_devoluciones.py`
- **Casos de Uso:** Ver `CASOS_DE_USO.md`

---

## 📞 Soporte

Si encuentras algún problema o necesitas aclaración sobre algún endpoint:
1. Revisa la documentación específica en esta carpeta
2. Ejecuta el script de prueba: `python test_flujo_completo_devoluciones.py`
3. Revisa los ejemplos de código en `06_EJEMPLOS_COMPLETOS.md`

---

**Última actualización:** 2025-11-10
**Versión API:** 1.0
**Estado:** ✅ Completamente funcional y probado
