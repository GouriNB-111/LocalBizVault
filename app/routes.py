from flask import Blueprint, render_template, redirect, url_for, flash, request, session, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Product, Order
from app.forms import RegistrationForm, LoginForm, ProductForm
from werkzeug.utils import secure_filename
import os
from slugify import slugify
from datetime import datetime
import cloudinary
import cloudinary.uploader

# ── Cloudinary config ──
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

bp = Blueprint('main', __name__)

# ------------------- HOME -------------------
@bp.route('/')
def home():
    live_shops = User.query.filter_by(role='shopkeeper', status='Deployed').limit(6).all()
    return render_template('index.html', live_shops=live_shops)

# ------------------- PUBLIC STOREFRONT -------------------
@bp.route('/<slug>')
def storefront(slug):
    shop = User.query.filter_by(slug=slug, role='shopkeeper').first_or_404()
    products = Product.query.filter_by(shop_id=shop.id).all()
    return render_template('storefront/storefront.html', shop=shop, products=products)

# ------------------- AUTH ROUTES -------------------
@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        slug = slugify(form.shop_name.data) if form.role.data == 'shopkeeper' else None
        user = User(
            username=form.username.data.lower(),
            name=form.name.data,
            phone=form.phone.data,
            address=form.address.data,
            role=form.role.data,
            shop_name=form.shop_name.data if form.role.data == 'shopkeeper' else None,
            slug=slug,
            status='Draft' if form.role.data == 'shopkeeper' else None
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('main.login'))
    return render_template('admin/register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            if user.role == 'shopkeeper':
                return redirect(url_for('main.dashboard'))
            else:
                return redirect(url_for('main.home'))
        flash('Invalid credentials', 'danger')
    return render_template('admin/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

# ------------------- SHOPKEEPER DASHBOARD -------------------
@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'shopkeeper':
        flash('Access denied. Only shopkeepers can view dashboard.', 'danger')
        return redirect(url_for('main.home'))
    products = Product.query.filter_by(shop_id=current_user.id).all()
    orders = Order.query.filter_by(shop_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('admin/dashboard.html', products=products, orders=orders)

# ------------------- ADD PRODUCT -------------------
@bp.route('/add-product', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.role != 'shopkeeper':
        flash('Only shopkeepers can add products.', 'warning')
        return redirect(url_for('main.home'))

    form = ProductForm()
    if form.validate_on_submit():
        filename = None
        image = request.files.get('image')
        if image and image.filename:
            try:
                result = cloudinary.uploader.upload(
                    image,
                    folder='localbizvault',
                    transformation=[
                        {'width': 600, 'height': 600, 'crop': 'fill'}
                    ]
                )
                filename = result['secure_url']  # permanent https:// URL
            except Exception as e:
                flash('Image upload failed, product saved without image.', 'warning')
                filename = None

        product = Product(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
            category=form.category.data,
            stock=form.stock.data,
            image=filename,
            shop_id=current_user.id
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('admin/add_product.html', form=form)

# ------------------- CUSTOMER CART & CHECKOUT -------------------
@bp.route('/add-to-cart/<int:product_id>/<slug>')
@login_required
def add_to_cart(product_id, slug):
    if current_user.role != 'customer':
        flash('Only customers can add to cart', 'warning')
        return redirect(url_for('main.storefront', slug=slug))

    if 'cart' not in session:
        session['cart'] = {}
    pid_str = str(product_id)
    session['cart'][pid_str] = session['cart'].get(pid_str, 0) + 1
    session.modified = True
    flash('Added to cart!', 'success')
    return redirect(url_for('main.storefront', slug=slug))

@bp.route('/cart')
@login_required
def cart():
    if current_user.role != 'customer':
        return redirect(url_for('main.home'))

    cart = session.get('cart', {})
    cart_items = []
    total = 0

    for pid_str, quantity in cart.items():
        product = Product.query.get(int(pid_str))
        if product:
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })

    return render_template('storefront/cart.html', cart_items=cart_items, total=total)

@bp.route('/update-cart/<int:product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    if current_user.role != 'customer':
        return redirect(url_for('main.home'))

    action = request.form.get('action')
    pid_str = str(product_id)

    if 'cart' not in session:
        session['cart'] = {}

    if pid_str in session['cart']:
        if action == 'increase':
            session['cart'][pid_str] += 1
        elif action == 'decrease':
            session['cart'][pid_str] -= 1
            if session['cart'][pid_str] <= 0:
                del session['cart'][pid_str]
        session.modified = True

    return redirect(url_for('main.cart'))

@bp.route('/remove-from-cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    if current_user.role != 'customer':
        return redirect(url_for('main.home'))

    pid_str = str(product_id)
    if 'cart' in session and pid_str in session['cart']:
        del session['cart'][pid_str]
        session.modified = True
        flash('Item removed from cart.', 'info')

    return redirect(url_for('main.cart'))

@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if current_user.role != 'customer':
        return redirect(url_for('main.home'))

    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('main.home'))

    shop_items = {}
    for pid_str, quantity in cart.items():
        product = Product.query.get(int(pid_str))
        if product:
            shop_id = product.shop_id
            if shop_id not in shop_items:
                shop_items[shop_id] = []
            shop_items[shop_id].append({
                'product': product,
                'quantity': quantity,
                'subtotal': product.price * quantity
            })

    if request.method == 'POST':
        payment_method = request.form.get('payment_method', 'cod')
        utr_number = request.form.get('utr_number', '').strip()

        for shop_id, items in shop_items.items():
            total_amount = sum(i['subtotal'] for i in items)
            pay_status = 'Pending UPI Verification' if payment_method == 'upi' else 'Unpaid'

            order = Order(
                customer_id=current_user.id,
                customer_name=request.form.get('customer_name'),
                customer_phone=request.form.get('customer_phone'),
                shop_id=shop_id,
                total_amount=total_amount,
                status='Pending',
                payment_method=payment_method,
                utr_number=utr_number if payment_method == 'upi' else None,
                payment_status=pay_status,
                created_at=datetime.utcnow()
            )
            db.session.add(order)

        db.session.commit()
        session.pop('cart', None)

        if payment_method == 'upi':
            flash('🎉 Order placed! Your payment is being verified by the shopkeeper.', 'success')
        else:
            flash('🎉 Order placed successfully!', 'success')

        return redirect(url_for('main.home'))

    all_items = [item for items in shop_items.values() for item in items]
    grand_total = sum(i['subtotal'] for i in all_items)

    first_shop_id = list(shop_items.keys())[0]
    shop_owner = db.session.get(User, first_shop_id)
    upi_id = (shop_owner.upi_id if shop_owner and shop_owner.upi_id else None) or 'yourupi@bank'
    upi_qr_image = shop_owner.upi_qr_image if shop_owner else None
    
    return render_template('storefront/checkout.html',
                           cart_items=all_items,
                           total=grand_total,
                           upi_id=upi_id,
                           upi_qr_image=upi_qr_image)

# ------------------- SHOPKEEPER ORDER MANAGEMENT -------------------
@bp.route('/orders')
@login_required
def orders():
    if current_user.role != 'shopkeeper':
        return redirect(url_for('main.home'))
    orders = Order.query.filter_by(shop_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@bp.route('/update-order/<int:order_id>', methods=['POST'])
@login_required
def update_order(order_id):
    if current_user.role != 'shopkeeper':
        return redirect(url_for('main.home'))
    order = Order.query.get_or_404(order_id)
    if order.shop_id == current_user.id:
        order.status = request.form.get('status')
        db.session.commit()
        flash('Order status updated', 'success')
    return redirect(url_for('main.orders'))

@bp.route('/store-status')
@login_required
def store_status():
    if current_user.role != 'shopkeeper':
        flash('Only shopkeepers can access store status', 'warning')
        return redirect(url_for('main.home'))
    return render_template('admin/store_status.html', shop=current_user)

# ------------------- DEPLOY STORE -------------------
@bp.route('/deploy-store', methods=['POST'])
@login_required
def deploy_store():
    if current_user.role != 'shopkeeper':
        flash('Only shopkeepers can deploy stores.', 'warning')
        return redirect(url_for('main.home'))

    if current_user.status == 'Draft':
        current_user.status = 'Deployed'
        current_user.deployed_at = datetime.utcnow()
        db.session.commit()
        flash('🎉 Your store has been successfully deployed on the platform!', 'success')

    return redirect(url_for('main.dashboard'))

@bp.route('/delete-product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if current_user.role != 'shopkeeper':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))

    product = Product.query.get_or_404(product_id)

    if product.shop_id == current_user.id:
        if product.image:
            try:
                # Delete from Cloudinary if it's a Cloudinary URL
                if 'cloudinary' in str(product.image):
                    public_id = 'localbizvault/' + product.image.split('/')[-1].split('.')[0]
                    cloudinary.uploader.destroy(public_id)
            except Exception:
                pass
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    else:
        flash('You can only delete your own products.', 'danger')

    return redirect(url_for('main.dashboard'))

# ==================== SERVE UPLOADED IMAGES ====================
@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    upload_path = os.path.join(os.getcwd(), 'uploads')
    return send_from_directory(upload_path, filename)

@bp.route('/update-payment/<int:order_id>', methods=['POST'])
@login_required
def update_payment(order_id):
    if current_user.role != 'shopkeeper':
        return redirect(url_for('main.home'))
    order = Order.query.get_or_404(order_id)
    if order.shop_id == current_user.id:
        order.payment_status = 'Paid' if order.payment_status != 'Paid' else 'Unpaid'
        db.session.commit()
        flash('Payment status updated.', 'success')
    return redirect(url_for('main.orders'))