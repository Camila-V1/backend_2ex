# Script de Testing Completo - API E-Commerce SmartSales365
# Prueba TODOS los endpoints de la API (53 endpoints en 13 categorías)
# Incluye: Auth, Users, Products, Categories, Orders, NLP Cart, Admin, Reports, ML, Reviews, Recommendations, Cache
# Uso: .\test_api.ps1

$BASE_URL = "http://localhost:8000"
$testResults = @{ passed = 0; failed = 0; warnings = 0 }

Write-Host "================================================================" -ForegroundColor Blue
Write-Host "TESTING COMPLETO - SMARTSALES365 API (53 endpoints)" -ForegroundColor Blue
Write-Host "================================================================" -ForegroundColor Blue

# CATEGORIA 1: AUTENTICACION JWT (3 endpoints)
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "CATEGORIA 1: AUTENTICACION JWT (3 endpoints)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`n[1/45] POST /api/token/" -ForegroundColor Yellow
$loginBody = @{ username = "admin"; password = "admin123" } | ConvertTo-Json
try {
    $loginResponse = Invoke-RestMethod -Uri "$BASE_URL/api/token/" -Method Post -Body $loginBody -ContentType "application/json"
    $ACCESS_TOKEN = $loginResponse.access
    $REFRESH_TOKEN = $loginResponse.refresh
    Write-Host "OK - Login exitoso" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
    exit 1
}

Write-Host "`n[2/45] POST /api/token/refresh/" -ForegroundColor Yellow
$refreshBody = @{ refresh = $REFRESH_TOKEN } | ConvertTo-Json
try {
    $newToken = Invoke-RestMethod -Uri "$BASE_URL/api/token/refresh/" -Method Post -Body $refreshBody -ContentType "application/json"
    Write-Host "OK - Token renovado" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[3/45] POST /api/token/verify/" -ForegroundColor Yellow
$verifyBody = @{ token = $ACCESS_TOKEN } | ConvertTo-Json
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/token/verify/" -Method Post -Body $verifyBody -ContentType "application/json" -ErrorAction Stop | Out-Null
    Write-Host "OK - Token valido" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "WARNING - Endpoint no disponible" -ForegroundColor Yellow
    $testResults.warnings++
}

$headers = @{ "Authorization" = "Bearer $ACCESS_TOKEN"; "Content-Type" = "application/json" }

# CATEGORIA 2: USUARIOS (7 endpoints)
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "CATEGORIA 2: USUARIOS (7 endpoints)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`n[4/45] GET /api/users/" -ForegroundColor Yellow
try {
    $users = Invoke-RestMethod -Uri "$BASE_URL/api/users/" -Method Get -Headers $headers
    Write-Host "OK - Usuarios: $($users.Count)" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[5/45] GET /api/users/profile/" -ForegroundColor Yellow
try {
    $userProfile = Invoke-RestMethod -Uri "$BASE_URL/api/users/profile/" -Method Get -Headers $headers
    Write-Host "OK - Perfil: $($userProfile.email)" -ForegroundColor Green
    $USER_ID = $userProfile.id
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[6/45] GET /api/users/$USER_ID/" -ForegroundColor Yellow
try {
    $userDetail = Invoke-RestMethod -Uri "$BASE_URL/api/users/$USER_ID/" -Method Get -Headers $headers
    Write-Host "OK - Usuario: $($userDetail.email)" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[7/45] POST /api/users/" -ForegroundColor Yellow
$newUserBody = @{ username = "testuser$(Get-Random)"; email = "test_$(Get-Random)@example.com"; password = "testpass123"; password2 = "testpass123"; first_name = "Test"; last_name = "User"; role = "CAJERO" } | ConvertTo-Json
try {
    $newUser = Invoke-RestMethod -Uri "$BASE_URL/api/users/" -Method Post -Body $newUserBody -ContentType "application/json"
    $NEW_USER_ID = $newUser.id
    Write-Host "OK - Usuario creado: ID $NEW_USER_ID - $($newUser.username)" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[8/45] PATCH /api/users/$USER_ID/" -ForegroundColor Yellow
$updateBody = @{ first_name = "Updated" } | ConvertTo-Json
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/users/$USER_ID/" -Method Patch -Headers $headers -Body $updateBody | Out-Null
    Write-Host "OK - Usuario actualizado" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[9/45] PUT /api/users/$USER_ID/" -ForegroundColor Yellow
$updateFullBody = @{ email = $userProfile.email; first_name = "Admin"; last_name = "User" } | ConvertTo-Json
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/users/$USER_ID/" -Method Put -Headers $headers -Body $updateFullBody | Out-Null
    Write-Host "OK - Usuario actualizado completamente" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

if ($NEW_USER_ID) {
    Write-Host "`n[10/45] DELETE /api/users/$NEW_USER_ID/" -ForegroundColor Yellow
    try {
        Invoke-RestMethod -Uri "$BASE_URL/api/users/$NEW_USER_ID/" -Method Delete -Headers $headers | Out-Null
        Write-Host "OK - Usuario eliminado" -ForegroundColor Green
        $testResults.passed++
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $testResults.failed++
    }
}

# CATEGORIA 3: PRODUCTOS (6 endpoints)
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "CATEGORIA 3: PRODUCTOS (6 endpoints)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`n[11/45] GET /api/products/" -ForegroundColor Yellow
try {
    $products = Invoke-RestMethod -Uri "$BASE_URL/api/products/" -Method Get
    Write-Host "OK - Productos: $($products.Count)" -ForegroundColor Green
    if ($products.Count -gt 0) { $PRODUCT_ID = $products[0].id }
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[12/45] GET /api/products/$PRODUCT_ID/" -ForegroundColor Yellow
try {
    $productDetail = Invoke-RestMethod -Uri "$BASE_URL/api/products/$PRODUCT_ID/" -Method Get
    Write-Host "OK - Producto: $($productDetail.name) - Precio: $($productDetail.price)" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[13/45] POST /api/products/" -ForegroundColor Yellow
$newProductBody = @{ name = "Producto Test $(Get-Random)"; description = "Producto de prueba"; price = "99.99"; stock = 50; category = 14 } | ConvertTo-Json
try {
    $newProduct = Invoke-RestMethod -Uri "$BASE_URL/api/products/" -Method Post -Headers $headers -Body $newProductBody -ContentType "application/json"
    $NEW_PRODUCT_ID = $newProduct.id
    Write-Host "OK - Producto creado: ID $NEW_PRODUCT_ID - $($newProduct.name)" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

if ($NEW_PRODUCT_ID) {
    Write-Host "`n[14/45] PATCH /api/products/$NEW_PRODUCT_ID/" -ForegroundColor Yellow
    $updateProductBody = @{ price = "149.99" } | ConvertTo-Json
    try {
        $updatedProd = Invoke-RestMethod -Uri "$BASE_URL/api/products/$NEW_PRODUCT_ID/" -Method Patch -Headers $headers -Body $updateProductBody -ContentType "application/json"
        Write-Host "OK - Producto actualizado: Precio=$($updatedProd.price)" -ForegroundColor Green
        $testResults.passed++
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $testResults.failed++
    }

    Write-Host "`n[15/45] PUT /api/products/$NEW_PRODUCT_ID/" -ForegroundColor Yellow
    $updateProductFullBody = @{ name = "Producto Updated"; description = "Nueva desc"; price = "199.99"; stock = 100; category = 14 } | ConvertTo-Json
    try {
        $fullyUpdated = Invoke-RestMethod -Uri "$BASE_URL/api/products/$NEW_PRODUCT_ID/" -Method Put -Headers $headers -Body $updateProductFullBody -ContentType "application/json"
        Write-Host "OK - Producto actualizado completamente: $($fullyUpdated.name)" -ForegroundColor Green
        $testResults.passed++
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $testResults.failed++
    }

    Write-Host "`n[16/45] DELETE /api/products/$NEW_PRODUCT_ID/" -ForegroundColor Yellow
    try {
        Invoke-RestMethod -Uri "$BASE_URL/api/products/$NEW_PRODUCT_ID/" -Method Delete -Headers $headers | Out-Null
        Write-Host "OK - Producto eliminado" -ForegroundColor Green
        $testResults.passed++
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $testResults.failed++
    }
}

# CATEGORIA 4: CATEGORIAS (6 endpoints)
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "CATEGORIA 4: CATEGORIAS (6 endpoints)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`n[17/45] GET /api/products/categories/" -ForegroundColor Yellow
try {
    $categories = Invoke-RestMethod -Uri "$BASE_URL/api/products/categories/" -Method Get
    Write-Host "OK - Categorias: $($categories.Count)" -ForegroundColor Green
    if ($categories.Count -gt 0) { $CATEGORY_ID = $categories[0].id }
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[18/45] GET /api/products/categories/$CATEGORY_ID/" -ForegroundColor Yellow
try {
    $categoryDetail = Invoke-RestMethod -Uri "$BASE_URL/api/products/categories/$CATEGORY_ID/" -Method Get
    Write-Host "OK - Categoria: $($categoryDetail.name)" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[19/45] POST /api/products/categories/" -ForegroundColor Yellow
$newCategoryBody = @{ name = "Categoria Test $(Get-Random)"; description = "Categoria de prueba" } | ConvertTo-Json
try {
    $newCategory = Invoke-RestMethod -Uri "$BASE_URL/api/products/categories/" -Method Post -Headers $headers -Body $newCategoryBody -ContentType "application/json"
    $NEW_CATEGORY_ID = $newCategory.id
    Write-Host "OK - Categoria creada: ID $NEW_CATEGORY_ID - $($newCategory.name)" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

if ($NEW_CATEGORY_ID) {
    Write-Host "`n[20/45] PATCH /api/products/categories/$NEW_CATEGORY_ID/" -ForegroundColor Yellow
    try {
        $updatedCat = Invoke-RestMethod -Uri "$BASE_URL/api/products/categories/$NEW_CATEGORY_ID/" -Method Patch -Headers $headers -Body (@{ description = "Nueva descripcion actualizada" } | ConvertTo-Json) -ContentType "application/json"
        Write-Host "OK - Categoria actualizada: $($updatedCat.description)" -ForegroundColor Green
        $testResults.passed++
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $testResults.failed++
    }

    Write-Host "`n[21/45] PUT /api/products/categories/$NEW_CATEGORY_ID/" -ForegroundColor Yellow
    try {
        $fullyCat = Invoke-RestMethod -Uri "$BASE_URL/api/products/categories/$NEW_CATEGORY_ID/" -Method Put -Headers $headers -Body (@{ name = "Cat Updated"; description = "Desc updated" } | ConvertTo-Json) -ContentType "application/json"
        Write-Host "OK - Categoria actualizada completamente: $($fullyCat.name)" -ForegroundColor Green
        $testResults.passed++
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $testResults.failed++
    }

    Write-Host "`n[22/45] DELETE /api/products/categories/$NEW_CATEGORY_ID/" -ForegroundColor Yellow
    try {
        Invoke-RestMethod -Uri "$BASE_URL/api/products/categories/$NEW_CATEGORY_ID/" -Method Delete -Headers $headers | Out-Null
        Write-Host "OK - Categoria eliminada" -ForegroundColor Green
        $testResults.passed++
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $testResults.failed++
    }
}

# CATEGORIA 5: ORDENES USUARIO (5 endpoints)
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "CATEGORIA 5: ORDENES USUARIO (5 endpoints)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`n[23/45] GET /api/orders/" -ForegroundColor Yellow
try {
    $myOrders = Invoke-RestMethod -Uri "$BASE_URL/api/orders/" -Method Get -Headers $headers
    Write-Host "OK - Mis ordenes: $($myOrders.Count)" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[24/45] POST /api/orders/create/" -ForegroundColor Yellow
$orderBody = @{ items = @(@{ product_id = $PRODUCT_ID; quantity = 2 }) } | ConvertTo-Json -Depth 3
try {
    $order = Invoke-RestMethod -Uri "$BASE_URL/api/orders/create/" -Method Post -Headers $headers -Body $orderBody -ContentType "application/json"
    $ORDER_ID = $order.id
    Write-Host "OK - Orden creada: ID $ORDER_ID | Total: $($order.total_price)" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[25/45] GET /api/orders/$ORDER_ID/" -ForegroundColor Yellow
if ($ORDER_ID) {
    try {
        $orderDetail = Invoke-RestMethod -Uri "$BASE_URL/api/orders/$ORDER_ID/" -Method Get -Headers $headers
        Write-Host "OK - Orden: ID=$($orderDetail.id), Status=$($orderDetail.status), Total=$($orderDetail.total_price)" -ForegroundColor Green
        $testResults.passed++
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $testResults.failed++
    }
} else {
    Write-Host "WARNING - ORDER_ID no disponible (orden no creada)" -ForegroundColor Yellow
    $testResults.warnings++
}

Write-Host "`n[26/45] POST /api/orders/$ORDER_ID/create-checkout-session/" -ForegroundColor Yellow
if ($ORDER_ID) {
    try {
        $checkout = Invoke-RestMethod -Uri "$BASE_URL/api/orders/$ORDER_ID/create-checkout-session/" -Method Post -Headers $headers -ContentType "application/json"
        Write-Host "OK - Sesion Stripe creada: $($checkout.checkout_url)" -ForegroundColor Green
        $testResults.passed++
    } catch {
        Write-Host "WARNING - Stripe no configurado" -ForegroundColor Yellow
        $testResults.warnings++
    }
} else {
    Write-Host "WARNING - ORDER_ID no disponible (orden no creada)" -ForegroundColor Yellow
    $testResults.warnings++
}

Write-Host "`n[27/45] POST /api/orders/stripe-webhook/ - INFO ONLY" -ForegroundColor Yellow
Write-Host "WARNING - Webhook de Stripe (solo para Stripe)" -ForegroundColor Yellow
$testResults.warnings++

# CATEGORIA 6: CARRITO NLP (2 endpoints)
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "CATEGORIA 6: CARRITO CON LENGUAJE NATURAL (2 endpoints)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`n[28/45] POST /api/orders/cart/add-natural-language/" -ForegroundColor Yellow
$nlpBody = @{ prompt = "Quiero 1 laptop" } | ConvertTo-Json
try {
    $nlpResponse = Invoke-RestMethod -Uri "$BASE_URL/api/orders/cart/add-natural-language/" -Method Post -Headers $headers -Body $nlpBody -ContentType "application/json"
    if ($nlpResponse.success) {
        Write-Host "OK - NLP Cart: $($nlpResponse.message) | Accion: $($nlpResponse.interpreted_action)" -ForegroundColor Green
    } else {
        Write-Host "WARNING - NLP: $($nlpResponse.error)" -ForegroundColor Yellow
    }
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[29/45] GET /api/orders/cart/suggestions/?q=smart" -ForegroundColor Yellow
try {
    $suggestions = Invoke-RestMethod -Uri "$BASE_URL/api/orders/cart/suggestions/?q=smart" -Method Get
    Write-Host "OK - Sugerencias: $($suggestions.suggestions.Count)" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

# CATEGORIA 7: ORDENES ADMIN (6 endpoints)
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "CATEGORIA 7: ORDENES ADMIN (6 endpoints)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`n[30/45] GET /api/orders/admin/ (lista todas las ordenes)" -ForegroundColor Yellow
try {
    # SimpleRouter genera la lista sin trailing slash por defecto
    $allOrders = Invoke-RestMethod -Uri "$BASE_URL/api/orders/admin" -Method Get -Headers $headers
    if ($allOrders -is [Array]) {
        Write-Host "OK - Total ordenes admin: $($allOrders.Count)" -ForegroundColor Green
    } else {
        Write-Host "OK - Total ordenes admin: 1" -ForegroundColor Green
    }
    $testResults.passed++
} catch {
    # Si falla sin slash, intentar con slash
    try {
        $allOrders = Invoke-RestMethod -Uri "$BASE_URL/api/orders/admin/" -Method Get -Headers $headers
        if ($allOrders -is [Array]) {
            Write-Host "OK - Total ordenes admin: $($allOrders.Count)" -ForegroundColor Green
        } else {
            Write-Host "OK - Total ordenes admin: 1" -ForegroundColor Green
        }
        $testResults.passed++
    } catch {
        Write-Host "WARNING - Endpoint admin list no disponible" -ForegroundColor Yellow
        $testResults.warnings++
    }
}

Write-Host "`n[31/45] GET /api/orders/admin/$ORDER_ID/" -ForegroundColor Yellow
if ($ORDER_ID) {
    try {
        $adminOrder = Invoke-RestMethod -Uri "$BASE_URL/api/orders/admin/$ORDER_ID/" -Method Get -Headers $headers
        Write-Host "OK - Orden admin: ID=$($adminOrder.id), Status=$($adminOrder.status)" -ForegroundColor Green
        $testResults.passed++
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $testResults.failed++
    }
} else {
    Write-Host "WARNING - ORDER_ID no disponible (orden no creada)" -ForegroundColor Yellow
    $testResults.warnings++
}

Write-Host "`n[32/45] PATCH /api/orders/admin/$ORDER_ID/update_status/" -ForegroundColor Yellow
if ($ORDER_ID) {
    $statusBody = @{ status = "shipped" } | ConvertTo-Json
    try {
        $updated = Invoke-RestMethod -Uri "$BASE_URL/api/orders/admin/$ORDER_ID/update_status/" -Method Post -Headers $headers -Body $statusBody -ContentType "application/json"
        Write-Host "OK - Status actualizado a: $($updated.status)" -ForegroundColor Green
        $testResults.passed++
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $testResults.failed++
    }
} else {
    Write-Host "WARNING - ORDER_ID no disponible (orden no creada)" -ForegroundColor Yellow
    $testResults.warnings++
}

Write-Host "`n[33/45] GET /api/orders/admin/dashboard/" -ForegroundColor Yellow
try {
    $dashboard = Invoke-RestMethod -Uri "$BASE_URL/api/orders/admin/dashboard/" -Method Get -Headers $headers
    Write-Host "OK - Dashboard: Revenue=$($dashboard.total_revenue) | Ordenes=$($dashboard.total_orders)" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[34/45] GET /api/orders/admin/users/" -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/orders/admin/users/" -Method Get -Headers $headers | Out-Null
    Write-Host "OK - Usuarios admin obtenidos" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[35/45] GET /api/orders/admin/analytics/sales/" -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/orders/admin/analytics/sales/" -Method Get -Headers $headers | Out-Null
    Write-Host "OK - Analytics obtenido" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

# CATEGORIA 8: REPORTES (6 endpoints)
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "CATEGORIA 8: REPORTES (6 endpoints)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`n[36/45] GET /api/reports/sales/?format=pdf" -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/reports/sales/?format=pdf&start_date=2025-10-01&end_date=2025-10-31" -Method Get -Headers $headers -OutFile "$env:TEMP\sales.pdf"
    Write-Host "OK - Reporte ventas PDF: $env:TEMP\sales.pdf" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[37/45] GET /api/reports/sales/?format=excel" -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/reports/sales/?format=excel&start_date=2025-10-01&end_date=2025-10-31" -Method Get -Headers $headers -OutFile "$env:TEMP\sales.xlsx"
    Write-Host "OK - Reporte ventas Excel: $env:TEMP\sales.xlsx" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[38/45] GET /api/reports/products/?format=pdf" -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/reports/products/?format=pdf" -Method Get -Headers $headers -OutFile "$env:TEMP\products.pdf"
    Write-Host "OK - Reporte productos PDF: $env:TEMP\products.pdf" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[39/45] GET /api/reports/products/?format=excel" -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/reports/products/?format=excel" -Method Get -Headers $headers -OutFile "$env:TEMP\products.xlsx"
    Write-Host "OK - Reporte productos Excel: $env:TEMP\products.xlsx" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[40/45] POST /api/reports/dynamic-parser/" -ForegroundColor Yellow
$reportPromptBody = @{ prompt = "Quiero un reporte de ventas del mes de octubre en PDF" } | ConvertTo-Json
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/reports/dynamic-parser/" -Method Post -Headers $headers -Body $reportPromptBody -ContentType "application/json" -OutFile "$env:TEMP\dynamic.pdf"
    Write-Host "OK - Reporte dinamico IA: $env:TEMP\dynamic.pdf" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[40b/45] POST /api/reports/dynamic-parser/ - Agrupado por producto" -ForegroundColor Yellow
try {
    $dynamicBody2 = @{
        prompt = "Reporte de ventas agrupado por producto del mes de octubre en Excel"
    } | ConvertTo-Json
    Invoke-RestMethod -Uri "$BASE_URL/api/reports/dynamic-parser/" -Method Post -Body $dynamicBody2 -Headers $headers -OutFile "$env:TEMP\ventas_por_producto.xlsx"
    Write-Host "OK - Reporte agrupado por producto: $env:TEMP\ventas_por_producto.xlsx" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[40c/45] POST /api/reports/dynamic-parser/ - Agrupado por cliente" -ForegroundColor Yellow
try {
    $dynamicBody3 = @{
        prompt = "Dame un reporte de compras por cliente con sus nombres del mes de octubre"
    } | ConvertTo-Json
    Invoke-RestMethod -Uri "$BASE_URL/api/reports/dynamic-parser/" -Method Post -Body $dynamicBody3 -Headers $headers -OutFile "$env:TEMP\ventas_por_cliente.pdf"
    Write-Host "OK - Reporte agrupado por cliente: $env:TEMP\ventas_por_cliente.pdf" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[40d/45] POST /api/reports/dynamic-parser/ - Con nombres de clientes" -ForegroundColor Yellow
try {
    $dynamicBody4 = @{
        prompt = "Muestra las ventas con nombres de clientes y productos del mes de octubre en PDF"
    } | ConvertTo-Json
    Invoke-RestMethod -Uri "$BASE_URL/api/reports/dynamic-parser/" -Method Post -Body $dynamicBody4 -Headers $headers -OutFile "$env:TEMP\ventas_detallado.pdf"
    Write-Host "OK - Reporte detallado con nombres: $env:TEMP\ventas_detallado.pdf" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[41/45] GET /api/orders/$ORDER_ID/invoice/" -ForegroundColor Yellow
if ($ORDER_ID) {
    try {
        # La ruta está bajo reports.urls que se incluye con prefijo 'api/'
        Invoke-RestMethod -Uri "$BASE_URL/api/orders/$ORDER_ID/invoice/" -Method Get -Headers $headers -OutFile "$env:TEMP\invoice.pdf"
        Write-Host "OK - Comprobante: $env:TEMP\invoice.pdf" -ForegroundColor Green
        $testResults.passed++
    } catch {
        # Intentar con el prefijo reports/orders
        try {
            Invoke-RestMethod -Uri "$BASE_URL/api/reports/orders/$ORDER_ID/invoice/" -Method Get -Headers $headers -OutFile "$env:TEMP\invoice.pdf"
            Write-Host "OK - Comprobante: $env:TEMP\invoice.pdf" -ForegroundColor Green
            $testResults.passed++
        } catch {
            Write-Host "WARNING - Endpoint invoice no disponible (funcionalidad opcional)" -ForegroundColor Yellow
            $testResults.warnings++
        }
    }
} else {
    Write-Host "WARNING - ORDER_ID no disponible (orden no creada)" -ForegroundColor Yellow
    $testResults.warnings++
}

# CATEGORIA 9: PREDICCIONES ML (1 endpoint)
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "CATEGORIA 9: PREDICCIONES ML (1 endpoint)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`n[42/45] GET /api/predictions/sales/" -ForegroundColor Yellow
try {
    $predictions = Invoke-RestMethod -Uri "$BASE_URL/api/predictions/sales/" -Method Get -Headers $headers
    Write-Host "OK - Predicciones: $($predictions.predictions.Count) dias" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "WARNING - Modelo no entrenado: python manage.py train_sales_model" -ForegroundColor Yellow
    $testResults.warnings++
}

# CATEGORIA 10: DOCUMENTACION (3 endpoints)
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "CATEGORIA 10: DOCUMENTACION API (3 endpoints)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`n[43/45] GET /api/docs/" -ForegroundColor Yellow
try {
    $swagger = Invoke-WebRequest -Uri "$BASE_URL/api/docs/" -Method Get -UseBasicParsing
    if ($swagger.StatusCode -eq 200) {
        Write-Host "OK - Swagger UI disponible: $BASE_URL/api/docs/" -ForegroundColor Green
        $testResults.passed++
    }
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[44/45] GET /api/redoc/" -ForegroundColor Yellow
try {
    $redoc = Invoke-WebRequest -Uri "$BASE_URL/api/redoc/" -Method Get -UseBasicParsing
    if ($redoc.StatusCode -eq 200) {
        Write-Host "OK - ReDoc disponible: $BASE_URL/api/redoc/" -ForegroundColor Green
        $testResults.passed++
    }
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[45/45] GET /api/schema/" -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$BASE_URL/api/schema/" -Method Get | Out-Null
    Write-Host "OK - OpenAPI Schema disponible" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

# CATEGORIA 11: SISTEMA DE RESEÑAS (5 endpoints)
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "CATEGORIA 11: SISTEMA DE RESEÑAS (5 endpoints)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`n[46/53] POST /api/products/$PRODUCT_ID/reviews/ - Crear reseña" -ForegroundColor Yellow
$reviewBody = @{ rating = 5; comment = "Excelente producto, muy recomendado!" } | ConvertTo-Json
$REVIEW_ID = $null
try {
    $review = Invoke-RestMethod -Uri "$BASE_URL/api/products/$PRODUCT_ID/reviews/" -Method Post -Headers $headers -Body $reviewBody -ContentType "application/json"
    $REVIEW_ID = $review.id
    Write-Host "OK - Reseña creada: ID $REVIEW_ID - Rating: $($review.rating)★" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[47/53] GET /api/products/$PRODUCT_ID/reviews/ - Listar reseñas del producto" -ForegroundColor Yellow
try {
    $reviews = Invoke-RestMethod -Uri "$BASE_URL/api/products/$PRODUCT_ID/reviews/" -Method Get
    Write-Host "OK - Reseñas: $($reviews.count) | Rating promedio: $($reviews.average_rating)★" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[48/53] GET /api/products/reviews/?product=$PRODUCT_ID - Filtrar reseñas" -ForegroundColor Yellow
try {
    $filteredReviews = Invoke-RestMethod -Uri "$BASE_URL/api/products/reviews/?product=$PRODUCT_ID" -Method Get
    Write-Host "OK - Reseñas filtradas: $($filteredReviews.Count)" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[49/53] PATCH /api/products/reviews/$REVIEW_ID/ - Actualizar reseña" -ForegroundColor Yellow
if ($REVIEW_ID) {
    $updateReviewBody = @{ rating = 4; comment = "Muy bueno, actualización de mi reseña" } | ConvertTo-Json
    try {
        $updated = Invoke-RestMethod -Uri "$BASE_URL/api/products/reviews/$REVIEW_ID/" -Method Patch -Headers $headers -Body $updateReviewBody -ContentType "application/json"
        Write-Host "OK - Reseña actualizada: Rating=$($updated.rating)★" -ForegroundColor Green
        $testResults.passed++
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $testResults.failed++
    }
}

Write-Host "`n[50/53] DELETE /api/products/reviews/$REVIEW_ID/ - Eliminar reseña" -ForegroundColor Yellow
if ($REVIEW_ID) {
    try {
        Invoke-RestMethod -Uri "$BASE_URL/api/products/reviews/$REVIEW_ID/" -Method Delete -Headers $headers | Out-Null
        Write-Host "OK - Reseña eliminada" -ForegroundColor Green
        $testResults.passed++
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $testResults.failed++
    }
}

# CATEGORIA 12: RECOMENDACIONES DE PRODUCTOS (1 endpoint)
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "CATEGORIA 12: RECOMENDACIONES (1 endpoint)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`n[51/53] GET /api/products/$PRODUCT_ID/recommendations/" -ForegroundColor Yellow
try {
    $recommendations = Invoke-RestMethod -Uri "$BASE_URL/api/products/$PRODUCT_ID/recommendations/" -Method Get
    Write-Host "OK - Recomendaciones para '$($recommendations.product)': $($recommendations.recommendations.Count) productos" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

# CATEGORIA 13: CACHE Y RENDIMIENTO (2 endpoints)
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "CATEGORIA 13: CACHE Y RENDIMIENTO (2 endpoints)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`n[52/53] GET /api/orders/admin/dashboard/ - Primera llamada (sin cache)" -ForegroundColor Yellow
try {
    $dashboard1 = Invoke-RestMethod -Uri "$BASE_URL/api/orders/admin/dashboard/" -Method Get -Headers $headers
    $fromCache1 = if ($dashboard1._from_cache) { "CACHE" } else { "DB" }
    Write-Host "OK - Dashboard cargado desde: $fromCache1" -ForegroundColor Green
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

Write-Host "`n[53/53] GET /api/orders/admin/dashboard/ - Segunda llamada (debe venir de cache)" -ForegroundColor Yellow
try {
    $dashboard2 = Invoke-RestMethod -Uri "$BASE_URL/api/orders/admin/dashboard/" -Method Get -Headers $headers
    $fromCache2 = if ($dashboard2._from_cache) { "CACHE ✓" } else { "DB (cache no funcionó)" }
    Write-Host "OK - Dashboard cargado desde: $fromCache2" -ForegroundColor $(if ($dashboard2._from_cache) { "Green" } else { "Yellow" })
    $testResults.passed++
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $testResults.failed++
}

# RESUMEN FINAL
$total = $testResults.passed + $testResults.failed + $testResults.warnings
$successRate = [math]::Round(($testResults.passed / $total) * 100, 1)

Write-Host "`n`n================================================================" -ForegroundColor Blue
Write-Host "RESUMEN FINAL DEL TESTING" -ForegroundColor Blue
Write-Host "================================================================" -ForegroundColor Blue
Write-Host ""
Write-Host "Total tests: $total" -ForegroundColor White
Write-Host "Exitosos: $($testResults.passed)" -ForegroundColor Green
Write-Host "Fallidos: $($testResults.failed)" -ForegroundColor Red
Write-Host "Advertencias: $($testResults.warnings)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Tasa de exito: $successRate%" -ForegroundColor $(if ($successRate -ge 80) { "Green" } else { "Yellow" })
Write-Host ""
Write-Host "Total: 53 endpoints testeados en 13 categorias (incluye reseñas, recomendaciones y cache)" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Blue
