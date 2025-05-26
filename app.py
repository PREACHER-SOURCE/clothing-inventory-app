from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'  # Change this to a random secret key for sessions

# Hardcoded user credentials for demo
USER_CREDENTIALS = {
    'username': 'admin',
    'password': 'pass123'
}

# Inventory: key is item_code; values are dicts with item info + 'sold' status
inventory = {
    'A001': {'name': 'Red T-Shirt', 'description': 'Comfortable cotton t-shirt', 'price': 15.99, 'sizes': ['S', 'M', 'L'], 'sold': False},
    'B002': {'name': 'Blue Jeans', 'description': 'Stylish denim jeans', 'price': 39.99, 'sizes': ['M', 'L', 'XL'], 'sold': False}
}

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        if uname == USER_CREDENTIALS['username'] and pwd == USER_CREDENTIALS['password']:
            session['user'] = uname
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    message = ''
    search_code = ''
    filtered_inventory = inventory

    # Handle search
    if request.method == 'POST':
        if 'search' in request.form:
            search_code = request.form['search_code'].strip().upper()
            if search_code:
                filtered_inventory = {code: item for code, item in inventory.items() if code == search_code}
                if not filtered_inventory:
                    message = f"No item found with code '{search_code}'"
        # Handle add new item
        elif 'add' in request.form:
            code = request.form['item_code'].strip().upper()
            name = request.form['item_name'].strip()
            desc = request.form['item_desc'].strip()
            price = request.form['item_price'].strip()
            sizes = request.form['item_sizes'].strip()

            if code and name and price:
                if code in inventory:
                    message = f"Item code '{code}' already exists!"
                else:
                    try:
                        price_val = float(price)
                        sizes_list = [s.strip().upper() for s in sizes.split(',')] if sizes else []
                        inventory[code] = {
                            'name': name,
                            'description': desc,
                            'price': price_val,
                            'sizes': sizes_list,
                            'sold': False
                        }
                        message = f"Added item '{name}' with code '{code}'."
                    except ValueError:
                        message = "Price must be a valid number."
            else:
                message = "Item code, name and price are required."

    return render_template('index.html', inventory=filtered_inventory, message=message, search_code=search_code)

@app.route('/delete/<code>')
@login_required
def delete_item(code):
    code = code.upper()
    if code in inventory:
        del inventory[code]
    return redirect(url_for('index'))

@app.route('/mark_sold/<code>')
@login_required
def mark_sold(code):
    code = code.upper()
    if code in inventory:
        inventory[code]['sold'] = True
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
