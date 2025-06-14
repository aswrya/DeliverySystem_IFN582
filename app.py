from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import config
import os

#creates a new Flask application instance
app = Flask(__name__)

#secure sessions and prevent tampering, 
app.secret_key = config.SECRET_KEY

# MySQL database Config
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
app.config['MYSQL_PORT'] = 3307                 #changed due to default port is taken for another proccess

mysql = MySQL(app)

# Decorators define to diffrenciate login Fucnction usage
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Login required", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash("Admin access only", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html',
                           error_code=404,
                           error_name='Page Not Found',
                           error_message='The page does not exist.'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html',
                           error_code=500,
                           error_name='Internal Server Error',
                           error_message='Something went wrong on our end. Please try again later.'), 500

#While app run it will landed here at the login page.
@app.route('/')
def index():
    return redirect(url_for('login'))

#logic for the login validations
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']       #email input given by the user
        password = request.form['password'] #password input given by the user
        cur = mysql.connection.cursor()     #db connection stablist
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[4]
            flash('Login successful', 'success')
            return redirect(url_for('dashboard' if user[4] == 'admin' else 'dashboard')) #if creditential is matched then user will login as the roll admin or user
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

# Admin signup logic
@app.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            flash("Email already exists", "warning")
        elif password != repeat_password:
            flash("Password and repeat password is not matched", "warning")

            return redirect(url_for('admin_signup'))
        
        cur.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)", 
                    (name, email, hashed_pw, 'admin'))
        mysql.connection.commit()
        cur.close()
        flash("Signup successful! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('admin_signup.html')

#user signup logic
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256') # hashing algorithm

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            flash("Email already exists", "warning")
        elif password != repeat_password:
            flash("Password and repeat password is not matched", "warning")

            return redirect(url_for('signup'))
        
        cur.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)", 
                    (name, email, hashed_pw, 'user'))
        mysql.connection.commit()
        cur.close()
        flash("Signup successful! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()

        if user:
            session['reset_email'] = email  # store temporarily in session
            flash('Email found. Please set your new password.', 'info')
            return redirect(url_for('reset_password')) #then this will redirect user to the reset_password
        else:
            flash('Email not found.', 'danger')

    return render_template('forgot_password.html')

# reset password
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_email' not in session:
        flash("Unauthorized access. Please use 'Forgot Password' first.", 'warning')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form['password']
        repeat_password = request.form['repeat_password']

        if new_password != repeat_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('reset_password'))

        hashed_pw = generate_password_hash(new_password, method='pbkdf2:sha256')
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET password=%s WHERE email=%s", (hashed_pw, session['reset_email']))
        mysql.connection.commit()
        cur.close()

        session.pop('reset_email')
        flash('Password reset successful. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=session.get('username'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html', name=session.get('username'))

# Logout logic with destroying all the session.
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for('login'))

# Rendering data for food section
@app.route('/food')
def food():
    user_role = session.get('role')

    if user_role not in ['admin', 'user']:
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT food_items.id, food_items.name, food_items.price, food_items.image_url, shops.name AS shop_name
        FROM food_items
        JOIN shops ON food_items.shop_id = shops.id
    """)
    items = cur.fetchall()
    cur.close()

    return render_template('food.html', items=items)

@app.route('/food/<int:shop_id>', endpoint='shop_food')
def shop_details(shop_id):
    # Fetch shop details
    cur = mysql.connection.cursor()
    cur.execute("SELECT name, description, image_url FROM shops WHERE id = %s", (shop_id,))
    shop = cur.fetchone()

    # Fetch food items for this shop
    cur.execute("SELECT id, name, price, image_url FROM food_items WHERE shop_id = %s", (shop_id,))
    food_items = cur.fetchall()
    cur.close()

    return render_template('shop_details.html', shop=shop, food_items=food_items)

# logic for adding food items by the admin
@app.route('/add_food_item', methods=['GET', 'POST'])
@admin_required
def add_food_item():
    cur = mysql.connection.cursor()

    # Fetch shops to populate dropdown (id and name)
    cur.execute("SELECT id, name FROM shops")
    shops = cur.fetchall()

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        shop_id = request.form.get('shop_id')
        image = request.files.get('image')

        if not (name and price and shop_id and image):
            flash('All fields are required.', 'danger')
            return redirect(url_for('add_food_item'))

        filename = secure_filename(image.filename)
        image_path = os.path.join('static', 'images', filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        image.save(image_path)

        image_url = f'images/{filename}'

        cur.execute("INSERT INTO food_items (name, price, image_url, shop_id) VALUES (%s, %s, %s, %s)",
                    (name, price, image_url, shop_id))
        mysql.connection.commit()
        cur.close()

        flash('Food item added successfully!', 'success')
        return redirect(url_for('add_food_item'))

    return render_template('add_food_item.html', shops=shops)

@app.route('/remove_food_item/<int:item_id>', methods=['POST'])
@admin_required
def remove_food_item(item_id):
    cur = mysql.connection.cursor()

    # Fetch the food item details to get the image URL
    cur.execute("SELECT image_url FROM food_items WHERE id = %s", (item_id,))
    item = cur.fetchone()

    if item:
        # Delete the item from the database
        cur.execute("DELETE FROM food_items WHERE id = %s", (item_id,))
        mysql.connection.commit()

        flash('Food item removed successfully!', 'success')
    else:
        flash('Food item not found.', 'danger')

    cur.close()
    return redirect(url_for('food'))

@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        flash("Please enter a search term.", "warning")
        return redirect(url_for('food'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT food_items.id, food_items.name, food_items.price, food_items.image_url, shops.name 
        FROM food_items
        JOIN shops ON food_items.shop_id = shops.id
        WHERE food_items.name LIKE %s
    """, (f"%{query}%",))
    results = cur.fetchall()
    cur.close()

    return render_template('search_results.html', items=results, query=query)


@app.route('/shop')
def shop():
    user_role = session.get('role')

    if user_role not in ['admin', 'user']:
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for('login'))
    # Fetch all shops from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, description, image_url FROM shops")
    shops = cur.fetchall()
    cur.close()

    return render_template('shop.html', shops=shops)


@app.route('/add_vendor', methods=['GET', 'POST'])
@admin_required
def add_vendor():
    if request.method == 'POST':
        shop_name = request.form.get('shop_name')
        description = request.form.get('description')
        location = request.form.get('location')
        image = request.files.get('shop_image')

        if not (shop_name and description and location and image):
            flash('All fields are required!', 'danger')
            return redirect(url_for('add_vendor'))

        filename = secure_filename(image.filename)
        image_folder = os.path.join('static', 'images')
        os.makedirs(image_folder, exist_ok=True)
        image_path = os.path.join(image_folder, filename)
        image.save(image_path)

        image_url = f'images/{filename}'

        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO shops (name, description, location, image_url) VALUES (%s, %s, %s, %s)",
                (shop_name, description, location, image_url)
            )
            mysql.connection.commit()
            cur.close()
            flash('Vendor added successfully!', 'success')
            return redirect(url_for('shop'))
        except Exception as e:
            flash(f'Error adding vendor: {str(e)}', 'danger')

    return render_template('add_vendor.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# saving data from about page
@app.route('/about', methods=['GET', 'POST'])
def about():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        if name and email and message:
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO contact_messages (name, email, message) VALUES (%s, %s, %s)",
                (name, email, message)
            )
            mysql.connection.commit()
            cursor.close()
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('about'))
        else:
            flash('All fields are required!', 'danger')

    return render_template('about.html')

# rendering the message form about page which is stored in contact_message for admin
@app.route('/admin/messages', endpoint='admin_messages')
@admin_required
def view_contact_messages():
    cur = mysql.connection.cursor()

    # Fetch contact messages from the database
    cur.execute("SELECT id, name, email, message, created_at FROM contact_messages ORDER BY created_at DESC")
    messages = cur.fetchall()

    cur.close()

    return render_template('admin_messages.html', messages=messages)

# rendering the data in cart from cart table
@app.route('/cart')
@login_required
def cart():
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, product_id, name, price, image_url, quantity FROM cart WHERE user_id = %s", (user_id,))
    results = cur.fetchall()
    cur.close()

    # Convert tuples to dictionaries
    cart_items = [
        {
            'id': row[0],
            'product_id': row[1],
            'name': row[2],
            'price': row[3],
            'image_url': row[4],
            'quantity': row[5],
            'subtotal': row[3] * row[5]
        }
        for row in results
    ]

    total = sum(item['subtotal'] for item in cart_items)

    return render_template('cart.html', cart=cart_items, total=total)

#count the number of item in the cart and show by user_id logged-in
@app.context_processor
def cart_count():
    if 'user_id' in session:
        user_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT SUM(quantity) FROM cart WHERE user_id = %s", (user_id,))
        result = cur.fetchone()
        cur.close()

        count = result[0] if result[0] is not None else 0
    else:
        count = 0

    return dict(cart_item_count=count)

#adding food items to the cart
@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    user_id = session['user_id'] #user_id comes from session
    item_id = request.form['item_id']
    item_name = request.form['item_name']
    item_price = float(request.form['item_price'])
    item_image = request.form['item_image']

    cur = mysql.connection.cursor()

    # Check if item already exists in cart
    cur.execute("SELECT id, quantity FROM cart WHERE user_id = %s AND product_id = %s", (user_id, item_id))
    existing_item = cur.fetchone()

    if existing_item:
        # Update quantity
        cart_id = existing_item[0]
        current_qty = existing_item[1]
        cur.execute("UPDATE cart SET quantity = %s WHERE id = %s", (current_qty + 1, cart_id)) #update on quantity if already exist
    else:
        # Insert new item
        cur.execute("""
            INSERT INTO cart (user_id, product_id, name, price, image_url, quantity)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, item_id, item_name, item_price, item_image, 1))

    mysql.connection.commit()
    cur.close()

    flash('Item added to cart', 'success')
    return redirect(url_for('food'))

#removing the items from cart
@app.route('/remove_item/<int:item_id>', methods=['POST'])
@login_required
def remove_item(item_id):
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM cart WHERE user_id = %s AND id = %s", (user_id, item_id)) # item will be removed by checking user_id and item_id
    mysql.connection.commit()
    cur.close()

    flash('Item removed from cart', 'success')
    return redirect(url_for('cart'))

#if user dont want to order and clear all the cart items
@app.route('/clear_cart', methods=['POST'])
@login_required
def clear_cart():
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

    flash('All items removed from cart', 'success')
    return redirect(url_for('cart'))

#order checkout by the user
@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    user_id = session['user_id']
    cur = mysql.connection.cursor()

    # Collect form data safely
    name = request.form.get('name')
    address = request.form.get('address')
    contact = request.form.get('contact')
    delivery_method = request.form.get('delivery_method')

    # Basic validation
    if not name or not address or not contact or not delivery_method:
        flash("All fields are required!", "danger")
        return redirect(url_for('cart'))  # Redirect to cart since form is there

    # Fetch cart items
    cur.execute("SELECT product_id, name, price, quantity FROM cart WHERE user_id = %s", (user_id,))
    cart_items = cur.fetchall()

    if not cart_items:
        flash("Cart is empty!", "warning")
        return redirect(url_for('cart'))

    total = sum(row[2] * row[3] for row in cart_items)

    # Insert into orders
    cur.execute("""
        INSERT INTO orders (user_id, total, name, address, contact, delivery_method)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, total, name, address, contact, delivery_method))
    order_id = cur.lastrowid

    # Insert into order_items
    for item in cart_items:
        cur.execute("""
            INSERT INTO order_items (order_id, product_id, name, price, quantity)
            VALUES (%s, %s, %s, %s, %s)
        """, (order_id, item[0], item[1], item[2], item[3]))

    # after placing the order, cart table will be empety and ready for the new order
    cur.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

    flash("Order placed successfully!", "success")
    return redirect(url_for('cart'))

#if user want to see the history of order placed by them
@app.route('/order_history')
@login_required
def order_history():
    user_id = session.get('user_id')
    cur = mysql.connection.cursor()

    # Get all orders by the user with userID
    cur.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    orders = cur.fetchall()

    # Get order items for each order
    order_details = []
    for order in orders:
        cur.execute("""
            SELECT oi.name, oi.price, oi.quantity
            FROM order_items oi
            WHERE oi.order_id = %s
        """, (order[0],))  # order[0] is order.id
        items = cur.fetchall()
        order_details.append({
            'order': order,
            'items': items
        })

    cur.close()
    return render_template('order_history.html', order_details=order_details)

# if admin want to see sales or all the sale items with user
@app.route('/admin/orders')
@admin_required
def view_all_orders():
    cur = mysql.connection.cursor()

    # Get all orders along with user info
    cur.execute("""
        SELECT o.id, u.name, u.email, o.total, o.created_at
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
    """)
    orders = cur.fetchall()

    # Get order items for each order
    all_order_details = []
    for order in orders:
        order_id = order[0]
        cur.execute("""
            SELECT name, price, quantity
            FROM order_items
            WHERE order_id = %s
        """, (order_id,))
        items = cur.fetchall()
        all_order_details.append({
            'order': order,
            'items': items
        })

    cur.close()
    return render_template('admin_orders.html', all_order_details=all_order_details)


#Flask web application server
if __name__ == '__main__':
    app.run(debug=False)
