from flask import Blueprint, render_template, redirect, request, flash, url_for, session
from flask_login import login_required, current_user
from .models import Basket, Product, db, CheckoutForm, AddProductForm, ProductManager
import os
import re


views = Blueprint('views', __name__)


@views.route('/')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products, user=current_user)


@views.route('/sort_products/<sort_id>')
def sort_products(sort_id):
    products = Product.query.all()  
    #sorts products based on sort_id using lambda function
    if sort_id == 'price_desc':
        products = sorted(products, key=lambda p: p.price)
    if sort_id == 'price_asc':
        products = sorted(products, key=lambda p: p.price, reverse=True)
    elif sort_id == 'name':
        products = sorted(products, key=lambda p: p.name)
    elif sort_id == 'carbon_footprint':
        products = sorted(products, key=lambda p: p.carbon_footprint)
    return render_template('products.html', products=products, user=current_user)


@views.route('/basket')
def basket():
    if current_user.is_authenticated:
        basket = Basket.query.filter_by(user_id=current_user.id).first()
        #appends product ids of each product in basket to product_ids array
        product_ids = [product.id for product in basket.products] if basket else []
    else:
        product_ids = session.get('basket', [])
    #retrieves all products using individual product ids in product_ids array
    products = Product.query.filter(Product.id.in_(product_ids)).all()

    total = round(sum(float(product.price) for product in products), 2)

    return render_template('basket.html', user=current_user, basket=products, total=total)


@views.route('/add_to_basket/<product_id>', methods=['POST'])
def add_to_basket(product_id):
    curr_product = Product.query.get(product_id)
    if current_user.is_authenticated:
        #finds user's basket or creates a new one if it doesn't exist
        basket = Basket.query.filter_by(user_id=current_user.id).first()
        if not basket:
            basket = Basket(user_id=current_user.id)
            db.session.add(basket)
            db.session.commit()
        elif curr_product not in basket.products:
            Basket.add_product_basket(basket, curr_product)
    else:
        #use sessions if user is not authenticated
        if 'basket' not in session:
            session['basket'] = []
        elif product_id not in session['basket']:
            session['basket'].append(product_id)

    return redirect(url_for('views.products'))


@views.route('/remove_from_basket/<product_id>', methods=['POST'])
def remove_from_basket(product_id):
    curr_product = Product.query.get(product_id)
    if current_user.is_authenticated:
        basket = Basket.query.filter_by(user_id=current_user.id).first()
        Basket.remove_product_basket(basket, curr_product)
        db.session.commit()
    else:
        if 'basket' in session:
            #replaces session basket with new basket that does not contain removed product
            session['basket'] = [product for product in session['basket'] if product != product_id]
    
    return redirect(url_for('views.basket'))


@views.route('display_product/<int:product_id>')
def display_product(product_id):
    return render_template('display_product.html', user=current_user, product=Product.query.get(product_id))


@views.route('add_product', methods=['GET', 'POST'])
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        image_filename = form.image.data.filename
        #uses absolute path to save image to img/products folder so that it can be used in create_product method
        image_path = os.path.join("/Users/slatham419/Desktop/University/Web-App/ecommerce_website/website/static/img/products/", image_filename)
        form.image.data.save(image_path)
        ProductManager.create_product(name=form.name.data, price=form.price.data, description=form.description.data, carbon_footprint=form.carbon_footprint.data, image=image_filename)
        return redirect(url_for('views.products'))
    return render_template('add_product.html', form=form, user=current_user)


@views.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    form = CheckoutForm()
    if form.validate_on_submit():
        return render_template("checkout_success.html", user=current_user)
    return render_template("checkout.html", user=current_user, form=form)


@views.route('/search', methods=['POST'])
def search():
    stop_words = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'were', 'will', 'with'
    }
    
    search_terms = request.form.get('search_terms')
    # removes punctuation; removes trailing and leading whitespace; converts to lowercase; splits into invidiual searcg keywords; removes stopwords
    search_keywords = set(word for word in re.sub(r'[^\w\s]', '', search_terms.lower()).strip().split(' ') if word not in stop_words)
    
    valid_products = []
    for product in Product.query.all():
        # removes punctuation; removes trailing and leading whitespace; converts to lowercase; splits into invidiual product keywords
        product_keywords = set(word for word in re.sub(r'[^\w\s]', '', product.name.lower()).strip().split(' '))
        for word in search_keywords:
            if word in product_keywords:
                valid_products.append(product)
                break
    
    return render_template('products.html', user=current_user, products=valid_products)
