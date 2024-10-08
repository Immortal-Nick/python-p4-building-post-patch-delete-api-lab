#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(  bakeries,   200  )

@app.route('/bakeries/<int:id>', methods=['PATCH'])
def bakery_by_id(id):

    bakery = Bakery.query.filter_by(id=id).first()

    new_bakery = request.form.get('name')
    bakery.name = new_bakery
    db.session.commit()

    bakery_serialized = bakery.to_dict()
    return make_response ( jsonify(bakery_serialized), 200)

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    return make_response( baked_goods_by_price_serialized, 200  )
   

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()
    return make_response( most_expensive_serialized,   200  )

@app.route('/baked_goods', methods=['POST'])
def baked_goods():
    try:
        # Get data from the form
        name = request.form.get("name")
        price = request.form.get("price")
        bakery_id = request.form.get("bakery_id")
        
        # Validate that required fields are provided
        if not name or not price or not bakery_id:
            return make_response(jsonify({"error": "Missing required fields"}), 400)

        # Ensure price is a float and bakery_id is an int
        try:
            price = float(price)
            bakery_id = int(bakery_id)
        except ValueError:
            return make_response(jsonify({"error": "Invalid data type for price or bakery_id"}), 400)

        # Create a new baked good
        new_baked_good = BakedGood(
            name=name,
            price=price,
            bakery_id=bakery_id
        )

        # Add and commit to the database
        db.session.add(new_baked_good)
        db.session.commit()

        # Serialize and return the created baked good
        baked_good_dict = new_baked_good.to_dict()

        return make_response(jsonify(baked_good_dict), 201)

    except Exception as e:
        # Roll back the session in case of error
        db.session.rollback()
        return make_response(jsonify({"error": str(e)}), 500)


@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.get(id)
    if not baked_good:
        return jsonify({"error": "Baked good not found"}), 404
    
    db.session.delete(baked_good)
    db.session.commit()
    
    return jsonify({"message": "Baked good deleted successfully"}), 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)