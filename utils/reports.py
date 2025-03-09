from fpdf import FPDF
import pandas as pd
from datetime import datetime
from models.inventory import Product, Transaction, Category, Supplier
from models.user import User
import os

class PDF(FPDF):
    """Clase personalizada de PDF para reportes"""
    def header(self):
        # Logo
        try:
            self.image('static/images/logo.png', 10, 8, 33)
        except:
            pass
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Mover a la derecha
        self.cell(80)
        # Título
        self.cell(30, 10, 'Sistema de Gestión de Inventario', 0, 0, 'C')
        # Salto de línea
        self.ln(20)

    def footer(self):
        # Posición a 1.5 cm del final
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Número de página
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')

def generate_pdf_report(report_type, start_date, end_date):
    """
    Genera reporte PDF según el tipo especificado.
    
    Args:
        report_type: Tipo de reporte ('inventory', 'transactions', 'low_stock')
        start_date: Fecha inicial
        end_date: Fecha final
    """
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    
    if report_type == 'inventory':
        generate_inventory_status_pdf(pdf)
    elif report_type == 'transactions':
        generate_transaction_history_pdf(pdf, start_date, end_date)
    elif report_type == 'low_stock':
        generate_low_stock_pdf(pdf)
    
    # Guardar el PDF
    filename = f'reports/{report_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    os.makedirs('reports', exist_ok=True)
    pdf.output(filename)
    return filename

def generate_excel_report(report_type, start_date, end_date):
    """
    Genera reporte Excel según el tipo especificado.
    
    Args:
        report_type: Tipo de reporte ('inventory', 'transactions', 'low_stock')
        start_date: Fecha inicial
        end_date: Fecha final
    """
    filename = f'reports/{report_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    os.makedirs('reports', exist_ok=True)
    
    if report_type == 'inventory':
        generate_inventory_status_excel(filename)
    elif report_type == 'transactions':
        generate_transaction_history_excel(filename, start_date, end_date)
    elif report_type == 'low_stock':
        generate_low_stock_excel(filename)
        
    return filename

def generate_inventory_status_pdf(pdf):
    """Genera PDF de estado actual del inventario"""
    pdf.cell(0, 10, 'Estado Actual del Inventario', 0, 1, 'C')
    pdf.ln(10)
    
    # Encabezado de tabla
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(50, 10, 'Producto', 1)
    pdf.cell(30, 10, 'Categoría', 1)
    pdf.cell(30, 10, 'Stock', 1)
    pdf.cell(30, 10, 'Stock Mín', 1)
    pdf.cell(30, 10, 'Precio', 1)
    pdf.ln()
    
    # Datos de tabla
    pdf.set_font('Arial', '', 10)
    products = Product.query.all()
    for product in products:
        pdf.cell(50, 10, product.name[:25], 1)
        pdf.cell(30, 10, product.category.name[:15], 1)
        pdf.cell(30, 10, str(product.current_stock), 1)
        pdf.cell(30, 10, str(product.minimum_stock), 1)
        pdf.cell(30, 10, f"${product.unit_price:.2f}", 1)
        pdf.ln()

def generate_transaction_history_pdf(pdf, start_date, end_date):
    """Genera PDF del historial de transacciones"""
    pdf.cell(0, 10, 'Historial de Transacciones', 0, 1, 'C')
    pdf.cell(0, 10, f'Del {start_date.strftime("%Y-%m-%d")} al {end_date.strftime("%Y-%m-%d")}', 0, 1, 'C')
    pdf.ln(10)
    
    # Encabezado de tabla
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(30, 10, 'Fecha', 1)
    pdf.cell(40, 10, 'Producto', 1)
    pdf.cell(20, 10, 'Tipo', 1)
    pdf.cell(20, 10, 'Cant.', 1)
    pdf.cell(30, 10, 'Precio', 1)
    pdf.cell(40, 10, 'Usuario', 1)
    pdf.ln()
    
    # Datos de tabla
    pdf.set_font('Arial', '', 10)
    transactions = Transaction.query.filter(
        Transaction.transaction_date.between(start_date, end_date)
    ).order_by(Transaction.transaction_date.desc()).all()
    
    for trans in transactions:
        pdf.cell(30, 10, trans.transaction_date.strftime("%Y-%m-%d"), 1)
        pdf.cell(40, 10, trans.product.name[:20], 1)
        pdf.cell(20, 10, 'Entrada' if trans.type == 'entrada' else 'Salida', 1)
        pdf.cell(20, 10, str(trans.quantity), 1)
        pdf.cell(30, 10, f"${trans.total_price:.2f}", 1)
        user = User.query.get(trans.created_by)
        pdf.cell(40, 10, user.username if user else 'N/A', 1)
        pdf.ln()

def generate_low_stock_pdf(pdf):
    """Genera PDF de productos con stock bajo"""
    pdf.cell(0, 10, 'Productos con Stock Bajo', 0, 1, 'C')
    pdf.ln(10)
    
    # Encabezado de tabla
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(60, 10, 'Producto', 1)
    pdf.cell(30, 10, 'Stock Actual', 1)
    pdf.cell(30, 10, 'Stock Mín', 1)
    pdf.cell(40, 10, 'Proveedor', 1)
    pdf.ln()
    
    # Datos de tabla
    pdf.set_font('Arial', '', 10)
    products = Product.query.filter(Product.current_stock <= Product.minimum_stock).all()
    
    for product in products:
        pdf.cell(60, 10, product.name[:30], 1)
        pdf.cell(30, 10, str(product.current_stock), 1)
        pdf.cell(30, 10, str(product.minimum_stock), 1)
        pdf.cell(40, 10, product.supplier.name[:20] if product.supplier else 'N/A', 1)
        pdf.ln()

def generate_inventory_status_excel(filename):
    """Genera Excel de estado actual del inventario"""
    products = Product.query.all()
    data = []
    
    for product in products:
        data.append({
            'Producto': product.name,
            'Categoría': product.category.name,
            'Stock Actual': product.current_stock,
            'Stock Mínimo': product.minimum_stock,
            'Precio Unitario': product.unit_price,
            'Proveedor': product.supplier.name if product.supplier else 'N/A',
            'Última Actualización': product.updated_at.strftime("%Y-%m-%d %H:%M")
        })
    
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False, sheet_name='Estado del Inventario')

def generate_transaction_history_excel(filename, start_date, end_date):
    """Genera Excel del historial de transacciones"""
    transactions = Transaction.query.filter(
        Transaction.transaction_date.between(start_date, end_date)
    ).order_by(Transaction.transaction_date.desc()).all()
    
    data = []
    for trans in transactions:
        user = User.query.get(trans.created_by)
        data.append({
            'Fecha': trans.transaction_date.strftime("%Y-%m-%d %H:%M"),
            'Producto': trans.product.name,
            'Tipo': 'Entrada' if trans.type == 'entrada' else 'Salida',
            'Cantidad': trans.quantity,
            'Precio Unitario': trans.unit_price,
            'Precio Total': trans.total_price,
            'Cliente/Proveedor': trans.customer.name if trans.customer else 'N/A',
            'Creado Por': user.username if user else 'N/A',
            'Notas': trans.notes
        })
    
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False, sheet_name='Historial de Transacciones')

def generate_low_stock_excel(filename):
    """Genera Excel de productos con stock bajo"""
    products = Product.query.filter(Product.current_stock <= Product.minimum_stock).all()
    data = []
    
    for product in products:
        data.append({
            'Producto': product.name,
            'Categoría': product.category.name,
            'Stock Actual': product.current_stock,
            'Stock Mínimo': product.minimum_stock,
            'Precio Unitario': product.unit_price,
            'Proveedor': product.supplier.name if product.supplier else 'N/A',
            'Última Actualización': product.updated_at.strftime("%Y-%m-%d %H:%M")
        })
    
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False, sheet_name='Productos con Stock Bajo')
