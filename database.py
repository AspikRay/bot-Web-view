import json
import os
from typing import List, Dict, Optional

class Database:
    def __init__(self, filename='products.json'):
        self.filename = filename
        self.load()
    
    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = {
                'products': [],
                'orders': [],
                'categories': ['Лекарственные травы', 'Чайные сборы', 'Специи', 'Семена']
            }
            self.save()
    
    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    # Управление товарами
    def add_product(self, name: str, description: str, price: float, 
                   category: str, image_url: str = None, in_stock: bool = True) -> int:
        product_id = len(self.data['products']) + 1
        product = {
            'id': product_id,
            'name': name,
            'description': description,
            'price': price,
            'category': category,
            'image_url': image_url,
            'in_stock': in_stock
        }
        self.data['products'].append(product)
        self.save()
        return product_id
    
    def remove_product(self, product_id: int) -> bool:
        self.data['products'] = [p for p in self.data['products'] if p['id'] != product_id]
        self.save()
        return True
    
    def update_product(self, product_id: int, **kwargs) -> bool:
        for product in self.data['products']:
            if product['id'] == product_id:
                product.update(kwargs)
                self.save()
                return True
        return False
    
    def get_product(self, product_id: int) -> Optional[Dict]:
        return next((p for p in self.data['products'] if p['id'] == product_id), None)
    
    def get_all_products(self) -> List[Dict]:
        return self.data['products']
    
    def get_products_by_category(self, category: str) -> List[Dict]:
        return [p for p in self.data['products'] if p['category'] == category]
    
    # Управление заказами
    def add_order(self, user_id: int, username: str, products: List[Dict], 
                  total: float, contact: str) -> int:
        order_id = len(self.data['orders']) + 1
        order = {
            'id': order_id,
            'user_id': user_id,
            'username': username,
            'products': products,
            'total': total,
            'contact': contact,
            'status': 'new',
            'timestamp': str(os.popen('date').read().strip())
        }
        self.data['orders'].append(order)
        self.save()
        return order_id
    
    def get_orders(self) -> List[Dict]:
        return self.data['orders']
    
    def get_categories(self) -> List[str]:
        return self.data['categories']

db = Database()
