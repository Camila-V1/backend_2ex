# 🎯 Previsualización de Reportes - RESUMEN RÁPIDO

## ✅ ¿Qué se hizo?

Se agregaron **3 nuevos endpoints** que retornan **JSON** para que el frontend pueda mostrar los datos **ANTES** de descargar el PDF/Excel.

## 📡 Nuevos Endpoints

### 1. Preview de Ventas
```bash
GET /api/reports/sales/preview/?start_date=2025-01-01&end_date=2025-01-31
```
Retorna JSON con:
- Total de órdenes
- Total de ingresos
- Lista de todas las órdenes con detalles (cliente, items, totales)

### 2. Preview de Productos
```bash
GET /api/reports/products/preview/
```
Retorna JSON con:
- Total de productos
- Total de stock
- Valor total del inventario
- Lista de todos los productos con detalles

### 3. Preview Dinámico (Lenguaje Natural)
```bash
POST /api/reports/dynamic-parser/preview/
Body: {"prompt": "ventas del mes de octubre agrupado por producto"}
```
Retorna JSON con:
- Título del reporte
- Encabezados de columnas
- Datos procesados según el prompt
- Total de registros

---

## 🔄 Flujo Recomendado

### En el Frontend:

1. **Usuario ingresa parámetros** (fechas, prompt, etc.)
2. **Botón "Vista Previa"** → Llama a `/preview/` → Recibe JSON
3. **Mostrar datos en tabla** con todos los detalles
4. **Usuario revisa los datos**
5. **Botones de descarga:**
   - "Descargar PDF" → Llama al endpoint original con `?format=pdf`
   - "Descargar Excel" → Llama al endpoint original con `?format=excel`

---

## 📊 Ejemplo en React/JavaScript

```javascript
// 1. Previsualizar
const handlePreview = async () => {
  const response = await fetch(
    `http://localhost:8000/api/reports/sales/preview/?start_date=${startDate}&end_date=${endDate}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  const data = await response.json();
  setPreviewData(data); // Mostrar en tabla
};

// 2. Descargar PDF (después de ver preview)
const handleDownloadPDF = async () => {
  const response = await fetch(
    `http://localhost:8000/api/reports/sales/?start_date=${startDate}&end_date=${endDate}&format=pdf`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `ventas_${startDate}_${endDate}.pdf`;
  a.click();
};
```

---

## 🧪 Probar el Sistema

```bash
# 1. Iniciar servidor
python manage.py runserver

# 2. En otra terminal, ejecutar pruebas
python test_report_preview.py
```

El script probará:
- ✅ Preview de ventas
- ✅ Preview de productos  
- ✅ Preview dinámico (3 prompts diferentes)
- ✅ Descarga de PDF/Excel (endpoints originales)

---

## ✨ Ventajas

- ✅ **Usuario ve los datos primero** antes de descargar
- ✅ **Ahorra ancho de banda** (no descarga si no es necesario)
- ✅ **Mejor UX** - feedback inmediato
- ✅ **Validación** - detectar errores antes
- ✅ **Sin modificar descarga** - endpoints originales intactos

---

## 📝 Archivos Modificados

```
reports/
├── serializers.py  ✅ Agregados 3 serializers de preview
├── views.py        ✅ Agregadas 3 vistas de preview
└── urls.py         ✅ Agregadas 3 rutas de preview

Nuevos archivos:
├── GUIA_PREVISUALIZACION_REPORTES.md  📖 Documentación completa
└── test_report_preview.py             🧪 Script de pruebas
```

---

## 🔒 Permisos

Todos los endpoints requieren:
- JWT Token válido
- Rol de administrador (`is_staff=True`)

---

## 🚀 ¡Listo para usar!

El backend ahora soporta:
1. ✅ Ver datos en JSON (nuevos endpoints `/preview/`)
2. ✅ Descargar PDF/Excel (endpoints originales)
3. ✅ Ambos funcionan independientemente

**El frontend puede implementar el flujo que prefieras:**
- Solo preview
- Solo descarga
- Preview → Descarga (recomendado)
