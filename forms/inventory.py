from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Email
from wtforms.widgets import TextArea

class ProductForm(FlaskForm):
    """Formulario de producto"""
    name = StringField('Nombre del Producto', validators=[DataRequired()])
    description = TextAreaField('Descripción')
    sku = StringField('SKU', validators=[DataRequired()])
    category_id = SelectField('Categoría', coerce=int, validators=[DataRequired()])
    supplier_id = SelectField('Proveedor', coerce=int, validators=[Optional()])
    unit_price = FloatField('Precio Unitario', validators=[
        DataRequired(),
        NumberRange(min=0, message='El precio debe ser mayor o igual a 0')
    ])
    current_stock = IntegerField('Stock Actual', validators=[
        DataRequired(),
        NumberRange(min=0, message='El stock debe ser mayor o igual a 0')
    ])
    minimum_stock = IntegerField('Stock Mínimo', validators=[
        DataRequired(),
        NumberRange(min=0, message='El stock mínimo debe ser mayor o igual a 0')
    ])
    image = FileField('Imagen del Producto', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], '¡Solo se permiten imágenes!')
    ])
    submit = SubmitField('Guardar Producto')

class CategoryForm(FlaskForm):
    """Formulario de categoría"""
    name = StringField('Nombre de Categoría', validators=[DataRequired()])
    description = TextAreaField('Descripción')
    submit = SubmitField('Guardar Categoría')

class SupplierForm(FlaskForm):
    """Formulario de proveedor"""
    name = StringField('Nombre del Proveedor', validators=[DataRequired()])
    contact_person = StringField('Persona de Contacto')
    email = StringField('Correo Electrónico', validators=[Optional(), Email()])
    phone = StringField('Teléfono')
    address = TextAreaField('Dirección')
    submit = SubmitField('Guardar Proveedor')

class CustomerForm(FlaskForm):
    """Formulario de cliente"""
    name = StringField('Nombre del Cliente', validators=[DataRequired()])
    email = StringField('Correo Electrónico', validators=[Optional(), Email()])
    phone = StringField('Teléfono')
    address = TextAreaField('Dirección')
    submit = SubmitField('Guardar Cliente')

class TransactionForm(FlaskForm):
    """Formulario de transacción"""
    type = SelectField('Tipo de Transacción', 
        choices=[('entrada', 'Entrada de Stock'), ('salida', 'Salida de Stock')],
        validators=[DataRequired()])
    product_id = SelectField('Producto', coerce=int, validators=[DataRequired()])
    customer_id = SelectField('Cliente', coerce=int, validators=[Optional()])
    quantity = IntegerField('Cantidad', validators=[
        DataRequired(),
        NumberRange(min=1, message='La cantidad debe ser mayor a 0')
    ])
    unit_price = FloatField('Precio Unitario', validators=[
        DataRequired(),
        NumberRange(min=0, message='El precio debe ser mayor o igual a 0')
    ])
    notes = TextAreaField('Notas')
    submit = SubmitField('Guardar Transacción')

class BulkUploadForm(FlaskForm):
    """Formulario de carga masiva"""
    file = FileField('Archivo Excel', validators=[
        DataRequired(),
        FileAllowed(['xlsx', 'xls'], '¡Solo se permiten archivos Excel!')
    ])
    submit = SubmitField('Subir')

class ProductSearchForm(FlaskForm):
    """Formulario de búsqueda de productos"""
    query = StringField('Buscar')
    category = SelectField('Categoría', coerce=int, choices=[], validators=[Optional()])
    supplier = SelectField('Proveedor', coerce=int, choices=[], validators=[Optional()])
    min_stock = IntegerField('Stock Mínimo', validators=[Optional()])
    max_stock = IntegerField('Stock Máximo', validators=[Optional()])
    submit = SubmitField('Buscar')

class DateRangeForm(FlaskForm):
    """Formulario de rango de fechas para reportes"""
    start_date = StringField('Fecha Inicial', validators=[DataRequired()])
    end_date = StringField('Fecha Final', validators=[DataRequired()])
    report_type = SelectField('Tipo de Reporte', 
        choices=[
            ('inventory', 'Estado de Inventario'),
            ('transactions', 'Historial de Transacciones'),
            ('low_stock', 'Productos con Stock Bajo')
        ],
        validators=[DataRequired()]
    )
    format = SelectField('Formato',
        choices=[
            ('pdf', 'PDF'),
            ('excel', 'Excel')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Generar Reporte')
