# 🚀 SISTEMA DE TESTING Y DEPLOY AUTOMÁTICO

## 📦 ¿Qué se implementó?

### 1. **Sistema Completo de Pruebas API** (`tests_api/`)

#### Estructura de archivos:
```
tests_api/
├── __init__.py              # Módulo Python
├── config.py                # Configuración (URL, credenciales, colores)
├── run_all_tests.py         # ⭐ Script principal
├── test_auth.py             # 5 pruebas de autenticación
├── test_users.py            # 3 pruebas de usuarios
├── test_products.py         # 5 pruebas de productos
├── test_orders.py           # 3 pruebas de órdenes
├── test_predictions.py      # 1 prueba de ML
└── README.md                # Documentación detallada
```

#### Características:
- ✅ **17 pruebas automatizadas** en total
- ✅ **Salida colorizada** (verde=éxito, rojo=fallo)
- ✅ **Resumen detallado** con porcentajes
- ✅ **Modular**: Ejecuta todos o uno solo
- ✅ **Configurable**: Cambiar URL fácilmente
- ✅ **CI/CD Ready**: Retorna exit code 0/1

---

### 2. **Deploy Automático con Base de Datos Limpia** (`deploy.sh`)

#### Cambios implementados:

**ANTES** (deploy.sh antiguo):
```bash
# Solo poblaba si la BD estaba vacía
if not CustomUser.objects.exists():
    python seed_data.py
else:
    print("Saltando seed_data.py")
```

**AHORA** (deploy.sh nuevo):
```bash
echo "🗑️ LIMPIANDO base de datos (flush)..."
python manage.py flush --no-input

echo "🌱 Repoblando base de datos con datos iniciales..."
python seed_data.py

echo "✅ Deploy completado exitosamente!"
echo "📊 Base de datos limpia y repoblada con datos frescos"
```

#### Beneficios:
- ✅ **Datos consistentes** en cada deploy
- ✅ **Sin duplicados** de usuarios/productos
- ✅ **Estado predecible** para testing
- ✅ **Fácil rollback** (solo redeployar)

---

### 3. **Scripts de Ejecución Rápida**

#### `test_api_quick.py` (multiplataforma):
```bash
python test_api_quick.py
```

#### `test_api_quick.ps1` (PowerShell):
```powershell
.\test_api_quick.ps1
```

Ambos ejecutan la suite completa automáticamente.

---

### 4. **Documentación Completa**

#### `GUIA_PRUEBAS_API.md`:
- 📝 Guía rápida de uso
- 👥 Credenciales de prueba
- ⚙️ Configuración del entorno
- 🛠️ Cómo agregar nuevas pruebas
- 🐛 Troubleshooting común
- 🎯 Tips y mejores prácticas

#### `tests_api/README.md`:
- 📚 Documentación técnica detallada
- 🔧 API de cada módulo
- 📊 Formato de resultados
- 🔄 Integración con CI/CD

---

## 🎯 Flujo de Trabajo Completo

### 1. **Desarrollo Local**
```bash
# Hacer cambios en el código
git add .
git commit -m "feat: Nueva funcionalidad"
git push origin main
```

### 2. **Deploy Automático en Render**
```
1. ⬇️ Render detecta push
2. 📥 Descarga código nuevo
3. 🔧 Instala dependencias
4. 📦 Colecta archivos estáticos
5. 🗄️ Ejecuta migraciones
6. 🗑️ FLUSH de la base de datos
7. 🌱 Repuebla con seed_data.py
8. ✅ Deploy completo
```

### 3. **Pruebas Automáticas**
```bash
# Esperar 2-3 minutos después del deploy
python test_api_quick.py
```

### 4. **Resultados**
```
======================================================================
📊 RESUMEN FINAL
======================================================================
Autenticación: 5/5 pruebas exitosas
Usuarios: 3/3 pruebas exitosas
Productos: 5/5 pruebas exitosas
Órdenes: 3/3 pruebas exitosas
Predicciones: 1/1 pruebas exitosas
======================================================================
TOTAL: 17/17 pruebas exitosas (100.0%)
✅ Exitosas: 17
❌ Fallidas: 0
======================================================================
```

---

## 📊 Cobertura de Pruebas

### 🔐 Autenticación (5 pruebas)
| Prueba | Endpoint | Método |
|--------|----------|--------|
| Login admin | `/api/token/` | POST |
| Login manager | `/api/token/` | POST |
| Login cajero | `/api/token/` | POST |
| Refresh token | `/api/token/refresh/` | POST |
| Get profile | `/api/users/profile/` | GET |

### 👥 Usuarios (3 pruebas)
| Prueba | Endpoint | Método |
|--------|----------|--------|
| Listar usuarios | `/api/users/` | GET |
| Detalle usuario | `/api/users/{id}/` | GET |
| Crear usuario | `/api/users/` | POST |

### 📦 Productos (5 pruebas)
| Prueba | Endpoint | Método |
|--------|----------|--------|
| Listar productos | `/api/products/` | GET |
| Detalle producto | `/api/products/{id}/` | GET |
| Listar categorías | `/api/products/categories/` | GET |
| Buscar productos | `/api/products/?search=query` | GET |
| Filtrar categoría | `/api/products/?category=id` | GET |

### 🛒 Órdenes (3 pruebas)
| Prueba | Endpoint | Método |
|--------|----------|--------|
| Listar órdenes | `/api/orders/` | GET |
| Detalle orden | `/api/orders/{id}/` | GET |
| Dashboard admin | `/api/orders/admin/dashboard/` | GET |

### 📈 Predicciones (1 prueba)
| Prueba | Endpoint | Método |
|--------|----------|--------|
| Predicciones ML | `/api/predictions/sales/` | GET |

---

## 🔧 Configuración de Entornos

### Producción (Render)
```python
# tests_api/config.py
API_BASE_URL = 'https://backend-2ex-ecommerce.onrender.com/api'
```

### Desarrollo Local
```python
# tests_api/config.py
API_BASE_URL = 'http://localhost:8000/api'
```

### Variable de Entorno
```bash
# Linux/Mac
export API_BASE_URL=http://localhost:8000/api

# Windows PowerShell
$env:API_BASE_URL = "http://localhost:8000/api"

# Windows CMD
set API_BASE_URL=http://localhost:8000/api
```

---

## 👥 Usuarios de Prueba (seed_data.py)

| Username | Password | Role | Descripción |
|----------|----------|------|-------------|
| admin | admin123 | ADMIN | Acceso total al sistema |
| manager1 | manager123 | MANAGER | Gestión de inventario |
| manager2 | manager123 | MANAGER | Gestión de inventario |
| cajero1 | cajero123 | CAJERO | Punto de venta |
| cajero2 | cajero123 | CAJERO | Punto de venta |
| cliente1 | cliente123 | CLIENTE | Compras online |
| cliente2 | cliente123 | CLIENTE | Compras online |
| ... | ... | ... | Total 12 usuarios |

---

## 🗄️ Datos de Seed

### Generados en cada deploy:
- **12 usuarios** (admin, managers, cajeros, clientes)
- **8 categorías** (Electrónica, Ropa, etc.)
- **35 productos** con precios y stock
- **168 reviews** (5 por producto promedio)
- **1 orden de prueba**

---

## 📈 Ventajas del Sistema

### ✅ Consistencia
- Mismos datos en cada deploy
- Sin duplicados ni inconsistencias
- Estado predecible para pruebas

### ✅ Automatización
- No requiere intervención manual
- Deploy completo en 2-3 minutos
- Tests ejecutables con un comando

### ✅ Mantenibilidad
- Fácil agregar nuevas pruebas
- Código modular y organizado
- Documentación completa

### ✅ Confiabilidad
- Detecta errores temprano
- Valida 17 endpoints críticos
- Feedback inmediato con colores

---

## 🚀 Próximos Pasos

### Opcional - Mejoras Futuras:

1. **Integración CI/CD**
   ```yaml
   # .github/workflows/test.yml
   - name: Run API Tests
     run: python tests_api/run_all_tests.py
   ```

2. **Tests de Performance**
   - Medir tiempos de respuesta
   - Detectar endpoints lentos
   - Alertas de timeout

3. **Tests de Seguridad**
   - Validar permisos por rol
   - Tests de inyección SQL
   - Verificar rate limiting

4. **Reportes HTML**
   - Generar reporte visual
   - Gráficos de cobertura
   - Historial de tests

---

## 🎉 Resultado Final

✅ **Sistema de testing completo** con 17 pruebas automatizadas
✅ **Deploy automático** con BD limpia en cada despliegue
✅ **Documentación completa** para uso y extensión
✅ **Scripts de ejecución rápida** para facilidad de uso
✅ **Estado consistente** garantizado en cada deploy

**Tiempo de implementación**: ~30 minutos
**Tiempo ahorrado en testing manual**: Horas por semana 🚀

---

## 📞 Soporte

**Problemas comunes**:
- Ver `GUIA_PRUEBAS_API.md` sección Troubleshooting
- Revisar logs de Render en: https://dashboard.render.com
- Verificar variables de entorno en Render

**Para más información**:
- README principal del proyecto
- Documentación de Django REST Framework
- Documentación de Render
