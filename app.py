from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_secret")

# Setup database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('postgresql://clothing_osd4_user:AuDNFQ6NR7OUSY6RHWCMDk3U8SduDNM9@dpg-d0qefo15pdvs73ahqc90-a/clothing_osd4')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Item(db.Model):
    item_code = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)
    sizes = db.Column(db.String(100))  # store sizes as comma-separated string
    sold = db.Column(db.Boolean, default=False)

# Create tables and add initial data if needed
def create_tables():
    with app.app_context():
        db.create_all()
        # Add default user if not exists
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin', password='pass123')
            db.session.add(user)
            db.session.commit()

create_tables()  # Run once at app startup

# Login decorator
from functools import wraps
def login_required(f):
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
        user = User.query.filter_by(username=uname, password=pwd).first()
        if user:
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
    filtered_inventory = Item.query.all()

    if request.method == 'POST':
        if 'search' in request.form:
            search_code = request.form['search_code'].strip().upper()
            if search_code:
                filtered_inventory = Item.query.filter_by(item_code=search_code).all()
                if not filtered_inventory:
                    message = f"No item found with code '{search_code}'"
        elif 'add' in request.form:
            code = request.form['item_code'].strip().upper()
            name = request.form['item_name'].strip()
            desc = request.form['item_desc'].strip()
            price = request.form['item_price'].strip()
            sizes = request.form['item_sizes'].strip()

            if code and name and price:
                existing_item = Item.query.filter_by(item_code=code).first()
                if existing_item:
                    message = f"Item code '{code}' already exists!"
                else:
                    try:
                        price_val = float(price)
                        sizes_str = ','.join([s.strip().upper() for s in sizes.split(',')]) if sizes else ''
                        new_item = Item(
                            item_code=code,
                            name=name,
                            description=desc,
                            price=price_val,
                            sizes=sizes_str,
                            sold=False
                        )
                        db.session.add(new_item)
                        db.session.commit()
                        message = f"Added item '{name}' with code '{code}'."
                    except ValueError:
                        message = "Price must be a valid number."
            else:
                message = "Item code, name and price are required."
    print(type(filtered_inventory))

    return render_template('index.html', inventory=filtered_inventory, message=message, search_code=search_code)

@app.route('/delete/<code>')
@login_required
def delete_item(code):
    code = code.upper()
    item = Item.query.filter_by(item_code=code).first()
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/mark_sold/<code>')
@login_required
def mark_sold(code):
    code = code.upper()
    item = Item.query.filter_by(item_code=code).first()
    if item:
        item.sold = True
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
