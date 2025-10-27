"""
Script para poblar la base de datos con datos de prueba
Incluye usuarios, categorías, productos, órdenes y reviews
Ejecutar con: python seed_data.py
"""

import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.contrib.auth import get_user_model
from products.models import Category, Product, Review
from shop_orders.models import Order, OrderItem

User = get_user_model()

# Colores para output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def clear_database():
    """Limpia todos los datos existentes"""
    print_info("Limpiando base de datos...")
    
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    Review.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    User.objects.all().delete()
    
    print_success("Base de datos limpiada")

def create_users():
    """Crea usuarios de prueba con diferentes roles"""
    print_info("Creando usuarios...")
    
    users_data = [
        # Administradores
        {
            'username': 'admin',
            'email': 'admin@ecommerce.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'Principal',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': True
        },
        {
            'username': 'maria_admin',
            'email': 'maria.admin@ecommerce.com',
            'password': 'maria123',
            'first_name': 'María',
            'last_name': 'González',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': False
        },
        
        # Managers
        {
            'username': 'carlos_manager',
            'email': 'carlos.manager@ecommerce.com',
            'password': 'carlos123',
            'first_name': 'Carlos',
            'last_name': 'Rodríguez',
            'role': 'MANAGER',
            'is_staff': True,
            'is_superuser': False
        },
        {
            'username': 'ana_manager',
            'email': 'ana.manager@ecommerce.com',
            'password': 'ana123',
            'first_name': 'Ana',
            'last_name': 'Martínez',
            'role': 'MANAGER',
            'is_staff': True,
            'is_superuser': False
        },
        
        # Cajeros
        {
            'username': 'luis_cajero',
            'email': 'luis.cajero@ecommerce.com',
            'password': 'luis123',
            'first_name': 'Luis',
            'last_name': 'López',
            'role': 'CAJERO',
            'is_staff': True,
            'is_superuser': False
        },
        {
            'username': 'sofia_cajero',
            'email': 'sofia.cajero@ecommerce.com',
            'password': 'sofia123',
            'first_name': 'Sofía',
            'last_name': 'Fernández',
            'role': 'CAJERO',
            'is_staff': True,
            'is_superuser': False
        },
        
        # Clientes regulares
        {
            'username': 'juan_cliente',
            'email': 'juan@email.com',
            'password': 'juan123',
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'role': None,
            'is_staff': False,
            'is_superuser': False
        },
        {
            'username': 'laura_cliente',
            'email': 'laura@email.com',
            'password': 'laura123',
            'first_name': 'Laura',
            'last_name': 'Sánchez',
            'role': None,
            'is_staff': False,
            'is_superuser': False
        },
        {
            'username': 'pedro_cliente',
            'email': 'pedro@email.com',
            'password': 'pedro123',
            'first_name': 'Pedro',
            'last_name': 'García',
            'role': None,
            'is_staff': False,
            'is_superuser': False
        },
        {
            'username': 'carmen_cliente',
            'email': 'carmen@email.com',
            'password': 'carmen123',
            'first_name': 'Carmen',
            'last_name': 'Torres',
            'role': None,
            'is_staff': False,
            'is_superuser': False
        },
        {
            'username': 'diego_cliente',
            'email': 'diego@email.com',
            'password': 'diego123',
            'first_name': 'Diego',
            'last_name': 'Ramírez',
            'role': None,
            'is_staff': False,
            'is_superuser': False
        },
        {
            'username': 'elena_cliente',
            'email': 'elena@email.com',
            'password': 'elena123',
            'first_name': 'Elena',
            'last_name': 'Morales',
            'role': None,
            'is_staff': False,
            'is_superuser': False
        },
    ]
    
    created_users = []
    for user_data in users_data:
        password = user_data.pop('password')
        user = User.objects.create_user(**user_data)
        user.set_password(password)
        user.save()
        created_users.append(user)
        print_success(f"Usuario creado: {user.username} ({user.role or 'Cliente'})")
    
    return created_users

def create_categories():
    """Crea categorías de productos"""
    print_info("Creando categorías...")
    
    categories_data = [
        {'name': 'Electrónica', 'description': 'Dispositivos electrónicos y accesorios'},
        {'name': 'Computadoras', 'description': 'Laptops, desktops y accesorios de computación'},
        {'name': 'Celulares', 'description': 'Smartphones y accesorios móviles'},
        {'name': 'Audio', 'description': 'Audífonos, parlantes y equipos de audio'},
        {'name': 'Gaming', 'description': 'Consolas, videojuegos y accesorios gaming'},
        {'name': 'Hogar', 'description': 'Electrodomésticos y artículos para el hogar'},
        {'name': 'Oficina', 'description': 'Artículos y equipos de oficina'},
        {'name': 'Deportes', 'description': 'Equipamiento y ropa deportiva'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category = Category.objects.create(**cat_data)
        categories.append(category)
        print_success(f"Categoría creada: {category.name}")
    
    return categories

def create_products(categories):
    """Crea productos variados"""
    print_info("Creando productos...")
    
    products_data = [
        # Electrónica
        {'name': 'Smart TV Samsung 55"', 'description': 'Televisor Smart 4K UHD de 55 pulgadas', 'price': 4999.99, 'stock': 25, 'category': 'Electrónica', 'warranty_info': '2 años de garantía'},
        {'name': 'Smart TV LG 43"', 'description': 'Televisor Smart Full HD de 43 pulgadas', 'price': 3299.99, 'stock': 30, 'category': 'Electrónica', 'warranty_info': '1 año de garantía'},
        {'name': 'Tablet iPad Air', 'description': 'Tablet Apple iPad Air 64GB', 'price': 5999.99, 'stock': 15, 'category': 'Electrónica', 'warranty_info': '1 año de garantía'},
        
        # Computadoras
        {'name': 'Laptop Dell Inspiron 15', 'description': 'Laptop Intel i5, 8GB RAM, 256GB SSD', 'price': 6999.99, 'stock': 20, 'category': 'Computadoras', 'warranty_info': '1 año de garantía'},
        {'name': 'Laptop HP Pavilion', 'description': 'Laptop Intel i7, 16GB RAM, 512GB SSD', 'price': 9999.99, 'stock': 12, 'category': 'Computadoras', 'warranty_info': '2 años de garantía'},
        {'name': 'MacBook Air M2', 'description': 'MacBook Air con chip M2, 8GB RAM, 256GB SSD', 'price': 12999.99, 'stock': 8, 'category': 'Computadoras', 'warranty_info': '1 año de garantía'},
        {'name': 'Monitor LG 27"', 'description': 'Monitor Full HD IPS 27 pulgadas', 'price': 1999.99, 'stock': 35, 'category': 'Computadoras', 'warranty_info': '3 años de garantía'},
        {'name': 'Teclado Mecánico RGB', 'description': 'Teclado mecánico gaming con iluminación RGB', 'price': 899.99, 'stock': 50, 'category': 'Computadoras', 'warranty_info': '1 año de garantía'},
        {'name': 'Mouse Logitech MX Master', 'description': 'Mouse inalámbrico ergonómico profesional', 'price': 1299.99, 'stock': 45, 'category': 'Computadoras', 'warranty_info': '2 años de garantía'},
        
        # Celulares
        {'name': 'iPhone 15 Pro', 'description': 'iPhone 15 Pro 256GB', 'price': 15999.99, 'stock': 10, 'category': 'Celulares', 'warranty_info': '1 año de garantía'},
        {'name': 'Samsung Galaxy S24', 'description': 'Samsung Galaxy S24 128GB', 'price': 11999.99, 'stock': 18, 'category': 'Celulares', 'warranty_info': '1 año de garantía'},
        {'name': 'Xiaomi Redmi Note 13', 'description': 'Xiaomi Redmi Note 13 128GB', 'price': 3999.99, 'stock': 40, 'category': 'Celulares', 'warranty_info': '1 año de garantía'},
        {'name': 'Funda iPhone Protectora', 'description': 'Funda protectora para iPhone con certificación militar', 'price': 299.99, 'stock': 100, 'category': 'Celulares', 'warranty_info': '6 meses de garantía'},
        {'name': 'Cargador Rápido 65W', 'description': 'Cargador USB-C de carga rápida 65W', 'price': 499.99, 'stock': 80, 'category': 'Celulares', 'warranty_info': '1 año de garantía'},
        
        # Audio
        {'name': 'AirPods Pro 2', 'description': 'Audífonos inalámbricos con cancelación de ruido', 'price': 2999.99, 'stock': 30, 'category': 'Audio', 'warranty_info': '1 año de garantía'},
        {'name': 'Sony WH-1000XM5', 'description': 'Audífonos over-ear con cancelación de ruido premium', 'price': 4999.99, 'stock': 22, 'category': 'Audio', 'warranty_info': '2 años de garantía'},
        {'name': 'JBL Flip 6', 'description': 'Parlante Bluetooth portátil resistente al agua', 'price': 1499.99, 'stock': 45, 'category': 'Audio', 'warranty_info': '1 año de garantía'},
        {'name': 'Bose SoundLink Mini', 'description': 'Parlante Bluetooth compacto con gran sonido', 'price': 2499.99, 'stock': 28, 'category': 'Audio', 'warranty_info': '1 año de garantía'},
        
        # Gaming
        {'name': 'PlayStation 5', 'description': 'Consola PS5 con lector de discos', 'price': 7999.99, 'stock': 15, 'category': 'Gaming', 'warranty_info': '1 año de garantía'},
        {'name': 'Xbox Series X', 'description': 'Consola Xbox Series X 1TB', 'price': 7499.99, 'stock': 12, 'category': 'Gaming', 'warranty_info': '1 año de garantía'},
        {'name': 'Nintendo Switch OLED', 'description': 'Consola Nintendo Switch modelo OLED', 'price': 4999.99, 'stock': 25, 'category': 'Gaming', 'warranty_info': '1 año de garantía'},
        {'name': 'Control DualSense PS5', 'description': 'Control inalámbrico para PlayStation 5', 'price': 899.99, 'stock': 60, 'category': 'Gaming', 'warranty_info': '1 año de garantía'},
        {'name': 'Silla Gaming RGB', 'description': 'Silla ergonómica gaming con iluminación RGB', 'price': 3999.99, 'stock': 18, 'category': 'Gaming', 'warranty_info': '2 años de garantía'},
        
        # Hogar
        {'name': 'Aspiradora Robot', 'description': 'Aspiradora robot inteligente con mapeo láser', 'price': 3499.99, 'stock': 20, 'category': 'Hogar', 'warranty_info': '1 año de garantía'},
        {'name': 'Cafetera Express', 'description': 'Cafetera express automática con molinillo', 'price': 4999.99, 'stock': 15, 'category': 'Hogar', 'warranty_info': '2 años de garantía'},
        {'name': 'Microondas Digital', 'description': 'Microondas digital 25L con grill', 'price': 1299.99, 'stock': 25, 'category': 'Hogar', 'warranty_info': '1 año de garantía'},
        {'name': 'Licuadora Premium', 'description': 'Licuadora de alta potencia 1500W', 'price': 899.99, 'stock': 35, 'category': 'Hogar', 'warranty_info': '2 años de garantía'},
        
        # Oficina
        {'name': 'Silla Ergonómica Oficina', 'description': 'Silla de oficina ergonómica con soporte lumbar', 'price': 2499.99, 'stock': 30, 'category': 'Oficina', 'warranty_info': '3 años de garantía'},
        {'name': 'Escritorio Ajustable', 'description': 'Escritorio con altura ajustable eléctrico', 'price': 5999.99, 'stock': 12, 'category': 'Oficina', 'warranty_info': '5 años de garantía'},
        {'name': 'Lámpara LED Escritorio', 'description': 'Lámpara LED regulable con carga inalámbrica', 'price': 599.99, 'stock': 50, 'category': 'Oficina', 'warranty_info': '2 años de garantía'},
        {'name': 'Organizador Escritorio', 'description': 'Organizador de escritorio con carga USB', 'price': 399.99, 'stock': 40, 'category': 'Oficina', 'warranty_info': '1 año de garantía'},
        
        # Deportes
        {'name': 'Smartwatch Deportivo', 'description': 'Reloj inteligente con GPS y monitor cardíaco', 'price': 2999.99, 'stock': 35, 'category': 'Deportes', 'warranty_info': '1 año de garantía'},
        {'name': 'Bicicleta Estática', 'description': 'Bicicleta estática con pantalla LCD', 'price': 3999.99, 'stock': 10, 'category': 'Deportes', 'warranty_info': '2 años de garantía'},
        {'name': 'Mancuernas Ajustables', 'description': 'Set de mancuernas ajustables 5-25kg', 'price': 1999.99, 'stock': 22, 'category': 'Deportes', 'warranty_info': '5 años de garantía'},
        {'name': 'Banda Elástica Set', 'description': 'Set de 5 bandas elásticas de resistencia', 'price': 299.99, 'stock': 60, 'category': 'Deportes', 'warranty_info': '1 año de garantía'},
    ]
    
    # Mapear categorías por nombre
    category_map = {cat.name: cat for cat in categories}
    
    products = []
    for prod_data in products_data:
        category_name = prod_data.pop('category')
        prod_data['category'] = category_map[category_name]
        product = Product.objects.create(**prod_data)
        products.append(product)
        print_success(f"Producto creado: {product.name} - ${product.price}")
    
    return products

def create_reviews(users, products):
    """Crea reviews de clientes para productos"""
    print_info("Creando reviews...")
    
    # Solo clientes (sin roles de staff)
    customers = [u for u in users if not u.role]
    
    reviews_count = 0
    for product in products:
        # Cada producto recibe entre 2-8 reviews
        num_reviews = random.randint(2, 8)
        reviewers = random.sample(customers, min(num_reviews, len(customers)))
        
        for user in reviewers:
            rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 15, 30, 40])[0]
            
            comments = {
                5: [
                    "¡Excelente producto! Superó mis expectativas.",
                    "Muy satisfecho con la compra, totalmente recomendado.",
                    "Calidad premium, vale cada peso.",
                    "Perfecto, justo lo que necesitaba.",
                ],
                4: [
                    "Buen producto, cumple con lo prometido.",
                    "Muy bueno, pequeños detalles a mejorar.",
                    "Satisfecho con la compra, buena relación calidad-precio.",
                    "Recomendado, funciona muy bien.",
                ],
                3: [
                    "Producto aceptable, esperaba un poco más.",
                    "Cumple pero nada extraordinario.",
                    "Está bien para el precio.",
                ],
                2: [
                    "No cumplió mis expectativas.",
                    "Calidad regular, esperaba mejor.",
                ],
                1: [
                    "Decepcionante, no lo recomiendo.",
                    "Mala calidad, no vale la pena.",
                ],
            }
            
            comment = random.choice(comments[rating])
            
            try:
                Review.objects.create(
                    product=product,
                    user=user,
                    rating=rating,
                    comment=comment
                )
                reviews_count += 1
            except:
                pass  # Skip si ya existe review de este usuario para este producto
    
    print_success(f"{reviews_count} reviews creadas")

def create_orders(users, products):
    """Crea órdenes de compra con suficientes datos para ML"""
    print_info("Creando órdenes (datos para ML)...")
    
    # Solo clientes
    customers = [u for u in users if not u.role]
    
    # Crear órdenes de los últimos 12 meses para tener buen historial
    from django.utils import timezone
    end_date = timezone.now()
    start_date = end_date - timedelta(days=365)
    
    orders_created = 0
    items_created = 0
    
    # Crear entre 150-200 órdenes para tener suficientes datos
    num_orders = random.randint(150, 200)
    
    for i in range(num_orders):
        # Fecha aleatoria en los últimos 12 meses
        random_days = random.randint(0, 365)
        order_date = end_date - timedelta(days=random_days)
        
        # Usuario aleatorio
        user = random.choice(customers)
        
        # Estado: mayoría pagadas para ML (80%), algunas pending/shipped/cancelled
        status = random.choices(
            [Order.OrderStatus.PAID, Order.OrderStatus.PENDING, Order.OrderStatus.SHIPPED, Order.OrderStatus.CANCELLED],
            weights=[80, 10, 5, 5]
        )[0]
        
        order = Order.objects.create(
            user=user,
            status=status,
            total_price=0
        )
        # Forzar la fecha de creación
        Order.objects.filter(pk=order.pk).update(created_at=order_date)
        
        # Agregar entre 1-5 productos a la orden
        num_items = random.randint(1, 5)
        selected_products = random.sample(products, num_items)
        
        total = Decimal('0.00')
        for product in selected_products:
            quantity = random.randint(1, 3)
            price = Decimal(str(product.price))
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )
            
            total += price * Decimal(str(quantity))
            items_created += 1
        
        # Actualizar total de la orden
        order.total_price = total
        order.save()
        orders_created += 1
    
    print_success(f"{orders_created} órdenes creadas con {items_created} items")
    print_success(f"Órdenes PAID (para ML): {Order.objects.filter(status=Order.OrderStatus.PAID).count()}")

def generate_credentials_file(users):
    """Genera archivo con credenciales de acceso"""
    print_info("Generando archivo de credenciales...")
    
    content = """
╔════════════════════════════════════════════════════════════════╗
║           CREDENCIALES DE ACCESO - ECOMMERCE API              ║
║                    Base de Datos Poblada                       ║
╚════════════════════════════════════════════════════════════════╝

📅 Generado: {}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👑 ADMINISTRADORES (ADMIN)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Usuario: admin
   Email: admin@ecommerce.com
   Password: admin123
   Rol: ADMIN (Superusuario)
   Permisos: Acceso total al sistema

2. Usuario: maria_admin
   Email: maria.admin@ecommerce.com
   Password: maria123
   Rol: ADMIN
   Permisos: Gestión completa sin superusuario

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👔 MANAGERS (MANAGER)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. Usuario: carlos_manager
   Email: carlos.manager@ecommerce.com
   Password: carlos123
   Rol: MANAGER
   Permisos: Gestión de órdenes, productos, reportes

4. Usuario: ana_manager
   Email: ana.manager@ecommerce.com
   Password: ana123
   Rol: MANAGER
   Permisos: Gestión de órdenes, productos, reportes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 CAJEROS (CAJERO)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. Usuario: luis_cajero
   Email: luis.cajero@ecommerce.com
   Password: luis123
   Rol: CAJERO
   Permisos: Ver órdenes y productos

6. Usuario: sofia_cajero
   Email: sofia.cajero@ecommerce.com
   Password: sofia123
   Rol: CAJERO
   Permisos: Ver órdenes y productos

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 CLIENTES (Sin rol especial)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7. Usuario: juan_cliente
   Email: juan@email.com
   Password: juan123
   Rol: Cliente
   
8. Usuario: laura_cliente
   Email: laura@email.com
   Password: laura123
   Rol: Cliente

9. Usuario: pedro_cliente
   Email: pedro@email.com
   Password: pedro123
   Rol: Cliente

10. Usuario: carmen_cliente
    Email: carmen@email.com
    Password: carmen123
    Rol: Cliente

11. Usuario: diego_cliente
    Email: diego@email.com
    Password: diego123
    Rol: Cliente

12. Usuario: elena_cliente
    Email: elena@email.com
    Password: elena123
    Rol: Cliente

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 ESTADÍSTICAS DE LA BASE DE DATOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Usuarios: {}
✓ Categorías: {}
✓ Productos: {}
✓ Reviews: {}
✓ Órdenes: {}
✓ Órdenes PAID (para ML): {}
✓ Items en órdenes: {}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 INFORMACIÓN DE AUTENTICACIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

API Base URL: http://127.0.0.1:8000/api/

Endpoints de autenticación:
  • Login: POST /api/users/login/
  • Registro: POST /api/users/register/
  • Profile: GET /api/users/profile/

Formato de login:
{{
  "username": "admin",
  "password": "admin123"
}}

Respuesta (incluye tokens JWT):
{{
  "refresh": "token_refresh...",
  "access": "token_access...",
  "user": {{...}}
}}

Usar token en headers:
Authorization: Bearer <access_token>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 MACHINE LEARNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

La base de datos ha sido poblada con suficientes datos para entrenar
el modelo de predicción de ventas:

✓ {} órdenes PAID (mínimo requerido: 10)
✓ Historial de 12 meses de ventas
✓ Múltiples productos y categorías

Para entrenar el modelo:
  python manage.py train_sales_model

Para obtener predicciones:
  GET /api/predictions/sales-forecast/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 NOTAS IMPORTANTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠ Estas credenciales son SOLO para desarrollo y pruebas
⚠ NO usar en producción
⚠ Cambiar todas las contraseñas antes de deploy

✓ Todas las contraseñas siguen el patrón: <nombre>123
✓ Los datos son generados aleatoriamente para pruebas
✓ Las órdenes tienen fechas de los últimos 12 meses

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 ENLACES ÚTILES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• API Docs (Swagger): http://127.0.0.1:8000/api/docs/
• API Docs (ReDoc): http://127.0.0.1:8000/api/redoc/
• Django Admin: http://127.0.0.1:8000/admin/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""".format(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        User.objects.count(),
        Category.objects.count(),
        Product.objects.count(),
        Review.objects.count(),
        Order.objects.count(),
        Order.objects.filter(status=Order.OrderStatus.PAID).count(),
        OrderItem.objects.count(),
        Order.objects.filter(status=Order.OrderStatus.PAID).count()
    )
    
    filename = 'CREDENCIALES_ACCESO.txt'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_success(f"Archivo generado: {filename}")

def main():
    """Función principal"""
    print("\n" + "="*70)
    print("  SCRIPT DE POBLACIÓN DE BASE DE DATOS")
    print("  E-commerce API con datos para Machine Learning")
    print("="*70 + "\n")
    
    try:
        # 1. Limpiar base de datos
        clear_database()
        print()
        
        # 2. Crear usuarios
        users = create_users()
        print()
        
        # 3. Crear categorías
        categories = create_categories()
        print()
        
        # 4. Crear productos
        products = create_products(categories)
        print()
        
        # 5. Crear reviews
        create_reviews(users, products)
        print()
        
        # 6. Crear órdenes (suficientes para ML)
        create_orders(users, products)
        print()
        
        # 7. Generar archivo de credenciales
        generate_credentials_file(users)
        print()
        
        # Resumen final
        print("="*70)
        print(f"{Colors.GREEN}✓ BASE DE DATOS POBLADA EXITOSAMENTE{Colors.END}")
        print("="*70)
        print(f"\n{Colors.BLUE}📊 RESUMEN:{Colors.END}")
        print(f"  • Usuarios: {User.objects.count()}")
        print(f"  • Categorías: {Category.objects.count()}")
        print(f"  • Productos: {Product.objects.count()}")
        print(f"  • Reviews: {Review.objects.count()}")
        print(f"  • Órdenes: {Order.objects.count()}")
        print(f"  • Órdenes PAID: {Order.objects.filter(status=Order.OrderStatus.PAID).count()}")
        print(f"  • Items en órdenes: {OrderItem.objects.count()}")
        print()
        print(f"{Colors.YELLOW}📁 Revisa el archivo CREDENCIALES_ACCESO.txt{Colors.END}")
        print()
        print(f"{Colors.BLUE}🤖 Para entrenar el modelo de ML:{Colors.END}")
        print(f"  python manage.py train_sales_model")
        print()
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {str(e)}{Colors.END}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
