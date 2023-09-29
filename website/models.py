from . import db
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, FloatField
from wtforms.validators import InputRequired, Length, EqualTo
from os import path
from flask_wtf.file import FileAllowed, FileField

basket_product_link = db.Table(
    #creates a many-to-many relationship between the Basket and Product models
    #this allows many products to be present in many baskets and vice versa
    'basket_product_link',
    db.Column('basket_id', db.Integer, db.ForeignKey('basket.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
)

class Basket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    products = db.relationship('Product', secondary=basket_product_link, backref='basket')

    @staticmethod
    def add_product_basket(basket, product):
        basket.products.append(product)
        db.session.commit()

    @staticmethod
    def remove_product_basket(basket, product):
        basket.products.remove(product)
        db.session.commit()


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    carbon_footprint = db.Column(db.Float)
    image = db.Column(db.String(100))

    def __repr__(self):
        return f'<Product {self.id}: {self.name}>'

class ProductManager():
    @staticmethod
    def create_product(name, price, description, carbon_footprint, image=None):
        product = Product(name=name, price=price, description=description, image=image, carbon_footprint=carbon_footprint)
        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def add_products_from_database(filename, delimiter):
        with open(filename, 'r') as f:
            products = f.readlines()
            for row in products[1:]:
                properties = row.split(delimiter)
                curr_product = Product.query.filter_by(image=properties[2]).first()
                if curr_product is None:
                    ProductManager.create_product(
                        image = properties[2],
                        name = properties[0],
                        price = float(properties[1]),
                        description = properties[4],
                        carbon_footprint = float(properties[3]),
                    )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(64))
    basket = db.relationship('Basket', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def register(username, password):
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def __repr__(self):
        return '<User {0}>'.format(self.username)

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Submit')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(4, 16, message='Username must be at least 4 characters')])
    password = PasswordField('Password', validators=[InputRequired(), Length(4, 16, message='Password must be at least 7 characters')])
    confirm_password = PasswordField('Confirm password', validators=[InputRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Submit')

class CheckoutForm(FlaskForm):
    card_name = StringField('Card Name', validators=[InputRequired()])
    card_number = StringField('Card Number', validators=[InputRequired(), Length(16, 16)])
    cvv_number = StringField('CVV Number', validators=[InputRequired(), Length(3, 3)])
    submit = SubmitField('Submit')

class AddProductForm(FlaskForm):
    name = StringField('Product Name', validators=[InputRequired()])
    price = FloatField('Price', validators=[InputRequired()])
    description = StringField('Product Description', validators=[InputRequired()])
    carbon_footprint = FloatField('Carbon Footprint', validators=[InputRequired()])
    image = FileField('Upload Image', validators=[InputRequired(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Add Product')

