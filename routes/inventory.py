from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from models.inventory import Product, Category, Supplier, Customer, Transaction, StockAlert
from forms.inventory import (ProductForm, CategoryForm, SupplierForm, CustomerForm, 
                           TransactionForm, BulkUploadForm, ProductSearchForm, DateRangeForm)
from utils.decorators import role_required
from utils.reports import generate_pdf_report, generate_excel_report
from utils.email import send_stock_alert
import os
import pandas as pd
from datetime import datetime

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/dashboard')
@login_required
def dashboard():
    """Panel de control principal"""
    # Obtener estadísticas resumidas
    total_products = Product.query.count()
    low_stock_count = Product.query.filter(Product.current_stock <= Product.minimum_stock).count()
    recent_transactions = Transaction.query.order_by(Transaction.transaction_date.desc()).limit(5).all()
    
    # Obtener datos para gráficos
    categories = Category.query.all()
    category_data = {
        'labels': [cat.name for cat in categories],
        'data': [len(cat.products) for cat in categories]
    }
    
    return render_template('inventory/dashboard.html', 
                         total_products=total_products,
                         low_stock_count=low_stock_count,
                         recent_transactions=recent_transactions,
                         category_data=category_data)

@inventory_bp.route('/products')
@login_required
def products():
    """Lista de productos"""
    search_form = ProductSearchForm()
    search_form.category.choices = [(0, 'Todas')] + [(c.id, c.name) for c in Category.query.all()]
    search_form.supplier.choices = [(0, 'Todos')] + [(s.id, s.name) for s in Supplier.query.all()]
    
    query = Product.query
    if request.args.get('query'):
        search = f"%{request.args.get('query')}%"
        query = query.filter(Product.name.like(search) | Product.sku.like(search))
    if request.args.get('category') and request.args.get('category') != '0':
        query = query.filter_by(category_id=request.args.get('category'))
    if request.args.get('supplier') and request.args.get('supplier') != '0':
        query = query.filter_by(supplier_id=request.args.get('supplier'))
    
    products = query.order_by(Product.name).all()
    return render_template('inventory/products.html', products=products, form=search_form)

@inventory_bp.route('/product/add', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'manager'])
def add_product():
    """Agregar nuevo producto"""
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    form.supplier_id.choices = [(0, 'Ninguno')] + [(s.id, s.name) for s in Supplier.query.all()]
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            sku=form.sku.data,
            category_id=form.category_id.data,
            supplier_id=form.supplier_id.data if form.supplier_id.data != 0 else None,
            unit_price=form.unit_price.data,
            current_stock=form.current_stock.data,
            minimum_stock=form.minimum_stock.data
        )
        
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join('static', 'product_images', filename))
            product.image_url = filename
            
        db.session.add(product)
        db.session.commit()
        
        if product.check_stock_level():
            alert = StockAlert(product_id=product.id)
            db.session.add(alert)
            db.session.commit()
            send_stock_alert(product)
            
        flash('¡Producto agregado exitosamente!', 'success')
        return redirect(url_for('inventory.products'))
        
    return render_template('inventory/product_form.html', form=form, title='Agregar Producto')

@inventory_bp.route('/product/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'manager'])
def edit_product(id):
    """Editar producto existente"""
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    form.supplier_id.choices = [(0, 'Ninguno')] + [(s.id, s.name) for s in Supplier.query.all()]
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.sku = form.sku.data
        product.category_id = form.category_id.data
        product.supplier_id = form.supplier_id.data if form.supplier_id.data != 0 else None
        product.unit_price = form.unit_price.data
        product.current_stock = form.current_stock.data
        product.minimum_stock = form.minimum_stock.data
        
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join('static', 'product_images', filename))
            product.image_url = filename
            
        db.session.commit()
        
        if product.check_stock_level():
            alert = StockAlert(product_id=product.id)
            db.session.add(alert)
            db.session.commit()
            send_stock_alert(product)
            
        flash('¡Producto actualizado exitosamente!', 'success')
        return redirect(url_for('inventory.products'))
        
    return render_template('inventory/product_form.html', form=form, title='Editar Producto')

@inventory_bp.route('/product/delete/<int:id>', methods=['POST'])
@login_required
@role_required(['admin'])
def delete_product(id):
    """Eliminar producto"""
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('¡Producto eliminado exitosamente!', 'success')
    return redirect(url_for('inventory.products'))

# Rutas para Categorías
@inventory_bp.route('/categories')
@login_required
def categories():
    """Lista de categorías"""
    categories = Category.query.all()
    return render_template('inventory/categories.html', categories=categories)

@inventory_bp.route('/category/add', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'manager'])
def add_category():
    """Agregar nueva categoría"""
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, description=form.description.data)
        db.session.add(category)
        db.session.commit()
        flash('¡Categoría agregada exitosamente!', 'success')
        return redirect(url_for('inventory.categories'))
    return render_template('inventory/category_form.html', form=form, title='Agregar Categoría')

# Rutas para Proveedores
@inventory_bp.route('/suppliers')
@login_required
def suppliers():
    """Lista de proveedores"""
    suppliers = Supplier.query.all()
    return render_template('inventory/suppliers.html', suppliers=suppliers)

@inventory_bp.route('/supplier/add', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'manager'])
def add_supplier():
    """Agregar nuevo proveedor"""
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier(
            name=form.name.data,
            contact_person=form.contact_person.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data
        )
        db.session.add(supplier)
        db.session.commit()
        flash('¡Proveedor agregado exitosamente!', 'success')
        return redirect(url_for('inventory.suppliers'))
    return render_template('inventory/supplier_form.html', form=form, title='Agregar Proveedor')

# Rutas para Transacciones
@inventory_bp.route('/transactions')
@login_required
def transactions():
    """Lista de transacciones"""
    transactions = Transaction.query.order_by(Transaction.transaction_date.desc()).all()
    return render_template('inventory/transactions.html', transactions=transactions)

@inventory_bp.route('/transaction/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    """Agregar nueva transacción"""
    form = TransactionForm()
    form.product_id.choices = [(p.id, p.name) for p in Product.query.all()]
    form.customer_id.choices = [(0, 'Ninguno')] + [(c.id, c.name) for c in Customer.query.all()]
    
    if form.validate_on_submit():
        product = Product.query.get(form.product_id.data)
        quantity = form.quantity.data
        
        if form.type.data == 'salida' and quantity > product.current_stock:
            flash('¡Stock insuficiente!', 'danger')
            return render_template('inventory/transaction_form.html', form=form, title='Agregar Transacción')
        
        transaction = Transaction(
            type=form.type.data,
            product_id=form.product_id.data,
            customer_id=form.customer_id.data if form.customer_id.data != 0 else None,
            quantity=quantity,
            unit_price=form.unit_price.data,
            total_price=form.unit_price.data * quantity,
            notes=form.notes.data,
            created_by=current_user.id
        )
        
        if form.type.data == 'entrada':
            product.current_stock += quantity
        else:
            product.current_stock -= quantity
            
        db.session.add(transaction)
        db.session.commit()
        
        if product.check_stock_level():
            alert = StockAlert(product_id=product.id)
            db.session.add(alert)
            db.session.commit()
            send_stock_alert(product)
            
        flash('¡Transacción agregada exitosamente!', 'success')
        return redirect(url_for('inventory.transactions'))
        
    return render_template('inventory/transaction_form.html', form=form, title='Agregar Transacción')

# Rutas para Reportes
@inventory_bp.route('/reports', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'manager'])
def reports():
    """Generación de reportes"""
    form = DateRangeForm()
    if form.validate_on_submit():
        start_date = datetime.strptime(form.start_date.data, '%Y-%m-%d')
        end_date = datetime.strptime(form.end_date.data, '%Y-%m-%d')
        
        if form.format.data == 'pdf':
            pdf_file = generate_pdf_report(form.report_type.data, start_date, end_date)
            return send_file(pdf_file, as_attachment=True)
        else:
            excel_file = generate_excel_report(form.report_type.data, start_date, end_date)
            return send_file(excel_file, as_attachment=True)
            
    return render_template('inventory/reports.html', form=form)

# Endpoints API para actualizaciones dinámicas
@inventory_bp.route('/api/product/<int:id>')
@login_required
def get_product(id):
    """Obtener información de producto vía API"""
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'current_stock': product.current_stock,
        'unit_price': product.unit_price
    })

@inventory_bp.route('/api/low-stock')
@login_required
def get_low_stock():
    """Obtener productos con stock bajo vía API"""
    products = Product.query.filter(Product.current_stock <= Product.minimum_stock).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'current_stock': p.current_stock,
        'minimum_stock': p.minimum_stock
    } for p in products])
