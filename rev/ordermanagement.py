import database as db
from flask import session
from datetime import datetime

def create_order_from_cart():
    print('checki')
    order = {}
    order.setdefault("username",session["user"]["username"])
    order.setdefault("orderdate",datetime.datetime.now(tz=datetime.timezone.utc))
    order_details = []
    cart = session["cart"]
    for key, value in cart.items():
        order_details.append({"code":key,
                            "name":value["name"],
                            "qty":value["qty"],
                            "subtotal":value["subtotal"]})
    order.setdefault("details",order_details)
    db.create_order(order)
