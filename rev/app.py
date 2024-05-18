

from flask import Flask,redirect
from flask import render_template
from flask import request
from flask import session
from bson.json_util import loads, dumps
from flask import make_response
from flask import flash
import database as db
import authentication
import logging
import ordermanagement as om


app = Flask(__name__)

# Set the secret key to some random bytes. 
# Keep this really secret!
app.secret_key = b's@g@d@c0ff33!'

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formsubmission', methods = ['POST'])
def form_submission():
    qty = request.form.getlist("qty")
    return render_template('formsubmission.html',qty=qty)


@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page="Products", product_list=product_list)

@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))

    return render_template('productdetails.html', code=code, product=product)

@app.route('/branches')
def branches():
    branch_list = db.get_branches()
    return render_template('branches.html', page="Branches", branch_list=branch_list)

@app.route('/branchdetails')
def branchdetails():
    code = request.args.get('code', '')
    branch = db.get_branch(int(code))

    return render_template('branchdetails.html', code=code, branch=branch)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        session['error_message'] = 'Invalid username or password. Please try again.'
    else:
        is_successful, user = authentication.login(username, password)
        app.logger.info('%s', is_successful)
        if is_successful:
            session.pop('error_message', None)  # Remove error message on success
            session["user"] = user
            return redirect('/')
        else:
            session['error_message'] = 'Invalid username or password. Please try again.'

    return redirect('/login/error')

@app.route('/login/error', methods=['GET', 'POST'])
def error():
    return render_template('error.html')

@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart",None)
    return redirect('/')


@app.route('/addtocart', methods=['POST'])
def addtocart():
  code = request.form.get('code', '')
  product = db.get_product(int(code))
  quantity = int(request.form.get('quantity', 1))  # Get quantity from form

  item = dict()
  item["qty"] = quantity
  item["name"] = product["name"]
  item["subtotal"] = product["price"] * item["qty"]

  if session.get("cart") is None:
    session["cart"] = {}

  cart = session["cart"]
  cart[code] = item
  session["cart"] = cart
  return redirect('/cart')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/removefromcart', methods=['POST'])
def removefromcart():
  code = request.form.get('code')
  if session.get('cart') is None:
    return redirect('/cart', error="Cart is empty.")  # Handle empty cart scenario
  elif not code:
    flash("Error: Invalid product code.")  # Handle missing code
    return redirect('/cart')  # Redirect to cart with error message
  else:
    cart = session["cart"]
    new_cart = {item_code: item_data for item_code, item_data in cart.items() if item_code != code}
    session["cart"] = new_cart
    flash(f"Successfully removed {cart[code]['name']} from cart.")  # Flash success message
    return redirect('/cart')

@app.route('/checkout', methods=['POST'])
def checkout():
    # clear cart in session memory upon checkout
    print('checkout')
    om.create_order_from_cart()
    session.pop("cart",None)
    return redirect('/ordercomplete')

@app.route('/ordercomplete')
def ordercomplete():
    return render_template('ordercomplete.html')

@app.route('/api/products',methods=['GET'])
def api_get_products():
    resp = make_response( dumps(db.get_products()) )
    resp.mimetype = 'application/json'
    return resp
