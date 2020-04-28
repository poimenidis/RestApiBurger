from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

#Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init marsh
ma = Marshmallow(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(200))
    password = db.Column(db.String(200))
    admin = db.Column(db.Boolean)

class Burger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    stars = db.Column(db.Integer)

    def __init__(self,name,description,price,stars):
        self.name = name
        self.description = description
        self.price = price
        self.stars = stars

class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'price', 'stars')

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'password', 'public_id', 'admin')


# init Schemas
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)


# Post:

@app.route('/burger', methods=['POST'])
def add_product():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    stars = request.json['stars']

    new_product = Burger(name, description, price, stars)
    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product)


@app.route('/user', methods=['POST'])
def add_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'],method='sha256')
    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user)

# Gets
@app.route('/burger', methods=['GET'])
def get_products():
    all_products = Burger.query.all()
    result = products_schema.dump(all_products)
    return products_schema.jsonify(result)

@app.route('/burger/<burger_id>', methods=['GET'])
def get_product_id(burger_id):
    product = Burger.query.get(burger_id)
    return product_schema.jsonify(product)

@app.route('/user', methods=['GET'])
def get_users():

    result = []
    all_users = User.query.all()

    for user in all_users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        result.append(user_data)

    return users_schema.jsonify(result)

@app.route('/user/<public_id>', methods=['GET'])
def get_user_id(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin
    return user_schema.jsonify(user_data)

# Put
@app.route('/burger/<id>', methods=['PUT'])
def put_product_id(id):
    product = Burger.query.get(id)

    product.name = request.json['name']
    product.description = request.json['description']
    product.price = request.json['price']
    product.stars = request.json['stars']

    db.session.commit()

    return product_schema.jsonify(product)

@app.route('/user/<public_id>', methods=['PUT'])
def put_user_id(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    user.name = request.json['name']

    db.session.commit()

    return user_schema.jsonify(user)

# Delete
@app.route('/burger/<id>', methods=['DELETE'])
def delete_product_id(id):
    product = Burger.query.get(id)

    db.session.delete(product)

    db.session.commit()

    return product_schema.jsonify(product)


@app.route('/user/<public_id>', methods=['DELETE'])
def delete_user_id(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    db.session.delete(user)
    db.session.commit()

    return user_schema.jsonify(user)

@app.route('/user', methods=['DELETE'])
def delete_users():
    all_users = User.query.all()

    for user in all_users:
        db.session.delete(user)

    db.session.commit()

    return jsonify({'message': 'all users have been deleted'})

# Run Server
if __name__ == '__main__':
    app.run(debug=True)