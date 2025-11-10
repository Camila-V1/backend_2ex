"""
POBLADOR COMPLETO DE BASE DE DATOS
===================================
Puebla TODOS los modelos del sistema con datos realistas y completos.

Ejecutar con:
    python seed_complete_database.py
"""

import os
import django
import random
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.contrib.auth import get_user_model
from products.models import Category, Product
from shop_orders.models import Order, OrderItem
from deliveries.models import Return
from users.models import Wallet, WalletTransaction

User = get_user_model()

# ============================================================================
# DATOS DE PRUEBA REALISTAS
# ============================================================================

CATEGORIES_DATA = [
    {'name': 'Electrónica', 'description': 'Dispositivos electrónicos y gadgets'},
    {'name': 'Computación', 'description': 'Laptops, PCs y accesorios'},
    {'name': 'Smartphones', 'description': 'Teléfonos móviles y accesorios'},
    {'name': 'Audio', 'description': 'Auriculares, altavoces y equipos de audio'},
    {'name': 'Gaming', 'description': 'Consolas, juegos y accesorios gamer'},
    {'name': 'Tablets', 'description': 'Tablets y accesorios'},
    {'name': 'Wearables', 'description': 'Smartwatches y pulseras inteligentes'},
    {'name': 'Fotografía', 'description': 'Cámaras y accesorios fotográficos'},
    {'name': 'Hogar Inteligente', 'description': 'Dispositivos domóticos y smart home'},
    {'name': 'Accesorios', 'description': 'Cables, cargadores y accesorios varios'},
]

PRODUCTS_DATA = [
    # Electrónica
    {'name': 'Tablet iPad Air 10.9"', 'price': Decimal('5999.99'), 'stock': 25, 'description': 'Tablet Apple iPad Air con pantalla Liquid Retina de 10.9 pulgadas, chip M1, 64GB', 'category': 'Tablets'},
    {'name': 'iPad Pro 12.9"', 'price': Decimal('12999.99'), 'stock': 15, 'description': 'iPad Pro con pantalla XDR de 12.9 pulgadas, chip M2, 256GB', 'category': 'Tablets'},
    {'name': 'Samsung Galaxy Tab S9', 'price': Decimal('8499.99'), 'stock': 20, 'description': 'Tablet Samsung Galaxy Tab S9 11 pulgadas, 128GB, S Pen incluido', 'category': 'Tablets'},
    
    # Computación
    {'name': 'MacBook Pro 16"', 'price': Decimal('34999.99'), 'stock': 10, 'description': 'MacBook Pro 16 pulgadas, chip M3 Pro, 18GB RAM, 512GB SSD', 'category': 'Computación'},
    {'name': 'Dell XPS 15', 'price': Decimal('24999.99'), 'stock': 12, 'description': 'Laptop Dell XPS 15, Intel i7-13700H, 16GB RAM, 512GB SSD, RTX 4050', 'category': 'Computación'},
    {'name': 'Lenovo ThinkPad X1', 'price': Decimal('18999.99'), 'stock': 18, 'description': 'ThinkPad X1 Carbon Gen 11, Intel i7, 16GB RAM, 512GB SSD', 'category': 'Computación'},
    {'name': 'ASUS ROG Zephyrus G14', 'price': Decimal('22999.99'), 'stock': 8, 'description': 'Laptop gamer ASUS ROG, Ryzen 9, RTX 4060, 32GB RAM, 1TB SSD', 'category': 'Gaming'},
    
    # Smartphones
    {'name': 'iPhone 15 Pro Max', 'price': Decimal('17999.99'), 'stock': 30, 'description': 'iPhone 15 Pro Max 256GB, Titanio Natural, A17 Pro', 'category': 'Smartphones'},
    {'name': 'Samsung Galaxy S24 Ultra', 'price': Decimal('16999.99'), 'stock': 25, 'description': 'Galaxy S24 Ultra 256GB, S Pen incluido, Snapdragon 8 Gen 3', 'category': 'Smartphones'},
    {'name': 'Google Pixel 8 Pro', 'price': Decimal('13999.99'), 'stock': 20, 'description': 'Pixel 8 Pro 256GB, Google Tensor G3, cámara de 50MP', 'category': 'Smartphones'},
    {'name': 'Xiaomi 14 Pro', 'price': Decimal('9999.99'), 'stock': 35, 'description': 'Xiaomi 14 Pro 256GB, Snapdragon 8 Gen 3, Leica camera', 'category': 'Smartphones'},
    
    # Audio
    {'name': 'AirPods Pro 2', 'price': Decimal('3299.99'), 'stock': 50, 'description': 'AirPods Pro segunda generación con cancelación activa de ruido', 'category': 'Audio'},
    {'name': 'Sony WH-1000XM5', 'price': Decimal('4999.99'), 'stock': 40, 'description': 'Audífonos over-ear con cancelación de ruido líder en la industria', 'category': 'Audio'},
    {'name': 'Bose QuietComfort Ultra', 'price': Decimal('5499.99'), 'stock': 30, 'description': 'Audífonos premium Bose con audio espacial', 'category': 'Audio'},
    {'name': 'JBL Flip 6', 'price': Decimal('1899.99'), 'stock': 60, 'description': 'Altavoz Bluetooth portátil resistente al agua', 'category': 'Audio'},
    {'name': 'Sonos Arc', 'price': Decimal('12999.99'), 'stock': 15, 'description': 'Barra de sonido premium con Dolby Atmos', 'category': 'Audio'},
    
    # Gaming
    {'name': 'PlayStation 5 Slim', 'price': Decimal('8999.99'), 'stock': 25, 'description': 'Consola PS5 Slim con 1TB SSD', 'category': 'Gaming'},
    {'name': 'Xbox Series X', 'price': Decimal('8499.99'), 'stock': 20, 'description': 'Consola Xbox Series X 1TB con 4K a 120fps', 'category': 'Gaming'},
    {'name': 'Nintendo Switch OLED', 'price': Decimal('5499.99'), 'stock': 35, 'description': 'Switch OLED con pantalla de 7 pulgadas', 'category': 'Gaming'},
    {'name': 'Steam Deck', 'price': Decimal('6999.99'), 'stock': 15, 'description': 'Consola portátil Steam Deck 512GB', 'category': 'Gaming'},
    {'name': 'Logitech G Pro X Superlight', 'price': Decimal('2199.99'), 'stock': 45, 'description': 'Mouse gaming inalámbrico ultra ligero', 'category': 'Gaming'},
    
    # Wearables
    {'name': 'Apple Watch Series 9', 'price': Decimal('6499.99'), 'stock': 40, 'description': 'Apple Watch Series 9 45mm GPS + Cellular', 'category': 'Wearables'},
    {'name': 'Samsung Galaxy Watch 6', 'price': Decimal('4999.99'), 'stock': 35, 'description': 'Galaxy Watch 6 44mm con sensor de salud avanzado', 'category': 'Wearables'},
    {'name': 'Garmin Fenix 7', 'price': Decimal('8999.99'), 'stock': 20, 'description': 'Smartwatch deportivo con GPS multibanda', 'category': 'Wearables'},
    {'name': 'Fitbit Charge 6', 'price': Decimal('2299.99'), 'stock': 50, 'description': 'Pulsera de actividad con monitor de frecuencia cardíaca', 'category': 'Wearables'},
    
    # Fotografía
    {'name': 'Canon EOS R6 Mark II', 'price': Decimal('34999.99'), 'stock': 8, 'description': 'Cámara mirrorless full-frame 24.2MP', 'category': 'Fotografía'},
    {'name': 'Sony A7 IV', 'price': Decimal('32999.99'), 'stock': 10, 'description': 'Cámara mirrorless 33MP con video 4K 60fps', 'category': 'Fotografía'},
    {'name': 'DJI Mini 4 Pro', 'price': Decimal('12999.99'), 'stock': 15, 'description': 'Drone compacto con cámara 4K HDR', 'category': 'Fotografía'},
    {'name': 'GoPro Hero 12', 'price': Decimal('6999.99'), 'stock': 25, 'description': 'Cámara de acción 5.3K con estabilización', 'category': 'Fotografía'},
    
    # Hogar Inteligente
    {'name': 'Amazon Echo Show 15', 'price': Decimal('4499.99'), 'stock': 30, 'description': 'Smart display de 15 pulgadas con Alexa', 'category': 'Hogar Inteligente'},
    {'name': 'Google Nest Hub Max', 'price': Decimal('3299.99'), 'stock': 35, 'description': 'Pantalla inteligente con Google Assistant', 'category': 'Hogar Inteligente'},
    {'name': 'Ring Video Doorbell Pro 2', 'price': Decimal('3999.99'), 'stock': 40, 'description': 'Timbre inteligente con video HD', 'category': 'Hogar Inteligente'},
    {'name': 'Philips Hue Starter Kit', 'price': Decimal('2799.99'), 'stock': 45, 'description': 'Kit de iluminación inteligente con 3 focos', 'category': 'Hogar Inteligente'},
    
    # Accesorios
    {'name': 'Anker PowerCore 20000', 'price': Decimal('899.99'), 'stock': 100, 'description': 'Batería externa 20000mAh con carga rápida', 'category': 'Accesorios'},
    {'name': 'Cable USB-C Thunderbolt 4', 'price': Decimal('499.99'), 'stock': 150, 'description': 'Cable certificado Thunderbolt 4 2 metros', 'category': 'Accesorios'},
    {'name': 'SanDisk Extreme Pro 1TB', 'price': Decimal('2199.99'), 'stock': 80, 'description': 'SSD externo portátil 1TB USB-C', 'category': 'Accesorios'},
    {'name': 'Belkin BoostCharge Pro', 'price': Decimal('1299.99'), 'stock': 90, 'description': 'Cargador inalámbrico 3 en 1 MagSafe', 'category': 'Accesorios'},
]

USERS_DATA = [
    # Clientes
    {'username': 'juan_cliente', 'email': 'juan.cliente@example.com', 'first_name': 'Juan', 'last_name': 'Pérez', 'role': 'CLIENTE', 'password': 'password123'},
    {'username': 'maria_gomez', 'email': 'maria.gomez@example.com', 'first_name': 'María', 'last_name': 'Gómez', 'role': 'CLIENTE', 'password': 'password123'},
    {'username': 'pedro_lopez', 'email': 'pedro.lopez@example.com', 'first_name': 'Pedro', 'last_name': 'López', 'role': 'CLIENTE', 'password': 'password123'},
    {'username': 'ana_martinez', 'email': 'ana.martinez@example.com', 'first_name': 'Ana', 'last_name': 'Martínez', 'role': 'CLIENTE', 'password': 'password123'},
    {'username': 'luis_rodriguez', 'email': 'luis.rodriguez@example.com', 'first_name': 'Luis', 'last_name': 'Rodríguez', 'role': 'CLIENTE', 'password': 'password123'},
    {'username': 'carmen_sanchez', 'email': 'carmen.sanchez@example.com', 'first_name': 'Carmen', 'last_name': 'Sánchez', 'role': 'CLIENTE', 'password': 'password123'},
    {'username': 'jorge_ramirez', 'email': 'jorge.ramirez@example.com', 'first_name': 'Jorge', 'last_name': 'Ramírez', 'role': 'CLIENTE', 'password': 'password123'},
    {'username': 'sofia_torres', 'email': 'sofia.torres@example.com', 'first_name': 'Sofía', 'last_name': 'Torres', 'role': 'CLIENTE', 'password': 'password123'},
    {'username': 'diego_flores', 'email': 'diego.flores@example.com', 'first_name': 'Diego', 'last_name': 'Flores', 'role': 'CLIENTE', 'password': 'password123'},
    {'username': 'laura_rivera', 'email': 'laura.rivera@example.com', 'first_name': 'Laura', 'last_name': 'Rivera', 'role': 'CLIENTE', 'password': 'password123'},
    
    # Managers
    {'username': 'carlos_manager', 'email': 'carlos_manager@example.com', 'first_name': 'Carlos', 'last_name': 'Manager', 'role': 'MANAGER', 'password': 'manager123'},
    {'username': 'ana_manager', 'email': 'ana_manager@example.com', 'first_name': 'Ana', 'last_name': 'Manager', 'role': 'MANAGER', 'password': 'manager123'},
    {'username': 'luis_manager', 'email': 'luis_manager@example.com', 'first_name': 'Luis', 'last_name': 'Manager', 'role': 'MANAGER', 'password': 'manager123'},
    {'username': 'sofia_manager', 'email': 'sofia_manager@example.com', 'first_name': 'Sofia', 'last_name': 'Manager', 'role': 'MANAGER', 'password': 'manager123'},
    {'username': 'miguel_manager', 'email': 'miguel_manager@example.com', 'first_name': 'Miguel', 'last_name': 'Manager', 'role': 'MANAGER', 'password': 'manager123'},
    {'username': 'laura_manager', 'email': 'laura_manager@example.com', 'first_name': 'Laura', 'last_name': 'Manager', 'role': 'MANAGER', 'password': 'manager123'},
    
    # Admins
    {'username': 'admin', 'email': 'admin@example.com', 'first_name': 'Admin', 'last_name': 'System', 'role': 'ADMIN', 'password': 'admin123'},
    {'username': 'superadmin', 'email': 'superadmin@example.com', 'first_name': 'Super', 'last_name': 'Admin', 'role': 'ADMIN', 'password': 'admin123'},
]

REASONS_FOR_RETURN = [
    "Producto defectuoso, no enciende correctamente",
    "Llegó con daños físicos en la caja y el producto",
    "No es compatible con mis dispositivos",
    "La descripción no coincide con el producto recibido",
    "Producto usado, no es nuevo como se anunció",
    "Rendimiento inferior al esperado",
    "Problemas de batería, se descarga muy rápido",
    "Pantalla con pixeles muertos",
    "No cumple con mis expectativas",
    "Compré uno mejor en otro lugar",
    "Audio con distorsión y ruido",
    "Conectividad Bluetooth defectuosa",
    "Carcasa rayada y con golpes",
    "No incluye todos los accesorios prometidos",
    "Calentamiento excesivo durante el uso",
]

# ============================================================================
# FUNCIONES DE POBLACIÓN
# ============================================================================

def clear_database():
    """Limpia toda la base de datos (opcional)"""
    print("\n" + "="*80)
    print("LIMPIANDO BASE DE DATOS...")
    print("="*80)
    
    WalletTransaction.objects.all().delete()
    Wallet.objects.all().delete()
    Return.objects.all().delete()
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    
    print("✅ Base de datos limpiada")


def create_categories():
    """Crea todas las categorías"""
    print("\n" + "="*80)
    print("CREANDO CATEGORÍAS...")
    print("="*80)
    
    categories = {}
    for cat_data in CATEGORIES_DATA:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description']
            }
        )
        categories[cat_data['name']] = category
        status = "✅ Creada" if created else "ℹ️  Ya existía"
        print(f"{status}: {category.name}")
    
    print(f"\n📊 Total categorías: {len(categories)}")
    return categories


def create_products(categories):
    """Crea todos los productos"""
    print("\n" + "="*80)
    print("CREANDO PRODUCTOS...")
    print("="*80)
    
    products = []
    for prod_data in PRODUCTS_DATA:
        category = categories.get(prod_data['category'])
        if not category:
            print(f"⚠️  Categoría no encontrada: {prod_data['category']}")
            continue
        
        product, created = Product.objects.get_or_create(
            name=prod_data['name'],
            defaults={
                'price': prod_data['price'],
                'stock': prod_data['stock'],
                'description': prod_data['description'],
                'category': category,
                'is_active': True
            }
        )
        products.append(product)
        status = "✅ Creado" if created else "ℹ️  Ya existía"
        print(f"{status}: {product.name} - ${product.price} (Stock: {product.stock})")
    
    print(f"\n📊 Total productos: {len(products)}")
    return products


def create_users():
    """Crea todos los usuarios"""
    print("\n" + "="*80)
    print("CREANDO USUARIOS...")
    print("="*80)
    
    users = {'clientes': [], 'managers': [], 'admins': []}
    
    for user_data in USERS_DATA:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'role': user_data['role']
            }
        )
        
        if created:
            user.set_password(user_data['password'])
            user.save()
        
        if user_data['role'] == 'CLIENTE':
            users['clientes'].append(user)
        elif user_data['role'] == 'MANAGER':
            users['managers'].append(user)
        else:
            users['admins'].append(user)
        
        status = "✅ Creado" if created else "ℹ️  Ya existía"
        print(f"{status}: {user.username} ({user.role}) - {user.email}")
    
    print(f"\n📊 Resumen:")
    print(f"   - Clientes: {len(users['clientes'])}")
    print(f"   - Managers: {len(users['managers'])}")
    print(f"   - Admins: {len(users['admins'])}")
    
    return users


def create_orders(users, products):
    """Crea órdenes variadas para los clientes"""
    print("\n" + "="*80)
    print("CREANDO ÓRDENES...")
    print("="*80)
    
    orders = []
    # Estados disponibles en Order.OrderStatus (evitar PAID para no disparar signal de Delivery)
    statuses = ['DELIVERED', 'SHIPPED', 'PENDING', 'DELIVERED', 'DELIVERED', 'DELIVERED']  # Más DELIVERED para poder devolver
    
    # Crear 30-50 órdenes
    for i in range(40):
        cliente = random.choice(users['clientes'])
        status = random.choice(statuses)
        
        order = Order.objects.create(
            user=cliente,
            status=status
        )
        
        # Agregar 1-3 items a la orden
        num_items = random.randint(1, 3)
        selected_products = random.sample(products, min(num_items, len(products)))
        
        total = Decimal('0')
        for product in selected_products:
            quantity = random.randint(1, 2)
            price = product.price
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )
            
            total += price * quantity
        
        order.total_price = total
        order.save()
        
        # Modificar fecha de creación para simular órdenes antiguas
        days_ago = random.randint(1, 60)
        order.created_at = datetime.now() - timedelta(days=days_ago)
        order.save(update_fields=['created_at'])
        
        orders.append(order)
        
        items_str = ", ".join([f"{item.product.name} x{item.quantity}" for item in order.items.all()])
        print(f"✅ Orden #{order.id} - {cliente.username} - {order.get_status_display()} - ${order.total_price}")
        print(f"   Items: {items_str}")
    
    print(f"\n📊 Total órdenes creadas: {len(orders)}")
    return orders


def create_returns(orders, users):
    """Crea devoluciones variadas"""
    print("\n" + "="*80)
    print("CREANDO DEVOLUCIONES...")
    print("="*80)
    
    returns = []
    statuses = ['REQUESTED', 'IN_EVALUATION', 'APPROVED', 'REJECTED', 'REQUESTED', 'APPROVED']
    refund_methods = ['WALLET', 'ORIGINAL', 'WALLET', 'WALLET']  # Más WALLET
    reason_choices = ['DEFECTIVE', 'WRONG_ITEM', 'NOT_AS_DESCRIBED', 'CHANGED_MIND', 'OTHER']
    
    # Solo crear devoluciones para órdenes DELIVERED
    delivered_orders = [o for o in orders if o.status == 'DELIVERED']
    
    # Crear 15-25 devoluciones
    num_returns = min(20, len(delivered_orders))
    selected_orders = random.sample(delivered_orders, num_returns)
    
    for order in selected_orders:
        # Seleccionar un item aleatorio de la orden
        items = list(order.items.all())
        if not items:
            continue
        
        order_item = random.choice(items)
        status = random.choice(statuses)
        refund_method = random.choice(refund_methods)
        reason_choice = random.choice(reason_choices)
        description = random.choice(REASONS_FOR_RETURN)
        
        # Fecha de devolución (después de la entrega)
        days_after_delivery = random.randint(1, 25)
        created_at = order.created_at + timedelta(days=days_after_delivery)
        
        ret = Return.objects.create(
            order=order,
            product=order_item.product,
            user=order.user,
            reason=reason_choice,
            description=description,
            status=status,
            refund_method=refund_method,
            created_at=created_at,
            updated_at=created_at
        )
        
        # Si está aprobada, procesar reembolso
        if status == 'APPROVED':
            ret.refund_amount = order_item.price * order_item.quantity
            ret.refund_processed = True
            ret.save()
            
            # Crear/actualizar billetera si el método es WALLET
            if refund_method == 'WALLET':
                wallet, _ = Wallet.objects.get_or_create(
                    user=order.user,
                    defaults={'balance': Decimal('0')}
                )
                
                # Crear transacción
                WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='REFUND',
                    amount=ret.refund_amount,
                    balance_after=wallet.balance + ret.refund_amount,
                    status='COMPLETED',
                    description=f"Reembolso por devolución #{ret.id} - {order_item.product.name}",
                    reference_id=f"RETURN-{ret.id}"
                )
                
                wallet.balance += ret.refund_amount
                wallet.save()
        
        # Si está rechazada, agregar razón
        if status == 'REJECTED':
            rejection_reasons = [
                "El producto está en perfectas condiciones",
                "No cumple con la política de devoluciones",
                "Producto usado más allá del uso normal",
                "Plazo de devolución excedido",
                "Daños causados por el usuario"
            ]
            ret.rejection_reason = random.choice(rejection_reasons)
            ret.save()
        
        returns.append(ret)
        
        print(f"✅ Devolución #{ret.id} - {order.user.username} - {ret.get_status_display()}")
        print(f"   Producto: {order_item.product.name} - Razón: {ret.get_reason_display()}")
        if status == 'APPROVED' and refund_method == 'WALLET':
            print(f"   💰 Reembolso: ${ret.refund_amount}")
    
    print(f"\n📊 Total devoluciones creadas: {len(returns)}")
    return returns


def create_additional_wallet_transactions(users):
    """Crea transacciones adicionales en las billeteras"""
    print("\n" + "="*80)
    print("CREANDO TRANSACCIONES ADICIONALES...")
    print("="*80)
    
    transactions = []
    
    # Obtener clientes con billetera
    wallets = Wallet.objects.filter(user__in=users['clientes'])
    
    for wallet in wallets:
        # Crear 2-5 transacciones adicionales
        num_transactions = random.randint(2, 5)
        
        for _ in range(num_transactions):
            tx_type = random.choice(['DEPOSIT', 'WITHDRAWAL', 'PURCHASE'])
            
            if tx_type == 'DEPOSIT':
                amount = Decimal(random.randint(500, 5000))
                old_balance = wallet.balance
                wallet.balance += amount
                
                transaction = WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='DEPOSIT',
                    amount=amount,
                    balance_after=wallet.balance,
                    status='COMPLETED',
                    description=f"Depósito a billetera",
                    reference_id=f"DEP-{random.randint(1000, 9999)}"
                )
                
            elif tx_type == 'WITHDRAWAL' and wallet.balance > 1000:
                amount = Decimal(random.randint(100, int(wallet.balance / 2)))
                old_balance = wallet.balance
                wallet.balance -= amount
                
                transaction = WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='WITHDRAWAL',
                    amount=amount,
                    balance_after=wallet.balance,
                    status='COMPLETED',
                    description=f"Retiro de billetera",
                    reference_id=f"WTH-{random.randint(1000, 9999)}"
                )
                
            elif tx_type == 'PURCHASE' and wallet.balance > 500:
                amount = Decimal(random.randint(100, min(2000, int(wallet.balance))))
                old_balance = wallet.balance
                wallet.balance -= amount
                
                transaction = WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='PURCHASE',
                    amount=amount,
                    balance_after=wallet.balance,
                    status='COMPLETED',
                    description=f"Compra con billetera",
                    reference_id=f"PUR-{random.randint(1000, 9999)}"
                )
            else:
                continue
            
            wallet.save()
            transactions.append(transaction)
            
            print(f"✅ {transaction.get_transaction_type_display()} - {wallet.user.username} - ${amount}")
    
    print(f"\n📊 Total transacciones adicionales: {len(transactions)}")


def print_summary():
    """Imprime resumen final"""
    print("\n" + "="*80)
    print("RESUMEN FINAL DE POBLACIÓN")
    print("="*80)
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   ├─ Categorías: {Category.objects.count()}")
    print(f"   ├─ Productos: {Product.objects.count()}")
    print(f"   ├─ Usuarios: {User.objects.count()}")
    print(f"   │  ├─ Clientes: {User.objects.filter(role='CLIENTE').count()}")
    print(f"   │  ├─ Managers: {User.objects.filter(role='MANAGER').count()}")
    print(f"   │  └─ Admins: {User.objects.filter(role='ADMIN').count()}")
    print(f"   ├─ Órdenes: {Order.objects.count()}")
    print(f"   │  ├─ Entregadas: {Order.objects.filter(status='DELIVERED').count()}")
    print(f"   │  ├─ En tránsito: {Order.objects.filter(status='IN_TRANSIT').count()}")
    print(f"   │  └─ Pendientes: {Order.objects.filter(status='PENDING').count()}")
    print(f"   ├─ Items de órdenes: {OrderItem.objects.count()}")
    print(f"   ├─ Devoluciones: {Return.objects.count()}")
    print(f"   │  ├─ Solicitadas: {Return.objects.filter(status='REQUESTED').count()}")
    print(f"   │  ├─ En evaluación: {Return.objects.filter(status='IN_EVALUATION').count()}")
    print(f"   │  ├─ Aprobadas: {Return.objects.filter(status='APPROVED').count()}")
    print(f"   │  └─ Rechazadas: {Return.objects.filter(status='REJECTED').count()}")
    print(f"   ├─ Billeteras: {Wallet.objects.count()}")
    print(f"   └─ Transacciones: {WalletTransaction.objects.count()}")
    
    # Estadísticas de billeteras
    print(f"\n💰 BILLETERAS:")
    wallets = Wallet.objects.all().order_by('-balance')[:5]
    for wallet in wallets:
        print(f"   • {wallet.user.username}: ${wallet.balance}")
    
    # Productos más vendidos
    print(f"\n🏆 TOP 5 PRODUCTOS MÁS VENDIDOS:")
    from django.db.models import Sum, Count
    top_products = OrderItem.objects.values('product__name').annotate(
        total_sold=Sum('quantity'),
        orders_count=Count('order', distinct=True)
    ).order_by('-total_sold')[:5]
    
    for i, prod in enumerate(top_products, 1):
        print(f"   {i}. {prod['product__name']}: {prod['total_sold']} unidades en {prod['orders_count']} órdenes")
    
    print("\n" + "="*80)
    print("✅ POBLACIÓN COMPLETA FINALIZADA")
    print("="*80)


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Ejecuta todo el proceso de población"""
    print("\n" + "="*80)
    print("POBLADOR COMPLETO DE BASE DE DATOS")
    print("="*80)
    
    import sys
    
    # Preguntar si limpiar la base de datos
    print("\n⚠️  ¿Deseas LIMPIAR la base de datos antes de poblar?")
    print("   (Esto ELIMINARÁ todos los datos existentes)")
    response = input("   Escribe 'SI' para confirmar: ")
    
    if response.upper() == 'SI':
        clear_database()
    
    # Poblar base de datos
    categories = create_categories()
    products = create_products(categories)
    users = create_users()
    orders = create_orders(users, products)
    returns = create_returns(orders, users)
    create_additional_wallet_transactions(users)
    
    # Mostrar resumen
    print_summary()
    
    print("\n✅ Proceso completado exitosamente!")
    print("\n📝 CREDENCIALES DE ACCESO:")
    print("   Cliente: juan_cliente / password123")
    print("   Manager: carlos_manager / manager123")
    print("   Admin: admin / admin123")


if __name__ == '__main__':
    main()
