import sqlite3
import json
import os
from datetime import datetime
from typing import List, Optional
from models.schemas import Product, Order, OrderItem, OrderStatus

class Database:
    def __init__(self, db_path: str = "contoso_mesh.db"):
        self.db_path = db_path
        self.init_database()
        self.load_products()
    
    def init_database(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                stock INTEGER NOT NULL,
                next_availability TEXT,
                features TEXT,
                specifications TEXT
            )
        """)
        
        # Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                status TEXT NOT NULL,
                total_amount REAL,
                discount_applied REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                agent_logs TEXT
            )
        """)
        
        # Order items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL,
                total_price REAL,
                availability_status TEXT,
                next_availability TEXT,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def load_products(self):
        """Load products from JSON file into database."""
        products_file = os.path.join(os.path.dirname(__file__), "../../data/products.json")
        if not os.path.exists(products_file):
            return
        
        with open(products_file, "r") as f:
            products_data = json.load(f)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for product_data in products_data:
            cursor.execute("""
                INSERT OR REPLACE INTO products 
                (id, name, category, description, price, stock, next_availability, features, specifications)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_data["id"],
                product_data["name"],
                product_data["category"],
                product_data["description"],
                product_data["price"],
                product_data["stock"],
                product_data.get("next_availability"),
                json.dumps(product_data["features"]),
                json.dumps(product_data["specifications"])
            ))
        
        conn.commit()
        conn.close()
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """Get a single product by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return Product(
            id=row[0],
            name=row[1],
            category=row[2],
            description=row[3],
            price=row[4],
            stock=row[5],
            next_availability=row[6],
            features=json.loads(row[7]),
            specifications=json.loads(row[8])
        )
    
    def get_products(self, category: Optional[str] = None) -> List[Product]:
        """Get all products, optionally filtered by category."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
        else:
            cursor.execute("SELECT * FROM products")
        
        rows = cursor.fetchall()
        conn.close()
        
        products = []
        for row in rows:
            products.append(Product(
                id=row[0],
                name=row[1],
                category=row[2],
                description=row[3],
                price=row[4],
                stock=row[5],
                next_availability=row[6],
                features=json.loads(row[7]),
                specifications=json.loads(row[8])
            ))
        
        return products
    
    def update_stock(self, product_id: str, new_stock: int):
        """Update product stock."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE products SET stock = ? WHERE id = ?",
            (new_stock, product_id)
        )
        
        conn.commit()
        conn.close()
    
    def create_order(self, order: Order) -> str:
        """Create a new order."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert order
        cursor.execute("""
            INSERT INTO orders 
            (id, customer_name, customer_email, status, total_amount, discount_applied, created_at, updated_at, agent_logs)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order.id,
            order.customer_name,
            order.customer_email,
            order.status.value,
            order.total_amount,
            order.discount_applied,
            order.created_at.isoformat(),
            order.updated_at.isoformat(),
            json.dumps([log.dict() if hasattr(log, 'dict') else log for log in order.agent_logs])
        ))
        
        # Insert order items
        for item in order.items:
            cursor.execute("""
                INSERT INTO order_items 
                (order_id, product_id, quantity, unit_price, total_price, availability_status, next_availability)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                order.id,
                item.product_id,
                item.quantity,
                item.unit_price,
                item.total_price,
                item.availability_status,
                item.next_availability
            ))
        
        conn.commit()
        conn.close()
        return order.id
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get an order by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order_row = cursor.fetchone()
        
        if not order_row:
            conn.close()
            return None
        
        cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
        item_rows = cursor.fetchall()
        
        conn.close()
        
        items = []
        for item_row in item_rows:
            items.append(OrderItem(
                product_id=item_row[2],
                quantity=item_row[3],
                unit_price=item_row[4],
                total_price=item_row[5],
                availability_status=item_row[6],
                next_availability=item_row[7]
            ))
        
        return Order(
            id=order_row[0],
            customer_name=order_row[1],
            customer_email=order_row[2],
            status=OrderStatus(order_row[3]),
            total_amount=order_row[4],
            discount_applied=order_row[5],
            created_at=datetime.fromisoformat(order_row[6]),
            updated_at=datetime.fromisoformat(order_row[7]),
            agent_logs=json.loads(order_row[8]) if order_row[8] else [],
            items=items
        )
    
    def get_orders(self) -> List[Order]:
        """Get all orders."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM orders ORDER BY created_at DESC")
        order_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        orders = []
        for order_id in order_ids:
            order = self.get_order(order_id)
            if order:
                orders.append(order)
        
        return orders
    
    def update_order(self, order: Order):
        """Update an existing order."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE orders SET 
            status = ?, total_amount = ?, discount_applied = ?, updated_at = ?, agent_logs = ?
            WHERE id = ?
        """, (
            order.status.value,
            order.total_amount,
            order.discount_applied,
            order.updated_at.isoformat(),
            json.dumps([log.dict() if hasattr(log, 'dict') else log for log in order.agent_logs]),
            order.id
        ))
        
        conn.commit()
        conn.close()