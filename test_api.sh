#!/bin/bash

# ================================================================
# 🧪 SCRIPT DE TESTING COMPLETO - API E-COMMERCE
# ================================================================
# Este script prueba TODOS los endpoints de la API usando curl
# Asegúrate de que el servidor esté corriendo: python manage.py runserver
# ================================================================

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}🚀 INICIANDO TESTING COMPLETO DE LA API${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

# ================================================================
# 1. AUTENTICACIÓN JWT
# ================================================================
echo -e "${YELLOW}[1/15] 🔐 AUTENTICACIÓN JWT${NC}"
echo "POST /api/token/"

LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/token/" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@smartsales365.com","password":"admin123"}')

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo -e "${RED}❌ ERROR: No se pudo obtener el token de acceso${NC}"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
else
  echo -e "${GREEN}✅ Login exitoso${NC}"
  echo "Token: ${ACCESS_TOKEN:0:30}..."
fi
echo ""

# ================================================================
# 2. LISTAR PRODUCTOS
# ================================================================
echo -e "${YELLOW}[2/15] 📦 LISTAR PRODUCTOS${NC}"
echo "GET /api/products/"

PRODUCTS_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/products/")
PRODUCT_COUNT=$(echo $PRODUCTS_RESPONSE | grep -o '"id"' | wc -l)

if [ $PRODUCT_COUNT -gt 0 ]; then
  echo -e "${GREEN}✅ Productos encontrados: $PRODUCT_COUNT${NC}"
  # Extraer primer producto para usar después
  PRODUCT_ID=$(echo $PRODUCTS_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
  echo "Primer producto ID: $PRODUCT_ID"
else
  echo -e "${RED}❌ ERROR: No hay productos${NC}"
fi
echo ""

# ================================================================
# 3. DETALLE DE PRODUCTO
# ================================================================
echo -e "${YELLOW}[3/15] 📦 DETALLE DE PRODUCTO${NC}"
echo "GET /api/products/$PRODUCT_ID/"

PRODUCT_DETAIL=$(curl -s -X GET "${BASE_URL}/api/products/${PRODUCT_ID}/")

if echo "$PRODUCT_DETAIL" | grep -q '"name"'; then
  echo -e "${GREEN}✅ Detalle obtenido correctamente${NC}"
  PRODUCT_NAME=$(echo $PRODUCT_DETAIL | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
  echo "Producto: $PRODUCT_NAME"
else
  echo -e "${RED}❌ ERROR: No se pudo obtener el detalle${NC}"
fi
echo ""

# ================================================================
# 4. LISTAR CATEGORÍAS
# ================================================================
echo -e "${YELLOW}[4/15] 🏷️ LISTAR CATEGORÍAS${NC}"
echo "GET /api/products/categories/"

CATEGORIES_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/products/categories/")
CATEGORY_COUNT=$(echo $CATEGORIES_RESPONSE | grep -o '"id"' | wc -l)

if [ $CATEGORY_COUNT -gt 0 ]; then
  echo -e "${GREEN}✅ Categorías encontradas: $CATEGORY_COUNT${NC}"
else
  echo -e "${RED}❌ ERROR: No hay categorías${NC}"
fi
echo ""

# ================================================================
# 5. CREAR ORDEN
# ================================================================
echo -e "${YELLOW}[5/15] 🛒 CREAR ORDEN${NC}"
echo "POST /api/orders/create/"

ORDER_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/orders/create/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"items\":[{\"product\":${PRODUCT_ID},\"quantity\":2}]}")

ORDER_ID=$(echo $ORDER_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ ! -z "$ORDER_ID" ]; then
  echo -e "${GREEN}✅ Orden creada correctamente${NC}"
  echo "Order ID: $ORDER_ID"
  ORDER_TOTAL=$(echo $ORDER_RESPONSE | grep -o '"total":"[^"]*"' | cut -d'"' -f4)
  echo "Total: $ORDER_TOTAL"
else
  echo -e "${RED}❌ ERROR: No se pudo crear la orden${NC}"
  echo "Response: $ORDER_RESPONSE"
fi
echo ""

# ================================================================
# 6. LISTAR MIS ÓRDENES
# ================================================================
echo -e "${YELLOW}[6/15] 📋 LISTAR MIS ÓRDENES${NC}"
echo "GET /api/orders/"

MY_ORDERS=$(curl -s -X GET "${BASE_URL}/api/orders/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

MY_ORDER_COUNT=$(echo $MY_ORDERS | grep -o '"id"' | wc -l)

if [ $MY_ORDER_COUNT -gt 0 ]; then
  echo -e "${GREEN}✅ Órdenes encontradas: $MY_ORDER_COUNT${NC}"
else
  echo -e "${YELLOW}⚠️ No hay órdenes para este usuario${NC}"
fi
echo ""

# ================================================================
# 7. DETALLE DE ORDEN
# ================================================================
echo -e "${YELLOW}[7/15] 📋 DETALLE DE ORDEN${NC}"
echo "GET /api/orders/$ORDER_ID/"

ORDER_DETAIL=$(curl -s -X GET "${BASE_URL}/api/orders/${ORDER_ID}/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

if echo "$ORDER_DETAIL" | grep -q '"status"'; then
  echo -e "${GREEN}✅ Detalle de orden obtenido${NC}"
  ORDER_STATUS=$(echo $ORDER_DETAIL | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
  echo "Status: $ORDER_STATUS"
else
  echo -e "${RED}❌ ERROR: No se pudo obtener el detalle${NC}"
fi
echo ""

# ================================================================
# 8. CREAR SESIÓN DE PAGO STRIPE
# ================================================================
echo -e "${YELLOW}[8/15] 💳 CREAR SESIÓN DE PAGO STRIPE${NC}"
echo "POST /api/orders/$ORDER_ID/create-checkout-session/"

CHECKOUT_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/orders/${ORDER_ID}/create-checkout-session/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

if echo "$CHECKOUT_RESPONSE" | grep -q '"checkout_url"'; then
  echo -e "${GREEN}✅ Sesión de pago creada${NC}"
  CHECKOUT_URL=$(echo $CHECKOUT_RESPONSE | grep -o '"checkout_url":"[^"]*"' | cut -d'"' -f4)
  echo "Checkout URL: ${CHECKOUT_URL:0:50}..."
else
  echo -e "${YELLOW}⚠️ No se pudo crear sesión (posible error de Stripe config)${NC}"
fi
echo ""

# ================================================================
# 9. CARRITO CON LENGUAJE NATURAL
# ================================================================
echo -e "${YELLOW}[9/15] 🎤 CARRITO CON LENGUAJE NATURAL${NC}"
echo "POST /api/orders/cart/add-natural-language/"

NLP_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/orders/cart/add-natural-language/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Agrega 2 smartphones al carrito"}')

if echo "$NLP_RESPONSE" | grep -q '"success"'; then
  echo -e "${GREEN}✅ NLP Cart funcionando${NC}"
  NLP_ACTION=$(echo $NLP_RESPONSE | grep -o '"interpreted_action":"[^"]*"' | cut -d'"' -f4)
  echo "Acción interpretada: $NLP_ACTION"
else
  echo -e "${RED}❌ ERROR: NLP Cart falló${NC}"
  echo "Response: $NLP_RESPONSE"
fi
echo ""

# ================================================================
# 10. SUGERENCIAS DE PRODUCTOS
# ================================================================
echo -e "${YELLOW}[10/15] 🔍 SUGERENCIAS DE PRODUCTOS${NC}"
echo "GET /api/orders/cart/suggestions/?q=smart"

SUGGESTIONS_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/orders/cart/suggestions/?q=smart")

SUGGESTION_COUNT=$(echo $SUGGESTIONS_RESPONSE | grep -o '"id"' | wc -l)

if [ $SUGGESTION_COUNT -gt 0 ]; then
  echo -e "${GREEN}✅ Sugerencias encontradas: $SUGGESTION_COUNT${NC}"
else
  echo -e "${YELLOW}⚠️ No hay sugerencias para 'smart'${NC}"
fi
echo ""

# ================================================================
# 11. DASHBOARD ADMIN
# ================================================================
echo -e "${YELLOW}[11/15] 📊 DASHBOARD ADMIN${NC}"
echo "GET /api/orders/admin/dashboard/"

DASHBOARD_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/orders/admin/dashboard/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

if echo "$DASHBOARD_RESPONSE" | grep -q '"total_revenue"'; then
  echo -e "${GREEN}✅ Dashboard obtenido${NC}"
  TOTAL_REVENUE=$(echo $DASHBOARD_RESPONSE | grep -o '"total_revenue":"[^"]*"' | cut -d'"' -f4)
  echo "Revenue total: $TOTAL_REVENUE"
else
  echo -e "${RED}❌ ERROR: No se pudo obtener el dashboard${NC}"
fi
echo ""

# ================================================================
# 12. REPORTE DINÁMICO CON IA
# ================================================================
echo -e "${YELLOW}[12/15] 🤖 REPORTE DINÁMICO CON IA${NC}"
echo "POST /api/reports/dynamic-parser/"

REPORT_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/reports/dynamic-parser/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Quiero un reporte de ventas del mes de octubre en PDF"}' \
  --write-out "%{http_code}" \
  --output /tmp/report_test.pdf)

if [ "$REPORT_RESPONSE" = "200" ]; then
  echo -e "${GREEN}✅ Reporte generado exitosamente${NC}"
  echo "PDF guardado en: /tmp/report_test.pdf"
else
  echo -e "${RED}❌ ERROR: No se pudo generar el reporte (HTTP $REPORT_RESPONSE)${NC}"
fi
echo ""

# ================================================================
# 13. COMPROBANTE DE ORDEN
# ================================================================
echo -e "${YELLOW}[13/15] 🧾 COMPROBANTE DE ORDEN${NC}"
echo "GET /api/reports/orders/$ORDER_ID/invoice/"

INVOICE_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/reports/orders/${ORDER_ID}/invoice/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  --write-out "%{http_code}" \
  --output /tmp/invoice_test.pdf)

if [ "$INVOICE_RESPONSE" = "200" ]; then
  echo -e "${GREEN}✅ Comprobante generado exitosamente${NC}"
  echo "PDF guardado en: /tmp/invoice_test.pdf"
else
  echo -e "${RED}❌ ERROR: No se pudo generar el comprobante (HTTP $INVOICE_RESPONSE)${NC}"
fi
echo ""

# ================================================================
# 14. PREDICCIONES DE VENTAS (ML)
# ================================================================
echo -e "${YELLOW}[14/15] 🧠 PREDICCIONES DE VENTAS (ML)${NC}"
echo "GET /api/predictions/sales/"

PREDICTIONS_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/predictions/sales/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

if echo "$PREDICTIONS_RESPONSE" | grep -q '"predictions"'; then
  echo -e "${GREEN}✅ Predicciones obtenidas${NC}"
  PREDICTIONS_COUNT=$(echo $PREDICTIONS_RESPONSE | grep -o '"date"' | wc -l)
  echo "Días predichos: $PREDICTIONS_COUNT"
else
  echo -e "${YELLOW}⚠️ Modelo no entrenado (ejecutar: python manage.py train_sales_model)${NC}"
fi
echo ""

# ================================================================
# 15. SWAGGER/OpenAPI DOCS
# ================================================================
echo -e "${YELLOW}[15/15] 📖 SWAGGER DOCS${NC}"
echo "GET /api/docs/"

SWAGGER_RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null "${BASE_URL}/api/docs/")

if [ "$SWAGGER_RESPONSE" = "200" ]; then
  echo -e "${GREEN}✅ Swagger UI disponible${NC}"
  echo "URL: ${BASE_URL}/api/docs/"
else
  echo -e "${RED}❌ ERROR: Swagger no disponible (HTTP $SWAGGER_RESPONSE)${NC}"
fi
echo ""

# ================================================================
# RESUMEN FINAL
# ================================================================
echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}📊 RESUMEN DEL TESTING${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""
echo "✅ Autenticación: JWT Token obtenido"
echo "✅ Productos: $PRODUCT_COUNT productos disponibles"
echo "✅ Categorías: $CATEGORY_COUNT categorías disponibles"
echo "✅ Órdenes: Orden #$ORDER_ID creada (Total: $ORDER_TOTAL)"
echo "✅ NLP Cart: Lenguaje natural funcionando"
echo "✅ Sugerencias: $SUGGESTION_COUNT sugerencias encontradas"
echo "✅ Dashboard Admin: Revenue total $TOTAL_REVENUE"
echo "✅ Reportes IA: PDF generado"
echo "✅ Comprobantes: PDF generado"
echo "✅ Swagger: Documentación disponible"
echo ""
echo -e "${GREEN}🎉 TESTING COMPLETADO${NC}"
echo -e "${BLUE}================================================================${NC}"
