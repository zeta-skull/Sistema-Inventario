from app import db
from datetime import datetime

class Category(db.Model):
    """Modelo para categorías de productos"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f'<Categoría {self.name}>'

class Product(db.Model):
    """Modelo para productos"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    sku = db.Column(db.String(50), unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    unit_price = db.Column(db.Float, nullable=False)
    current_stock = db.Column(db.Integer, default=0)
    minimum_stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def check_stock_level(self):
        """Verifica si el stock está en nivel bajo"""
        return self.current_stock <= self.minimum_stock

    def __repr__(self):
        return f'<Producto {self.name}>'

class Supplier(db.Model):
    """Modelo para proveedores"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship('Product', backref='supplier', lazy=True)

    def __repr__(self):
        return f'<Proveedor {self.name}>'

class Customer(db.Model):
    """Modelo para clientes"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transactions = db.relationship('Transaction', backref='customer', lazy=True)

    def __repr__(self):
        return f'<Cliente {self.name}>'

class Transaction(db.Model):
    """Modelo para transacciones de inventario"""
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # 'entrada' o 'salida'
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Transacción {self.id} - {self.type}>'

class StockAlert(db.Model):
    """Modelo para alertas de stock bajo"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    alert_date = db.Column(db.DateTime, default=datetime.utcnow)
    notified = db.Column(db.Boolean, default=False)
    resolved = db.Column(db.Boolean, default=False)
    product = db.relationship('Product', backref='alerts', lazy=True)

    def __repr__(self):
        return f'<Alerta de Stock {self.id} - Producto {self.product.name}>'
