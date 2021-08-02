from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from datetime import datetime
from flask_migrate import Migrate
import sys
import logging
import json

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///order.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Cafeorders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    food_items = db.Column(db.String(1000), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    bill_amount = db.Column(db.Float, default=0.0)
    time_of_order = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
       return '<Order %r>' % self.id

    def __init__(self, name, food_items, quantity, bill_amount, time_of_order=None):
        self.name = name
        self.food_items = food_items
        self.quantity = quantity
        self.bill_amount = bill_amount
        if time_of_order is None:
            self.time_of_order = datetime.utcnow()
        else:
            self.time_of_order = time_of_order

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'food_items': self.food_items,
            'quantity': self.quantity,
            'bill_amount': self.bill_amount,
            'time_of_order':self.time_of_order
        }


@app.route('/')
@app.route('/home')
def homepage():
    return render_template('menu.html')

    
@app.route('/order', methods=['GET', 'POST'])
def displayorders():
    if request.method == 'GET':
        try:
            orders = Cafeorders.query.order_by(Cafeorders.time_of_order).all()
            json_list=[i.to_json() for i in orders]
            return jsonify(json_list)
        except Exception as e:
            print(e)
    else:
         return render_template('menu.html')

@app.route('/orderform')
def orderform():
    return render_template('orderform.html')


@app.route('/addorder', methods=['POST', 'GET'])
def submitorder():
    data = request.get_data(as_text=True)
    order_request = json.loads(data)
    app.logger.info("Order Request::", type(order_request))
    if request.method == 'POST':
        name = order_request['name']
        food_item = order_request['food_items']
        quantity = order_request['quantity']
        if food_item != None:
            if food_item == 'Cappuccino':
                bill_amount = float(quantity) * 120
            elif food_item == 'Cold Coffee':
                bill_amount = float(quantity) * 100
            elif food_item == 'Hot Coffee':
                bill_amount = float(quantity) * 80
            else:
                bill_amount = 0
        else:
            food_item = ""
        order_details = Cafeorders(name, food_item, quantity, bill_amount, None)
        try:
            db.session.add(order_details)
            db.session.commit()
            return jsonify("Order placed successfully!!!")
        except Exception as e:
            print(e)
    else:
        return jsonify("Order Failed !! Please order again!!")


@app.route('/updateorder', methods=['POST', 'GET'])
def updateorder():
    data = request.get_data(as_text=True)
    update_request = json.loads(data)
    update_order = Cafeorders.query.get_or_404(update_request['id'])
    app.logger.info("Update Request::", type(update_request), "UpdateOrder Object ::", update_order.name)
    if request.method == 'POST':
        update_order.name = update_request['name']
        app.logger.info("Updated NAme : ",update_order.name)
        update_order.food_item = update_request['food_items']
        update_order.quantity = update_request['quantity']
        if update_order.food_item != None:
            if update_order.food_item == 'Cappuccino':
                update_order.bill_amount = float(update_order.quantity) * 120
            elif update_order.food_item == 'Cold Coffee':
                update_order.bill_amount = float(update_order.quantity) * 100
            elif update_order.food_item == 'Hot Coffee':
                update_order.bill_amount = float(update_order.quantity) * 80
            else:
                update_order.bill_amount = 0
        else:
            update_order.food_item = ""

        try:
            db.session.commit()
            return jsonify("Order Updated Successfully!!!")
        except Exception as e:
            print(e)
    else:
        return jsonify("Update Order Failed !! Please order again!!")

        
@app.route('/deleteorder/<int:id>', methods=['DELETE'])
def deleteorder(id):
    delete_order = Cafeorders.query.get_or_404(id)
    try:
        db.session.delete(delete_order)
        db.session.commit()
        return jsonify("Order Deleted Successfully!!!")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    app.run(debug=True)
