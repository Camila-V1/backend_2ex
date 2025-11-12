                                                # 🚨 SOLUCIÓN: Error "NOT_FOUND" en Payment Success

                                                ## 📌 Problema Actual

                                                Cuando el usuario paga en Stripe, es redirigido a:
                                                ```
                                                https://web-2ex-b1agwzii7-vazquescamila121-7209s-projects.vercel.app/payment-success
                                                ```

                                                Y Vercel responde con:
                                                ```
                                                NOT_FOUND
                                                Code: NOT_FOUND
                                                ID: gru1::4mzft-1762912348605-f98ca04bd8dd
                                                ```

                                                **Resultado:** La orden queda en estado `PENDING` porque el webhook nunca se ejecuta.

                                                ---

                                                ## 🔍 Causas del Problema

                                                ### 1️⃣ **Frontend no tiene la ruta `/payment-success`**
                                                - Vercel no encuentra esta ruta en el código del frontend
                                                - Necesitas crear esta página en tu proyecto de frontend

                                                ### 2️⃣ **Variable `FRONTEND_URL` mal configurada en Render**
                                                - Debe apuntar a la URL de producción de Vercel
                                                - Actualmente podría estar apuntando a otra URL

                                                ### 3️⃣ **Webhook de Stripe no configurado**
                                                - Stripe necesita saber a qué URL enviar eventos
                                                - Si no está configurado, la orden nunca cambia de `PENDING` a `PAID`

                                                ---

                                                ## ✅ SOLUCIÓN PASO A PASO

                                                ### **PASO 1: Configurar `FRONTEND_URL` en Render**

                                                1. Ve a tu proyecto en Render Dashboard:
                                                ```
                                                https://dashboard.render.com/web/srv-YOUR_SERVICE_ID
                                                ```

                                                2. Ve a **Environment** → **Add Environment Variable**

                                                3. Agrega:
                                                ```
                                                Key: FRONTEND_URL
                                                Value: https://web-2ex.vercel.app
                                                ```
                                                ⚠️ **Importante:** No incluyas `/` al final

                                                4. Haz clic en **Save Changes**

                                                5. Espera que Render redespliegue (5-7 minutos)

                                                ---

                                                ### **PASO 2: Crear página `/payment-success` en el Frontend**

                                                **Opción A: Si usas React Router (src/App.jsx o routes):**

                                                ```jsx
                                                // src/pages/PaymentSuccess.jsx
                                                import { useEffect, useState } from 'react';
                                                import { useSearchParams, useNavigate } from 'react-router-dom';
                                                import axios from 'axios';

                                                export default function PaymentSuccess() {
                                                const [searchParams] = useSearchParams();
                                                const navigate = useNavigate();
                                                const [loading, setLoading] = useState(true);
                                                const sessionId = searchParams.get('session_id');

                                                useEffect(() => {
                                                    if (sessionId) {
                                                    // Opcional: Verificar el pago con tu backend
                                                    axios.get(`/api/orders/verify-payment/${sessionId}`)
                                                        .then(() => {
                                                        setLoading(false);
                                                        })
                                                        .catch(error => {
                                                        console.error('Error verificando pago:', error);
                                                        setLoading(false);
                                                        });
                                                    }
                                                }, [sessionId]);

                                                if (loading) {
                                                    return (
                                                    <div className="min-h-screen flex items-center justify-center">
                                                        <div className="text-center">
                                                        <h2 className="text-2xl font-bold mb-4">Verificando pago...</h2>
                                                        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-green-500 mx-auto"></div>
                                                        </div>
                                                    </div>
                                                    );
                                                }

                                                return (
                                                    <div className="min-h-screen flex items-center justify-center bg-gray-50">
                                                    <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-8 text-center">
                                                        <div className="mb-6">
                                                        <svg className="mx-auto h-16 w-16 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                        </svg>
                                                        </div>
                                                        
                                                        <h1 className="text-3xl font-bold text-gray-900 mb-4">
                                                        ¡Pago Exitoso!
                                                        </h1>
                                                        
                                                        <p className="text-gray-600 mb-6">
                                                        Tu pago ha sido procesado correctamente. 
                                                        Recibirás un correo de confirmación en breve.
                                                        </p>

                                                        <div className="space-y-3">
                                                        <button
                                                            onClick={() => navigate('/orders')}
                                                            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition"
                                                        >
                                                            Ver mis órdenes
                                                        </button>
                                                        
                                                        <button
                                                            onClick={() => navigate('/')}
                                                            className="w-full bg-gray-200 text-gray-700 py-3 px-6 rounded-lg hover:bg-gray-300 transition"
                                                        >
                                                            Volver al inicio
                                                        </button>
                                                        </div>
                                                    </div>
                                                    </div>
                                                );
                                                }
                                                ```

                                                **Agregar la ruta en tu archivo de rutas:**

                                                ```jsx
                                                // src/App.jsx o src/routes/index.jsx
                                                import PaymentSuccess from './pages/PaymentSuccess';
                                                import PaymentCancelled from './pages/PaymentCancelled';

                                                // En tus routes:
                                                <Route path="/payment-success" element={<PaymentSuccess />} />
                                                <Route path="/payment-cancelled" element={<PaymentCancelled />} />
                                                ```

                                                **Opción B: Crear también la página de cancelación:**

                                                ```jsx
                                                // src/pages/PaymentCancelled.jsx
                                                import { useNavigate } from 'react-router-dom';

                                                export default function PaymentCancelled() {
                                                const navigate = useNavigate();

                                                return (
                                                    <div className="min-h-screen flex items-center justify-center bg-gray-50">
                                                    <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-8 text-center">
                                                        <div className="mb-6">
                                                        <svg className="mx-auto h-16 w-16 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                        </svg>
                                                        </div>
                                                        
                                                        <h1 className="text-3xl font-bold text-gray-900 mb-4">
                                                        Pago Cancelado
                                                        </h1>
                                                        
                                                        <p className="text-gray-600 mb-6">
                                                        Has cancelado el proceso de pago. 
                                                        Tu orden permanece pendiente.
                                                        </p>

                                                        <div className="space-y-3">
                                                        <button
                                                            onClick={() => navigate('/cart')}
                                                            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition"
                                                        >
                                                            Volver al carrito
                                                        </button>
                                                        
                                                        <button
                                                            onClick={() => navigate('/')}
                                                            className="w-full bg-gray-200 text-gray-700 py-3 px-6 rounded-lg hover:bg-gray-300 transition"
                                                        >
                                                            Continuar comprando
                                                        </button>
                                                        </div>
                                                    </div>
                                                    </div>
                                                );
                                                }
                                                ```

                                                ---

                                                ### **PASO 3: Configurar Webhook en Stripe**

                                                1. **Ir a Stripe Dashboard:**
                                                ```
                                                https://dashboard.stripe.com/test/webhooks
                                                ```

                                                2. **Crear nuevo webhook:**
                                                - Haz clic en **+ Add endpoint**

                                                3. **Configurar el endpoint:**
                                                ```
                                                Endpoint URL: https://backend-2ex-ecommerce.onrender.com/api/orders/stripe-webhook/
                                                
                                                Events to send:
                                                ✅ checkout.session.completed
                                                ```

                                                4. **Copiar el Signing Secret:**
                                                - Después de crear el webhook, verás un **Signing secret** (empieza con `whsec_...`)
                                                - Cópialo

                                                5. **Agregar el secret en Render:**
                                                - Ve a Render Dashboard → Environment Variables
                                                - Agrega:
                                                    ```
                                                    Key: STRIPE_WEBHOOK_SECRET
                                                    Value: whsec_tu_signing_secret_aquí
                                                    ```
                                                - Haz clic en **Save Changes**

                                                ---

                                                ## 🧪 TESTING

                                                ### **1. Probar el flujo completo:**

                                                1. En tu frontend, agrega un producto al carrito
                                                2. Ve al checkout y haz clic en "Pagar"
                                                3. Usa la tarjeta de prueba de Stripe:
                                                ```
                                                Número: 4242 4242 4242 4242
                                                Fecha: 12/34 (cualquier fecha futura)
                                                CVC: 123
                                                ZIP: 12345
                                                ```
                                                4. Completa el pago
                                                5. Deberías ser redirigido a `/payment-success`
                                                6. La orden debe cambiar de `PENDING` a `PAID`

                                                ### **2. Verificar que el webhook funciona:**

                                                En Render logs, deberías ver:
                                                ```
                                                INFO debug_middleware 🌐 REQUEST: POST /api/orders/stripe-webhook/
                                                INFO debug_middleware 🌐 RESPONSE: 200 for /api/orders/stripe-webhook/
                                                ```

                                                En Stripe Dashboard → Webhooks, deberías ver:
                                                ```
                                                ✅ checkout.session.completed - 200 OK
                                                ```

                                                ---

                                                ## 📊 VERIFICACIÓN FINAL

                                                ### **Checklist de configuración:**

                                                - [ ] `FRONTEND_URL` configurado en Render apuntando a `https://web-2ex.vercel.app`
                                                - [ ] Página `/payment-success` creada en el frontend
                                                - [ ] Página `/payment-cancelled` creada en el frontend
                                                - [ ] Rutas agregadas en React Router
                                                - [ ] Webhook configurado en Stripe Dashboard
                                                - [ ] `STRIPE_WEBHOOK_SECRET` agregado en Render
                                                - [ ] Frontend redesplegado en Vercel
                                                - [ ] Backend redesplegado en Render
                                                - [ ] Prueba de pago completada exitosamente
                                                - [ ] Orden cambia de `PENDING` a `PAID`

                                                ---

                                                ## ⚠️ PROBLEMA ADICIONAL: URLs de Preview de Vercel

                                                Si ves URLs como:
                                                ```
                                                https://web-2ex-b1agwzii7-vazquescamila121-7209s-projects.vercel.app/
                                                ```

                                                Estas son **preview URLs** que Vercel genera para cada commit. Para evitar problemas:

                                                **Opción A: Usar solo la URL de producción**
                                                1. Ve a Vercel Dashboard
                                                2. En tu proyecto, ve a **Settings → Domains**
                                                3. Usa solo la URL principal: `https://web-2ex.vercel.app`
                                                4. Configura esa URL en la variable `FRONTEND_URL` de Render

                                                **Opción B: Permitir múltiples dominios (Avanzado)**
                                                Modificar el backend para aceptar cualquier subdominio de Vercel:

                                                ```python
                                                # ecommerce_api/settings.py
                                                import re

                                                # En lugar de usar FRONTEND_URL fijo, extraer del header Referer
                                                # Este cambio se haría en shop_orders/views.py
                                                ```

                                                ---

                                                ## 🆘 Si el problema persiste

                                                **Revisa los logs:**

                                                1. **Logs de Render:**
                                                ```
                                                https://dashboard.render.com/web/srv-YOUR_SERVICE_ID/logs
                                                ```
                                                Busca: `stripe-webhook` y verifica si hay errores

                                                2. **Logs de Stripe:**
                                                ```
                                                https://dashboard.stripe.com/test/webhooks
                                                ```
                                                Verifica el estado de los webhooks enviados

                                                3. **Consola del navegador:**
                                                Abre DevTools → Network → verifica la petición a `create-checkout-session`

                                                ---

                                                ## 📞 Contacto

                                                Si necesitas más ayuda, provee:
                                                1. Screenshot del error en Vercel
                                                2. Logs de Render (últimas 50 líneas)
                                                3. Screenshot de la configuración del webhook en Stripe
                                                4. URL actual de tu frontend en Vercel
