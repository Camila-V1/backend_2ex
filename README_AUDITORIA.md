# ✅ Sistema de Auditoría - LISTO PARA USAR

## 🎯 ¿Qué se implementó?

Sistema completo de bitácora/auditoría que registra **TODO** automáticamente:

✅ **17 tipos de acciones**: Login, CRUD productos, órdenes, reportes, NLP, errores, etc.
✅ **IP incluida**: Captura IP real del cliente (soporta proxies)
✅ **10+ filtros**: Por acción, severidad, usuario, IP, fechas, objetos, búsqueda
✅ **Exportar a PDF**: Reporte formateado con tabla profesional
✅ **Exportar a Excel**: Archivo .xlsx con estilos y formato

## 🚀 ¿Cómo usar?

### 1. Iniciar servidor
```bash
python manage.py runserver
```

### 2. Probar el sistema
```bash
python test_audit_system.py
```

Este script hará:
- Generar actividad de prueba
- Mostrar logs registrados
- Mostrar estadísticas
- Probar todos los filtros
- Descargar PDF de prueba
- Descargar Excel de prueba

## 📡 Endpoints API

**Acceso**: Solo administradores con token JWT

```bash
# Listar logs (con paginación)
GET /api/audit/

# Estadísticas del sistema
GET /api/audit/stats/

# Descargar PDF
GET /api/audit/export_pdf/

# Descargar Excel
GET /api/audit/export_excel/
```

## 🔍 Ejemplos de Filtros

```bash
# Ver solo logins
GET /api/audit/?action=LOGIN

# Ver errores
GET /api/audit/?severity=ERROR

# Ver actividad del usuario admin
GET /api/audit/?username=admin

# Ver actividad desde una IP
GET /api/audit/?ip_address=127.0.0.1

# Ver logs de hoy
GET /api/audit/?start_date=2025-01-26

# Buscar en descripciones
GET /api/audit/?search=payment

# Combinar filtros
GET /api/audit/?action=LOGIN_FAILED&start_date=2025-01-20&severity=ERROR
```

## 📊 Ver en el Admin

```
http://localhost:8000/admin/audit_log/auditlog/
```

Con usuario: `admin` / contraseña: `admin123`

## 🎨 Funciona Automáticamente

**NO necesitas código adicional!** El middleware captura todas las peticiones:

- Cuando un usuario hace login → Se registra automáticamente
- Cuando se crea un producto → Se registra automáticamente
- Cuando hay un error → Se registra automáticamente
- Cuando se hace una consulta NLP → Se registra automáticamente

## 📁 Archivos Creados

```
audit_log/
├── models.py          # Modelo AuditLog con 17 acciones
├── serializers.py     # Serializers para API
├── middleware.py      # Captura automática de peticiones
├── views.py           # ViewSet con stats y exports
├── urls.py            # Routing de la API
└── admin.py           # Interfaz del admin Django

test_audit_system.py   # Script de pruebas completo
SISTEMA_AUDITORIA.md   # Documentación completa
```

## ✨ Características Destacadas

- **100% Automático**: Sin código adicional necesario
- **IP Real**: Detecta IP real incluso detrás de proxies
- **Filtros Potentes**: Combinables para búsquedas complejas
- **Exports Profesionales**: PDF y Excel con formato
- **Estadísticas**: Dashboard con métricas
- **Seguro**: Solo admins, logs inmutables
- **Rápido**: Índices de BD para alto rendimiento

## 📞 ¿Problemas?

1. **No puedo acceder**: Verifica que seas administrador
2. **No veo logs**: Genera actividad haciendo peticiones al API
3. **Error 500**: Verifica que el servidor esté corriendo
4. **Permisos**: Solo usuarios con `is_staff=True` pueden acceder

---

**¡Sistema 100% funcional y listo para producción! 🚀**

Para más detalles, lee: `SISTEMA_AUDITORIA.md`
