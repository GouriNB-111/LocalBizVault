from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(120))
    role = db.Column(db.String(20), default="customer")   # customer or shopkeeper
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)

    # Shopkeeper specific fields
    shop_name = db.Column(db.String(120))
    slug = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default="Draft")
    deployed_at = db.Column(db.DateTime)
    upi_id       = db.Column(db.String(100), nullable=True)   # e.g. shop@upi
    upi_qr_image = db.Column(db.String(200), nullable=True)   # uploaded QR filename

    # Relationships
    products = db.relationship('Product', backref='shop', lazy=True, cascade="all, delete-orphan")
    
    # Fixed relationships with explicit foreign_keys
    orders_as_shop = db.relationship('Order', 
                                     foreign_keys='Order.shop_id', 
                                     backref='shop', 
                                     lazy=True)

    orders_as_customer = db.relationship('Order', 
                                         foreign_keys='Order.customer_id', 
                                         backref='customer', 
                                         lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(300))
    shop_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    customer_name = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20))
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default="Pending")   # Pending, Out for Delivery, Delivered
    payment_status = db.Column(db.String(20), default="Unpaid")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    shop_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    payment_method = db.Column(db.String(20), default='cod')   # 'cod' or 'upi'
    utr_number     = db.Column(db.String(100), nullable=True)  # UPI transaction ID