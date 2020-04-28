from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

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


# init Schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


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

# Gets
@app.route('/burger', methods=['GET'])
def get_products():
    all_products = Burger.query.all()
    result = products_schema.dump(all_products)
    return jsonify(result)

@app.route('/burger/<id>', methods=['GET'])
def get_product_id(id):
    product = Burger.query.get(id)
    return product_schema.jsonify(product)

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

# Delete
@app.route('/burger/<id>', methods=['DELETE'])
def delete_product_id(id):
    product = Burger.query.get(id)

    db.session.delete(product)

    db.session.commit()

    return product_schema.jsonify(product)

# Run Server
if __name__ == '__main__':
    app.run(debug=True)