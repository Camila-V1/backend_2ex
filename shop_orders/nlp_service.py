"""
Servicio de procesamiento de lenguaje natural para el carrito de compras
Permite a los usuarios agregar productos usando comandos en texto o voz
"""
import re
from products.models import Product, Category


class CartNLPService:
    """
    Servicio para interpretar comandos en lenguaje natural relacionados con el carrito
    """
    
    # Palabras clave para acciones
    ACTION_KEYWORDS = {
        'add': ['agrega', 'agregar', 'añade', 'añadir', 'quiero', 'dame', 'comprar', 'necesito'],
        'remove': ['quita', 'quitar', 'elimina', 'eliminar', 'borra', 'borrar', 'saca', 'sacar'],
        'clear': ['vacía', 'vaciar', 'limpiar', 'limpía', 'borrar todo', 'quitar todo']
    }
    
    # Palabras clave para categorías
    CATEGORY_KEYWORDS = {
        'electrónica': ['electrónica', 'electronico', 'tecnología', 'tech'],
        'ropa': ['ropa', 'vestir', 'prenda', 'vestimenta'],
        'hogar': ['hogar', 'casa', 'cocina'],
        'deportes': ['deporte', 'deportes', 'fitness', 'gym'],
    }
    
    @staticmethod
    def parse_cart_command(prompt):
        """
        Interpreta un comando de lenguaje natural para el carrito
        
        Args:
            prompt (str): Comando en lenguaje natural
            
        Returns:
            dict: {
                'action': 'add'|'remove'|'clear',
                'items': [{'product_id': int, 'quantity': int, 'name': str}],
                'error': str|None
            }
        """
        prompt_lower = prompt.lower().strip()
        
        # Detectar acción
        action = CartNLPService._detect_action(prompt_lower)
        
        if action == 'clear':
            return {
                'action': 'clear',
                'items': [],
                'error': None
            }
        
        # Extraer productos y cantidades
        items = CartNLPService._extract_items(prompt_lower)
        
        if not items:
            return {
                'action': action,
                'items': [],
                'error': 'No se pudieron identificar productos en el comando.'
            }
        
        # Buscar productos en la base de datos
        resolved_items = []
        for item in items:
            product = CartNLPService._find_product(item['name'], item.get('category'))
            if product:
                resolved_items.append({
                    'product_id': product.id,
                    'product': product.id,  # Para compatibilidad con serializer
                    'quantity': item['quantity'],
                    'name': product.name,
                    'price': str(product.price),
                    'stock_available': product.stock
                })
            else:
                return {
                    'action': action,
                    'items': [],
                    'error': f'No se encontró el producto: "{item["name"]}"'
                }
        
        return {
            'action': action,
            'items': resolved_items,
            'error': None
        }
    
    @staticmethod
    def _detect_action(prompt):
        """Detecta la acción a realizar"""
        # Verificar clear primero
        for keyword in CartNLPService.ACTION_KEYWORDS['clear']:
            if keyword in prompt:
                return 'clear'
        
        # Verificar remove
        for keyword in CartNLPService.ACTION_KEYWORDS['remove']:
            if keyword in prompt:
                return 'remove'
        
        # Por defecto: add
        return 'add'
    
    @staticmethod
    def _extract_items(prompt):
        """
        Extrae productos y cantidades del comando
        Ejemplos:
        - "agrega 2 smartphones" -> [{'name': 'smartphones', 'quantity': 2}]
        - "quiero 3 laptops y 1 mouse" -> [{'name': 'laptops', 'quantity': 3}, {'name': 'mouse', 'quantity': 1}]
        """
        items = []
        
        # Patrón: número + nombre del producto
        # Ej: "2 smartphones", "3 laptops"
        pattern = r'(\d+)\s+([a-záéíóúñ\s]+?)(?=\s+y\s+|\s*$|,)'
        matches = re.findall(pattern, prompt)
        
        for match in matches:
            quantity = int(match[0])
            name = match[1].strip()
            
            # Limpiar palabras comunes
            name = re.sub(r'\b(el|la|los|las|un|una|unos|unas|de|del)\b', '', name).strip()
            
            if name:
                items.append({
                    'name': name,
                    'quantity': quantity
                })
        
        # Si no se encontró patrón con números, buscar solo nombres
        if not items:
            # Patrón: nombres de productos sin números (asume cantidad = 1)
            # Limpia el prompt de palabras de acción
            cleaned = prompt
            for action_list in CartNLPService.ACTION_KEYWORDS.values():
                for keyword in action_list:
                    cleaned = cleaned.replace(keyword, '')
            
            cleaned = cleaned.strip()
            if cleaned:
                items.append({
                    'name': cleaned,
                    'quantity': 1
                })
        
        return items
    
    @staticmethod
    def _find_product(search_term, category=None):
        """
        Busca un producto por nombre o descripción
        Implementa búsqueda difusa (fuzzy search)
        """
        # Buscar por coincidencia exacta (case-insensitive)
        product = Product.objects.filter(
            name__icontains=search_term,
            is_active=True
        ).first()
        
        if product:
            return product
        
        # Buscar en descripción
        product = Product.objects.filter(
            description__icontains=search_term,
            is_active=True
        ).first()
        
        if product:
            return product
        
        # Buscar palabras individuales
        words = search_term.split()
        for word in words:
            if len(word) > 3:  # Solo palabras significativas
                product = Product.objects.filter(
                    name__icontains=word,
                    is_active=True
                ).first()
                if product:
                    return product
        
        return None
    
    @staticmethod
    def get_suggestions(partial_name):
        """
        Obtiene sugerencias de productos basadas en texto parcial
        Útil para autocompletado
        """
        products = Product.objects.filter(
            name__icontains=partial_name,
            is_active=True
        )[:5]  # Top 5 sugerencias
        
        return [
            {
                'id': p.id,
                'name': p.name,
                'price': str(p.price),
                'stock': p.stock,
                'category': p.category.name if p.category else None
            }
            for p in products
        ]
