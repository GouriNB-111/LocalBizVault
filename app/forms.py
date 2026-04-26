from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange

# ==================== AUTH FORMS ====================
class RegistrationForm(FlaskForm):
    role = SelectField('I am a', 
                      choices=[('customer', 'Customer'), ('shopkeeper', 'Shopkeeper')], 
                      validators=[DataRequired()])
    
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    name = StringField('Full Name', validators=[DataRequired()])
    shop_name = StringField('Shop Name')   # Only for shopkeeper
    
    address = StringField('Address', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# ==================== PRODUCT FORM ====================
class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    price = FloatField('Price (₹)', validators=[DataRequired(), NumberRange(min=1)])
    description = TextAreaField('Description')
    category = StringField('Category')
    stock = IntegerField('Stock Quantity', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save Product')