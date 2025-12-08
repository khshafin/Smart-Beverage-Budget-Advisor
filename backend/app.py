from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import bcrypt
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
CORS(app)

# Database
def init_db():
    conn = sqlite3.connect('starbucks_budget.db')
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        weekly_budget REAL DEFAULT 25.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Purchases table
    c.execute('''CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        beverage_id INTEGER NOT NULL,
        mood TEXT NOT NULL,
        price REAL NOT NULL,
        purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (beverage_id) REFERENCES beverages(id)
    )''')
    
    # Beverages table
    c.execute('''CREATE TABLE IF NOT EXISTS beverages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        suitable_moods TEXT
    )''')
    
    # Insert sample beverages
    beverages = [
        # $2-$4
        ('Tall Brewed Coffee', 'Coffee', 2.45, 'Tired,Stressed,Focused'),
        ('Grande Brewed Coffee', 'Coffee', 2.95, 'Tired,Stressed,Focused'),
        ('Tall Americano', 'Espresso', 3.75, 'Tired,Focused'),
        ('Tall Hot Chocolate', 'Other', 3.75, 'Happy,Stressed'),
        
        # $4-$5
        ('Grande Americano', 'Espresso', 4.25, 'Tired,Focused'),
        ('Tall Cappuccino', 'Espresso', 4.25, 'Tired,Focused'),
        ('Tall Latte', 'Latte', 4.45, 'Tired,Happy'),
        ('Grande Cappuccino', 'Espresso', 4.75, 'Tired,Focused'),

        # $5-$6
        ('Grande Iced Latte', 'Latte', 5.45, 'Tired,Focused'),
        ('Grande Chai Tea Latte', 'Tea', 5.45, 'Stressed,Happy,Tired'),
        ('Grande Vanilla Latte', 'Latte', 5.65, 'Happy,Tired'),
        ('Venti Iced Latte', 'Latte', 5.95, 'Tired,Happy'),
        ('Grande Caramel Macchiato', 'Latte', 5.95, 'Happy,Tired'),
        ('Grande Green Tea Latte', 'Tea', 5.95, 'Stressed,Focused,Tired'),
        
        # $6+
        ('Grande Caramel Frappuccino', 'Frappuccino', 6.25, 'Happy'),
        ('Grande White Chocolate Mocha', 'Mocha', 6.25, 'Happy,Tired'),
        ('Grande Mocha Frappuccino', 'Frappuccino', 6.45, 'Happy,Stressed'),
        ('Grande Pumpkin Spice Latte', 'Seasonal', 6.45, 'Happy,Stressed'),
        ('Grande Java Chip Frappuccino', 'Frappuccino', 6.75, 'Happy'),
        ('Venti Caramel Frappuccino', 'Frappuccino', 6.95, 'Happy'),
    ]        
    
    c.execute('SELECT COUNT(*) FROM beverages')
    if c.fetchone()[0] == 0:
        c.executemany('INSERT INTO beverages (name, category, price, suitable_moods) VALUES (?, ?, ?, ?)', beverages)
    
    conn.commit()
    conn.close()

# JWT token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401
        try:
            token = token.split()[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except:
            return jsonify({'success': False, 'message': 'Invalid token'}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated

# API
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    weekly_budget = data.get('weekly_budget', 25.0)
    
    if not all([username, email, password]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        conn = sqlite3.connect('starbucks_budget.db')
        conn.execute("PRAGMA foreign_keys = ON")
        c = conn.cursor()
        c.execute('INSERT INTO users (username, email, password_hash, weekly_budget) VALUES (?, ?, ?, ?)',
                  (username, email, password_hash, weekly_budget))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user_id': user_id
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Username or email already exists'}), 409

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        return jsonify({'success': False, 'message': 'Missing credentials'}), 400
    
    conn = sqlite3.connect('starbucks_budget.db')
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    if bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token,
            'user_id': user['id'],
            'username': user['username']
        }), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/user/profile/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    conn = sqlite3.connect('starbucks_budget.db')
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT id, username, email, weekly_budget, created_at FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    return jsonify({
        'user_id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'weekly_budget': user['weekly_budget'],
        'member_since': user['created_at']
    }), 200

@app.route('/api/user/budget/<int:user_id>', methods=['PUT'])
def update_budget(user_id):
    data = request.json
    new_budget = data.get('weekly_budget')
    
    if not new_budget or new_budget <= 0:
        return jsonify({'success': False, 'message': 'Invalid budget amount'}), 400
    
    conn = sqlite3.connect('starbucks_budget.db')
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()
    c.execute('UPDATE users SET weekly_budget = ? WHERE id = ?', (new_budget, user_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Budget updated successfully'}), 200

@app.route('/api/purchase', methods=['POST'])
def record_purchase():
    data = request.json
    user_id = data.get('user_id')
    beverage_id = data.get('beverage_id')
    mood = data.get('mood')
    price = data.get('price')
    
    if not all([user_id, beverage_id, mood, price]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    conn = sqlite3.connect('starbucks_budget.db')
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()
    c.execute('INSERT INTO purchases (user_id, beverage_id, mood, price) VALUES (?, ?, ?, ?)',
              (user_id, beverage_id, mood, price))
    purchase_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'purchase_id': purchase_id,
        'message': 'Purchase recorded successfully'
    }), 201

@app.route('/api/purchase/history/<int:user_id>', methods=['GET'])
def get_purchase_history(user_id):
    limit = request.args.get('limit', 50, type=int)
    days = request.args.get('days', 365, type=int)
    
    conn = sqlite3.connect('starbucks_budget.db')
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    query = '''
        SELECT p.id, p.mood, p.price, p.purchase_date,
               b.name as beverage_name, b.category
        FROM purchases p
        JOIN beverages b ON p.beverage_id = b.id
        WHERE p.user_id = ? AND p.purchase_date >= date('now', '-' || ? || ' days')
        ORDER BY p.purchase_date DESC
        LIMIT ?
    '''
    
    c.execute(query, (user_id, days, limit))
    purchases = c.fetchall()
    conn.close()
    
    history = [{
        'purchase_id': p['id'],
        'beverage_name': p['beverage_name'],
        'category': p['category'],
        'mood': p['mood'],
        'price': p['price'],
        'date': p['purchase_date']
    } for p in purchases]
    
    return jsonify({
        'user_id': user_id,
        'total_purchases': len(history),
        'history': history
    }), 200

@app.route('/api/purchase/weekly-spending/<int:user_id>', methods=['GET'])
def get_weekly_spending(user_id):
    conn = sqlite3.connect('starbucks_budget.db')
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('SELECT weekly_budget FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    if not user:
        conn.close()
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    query = '''
        SELECT COALESCE(SUM(price), 0) as spent
        FROM purchases
        WHERE user_id = ? AND purchase_date >= date('now', 'weekday 0', '-7 days')
    '''
    c.execute(query, (user_id,))
    result = c.fetchone()
    conn.close()
    
    spent = result['spent']
    weekly_budget = user['weekly_budget']
    
    return jsonify({
        'user_id': user_id,
        'weekly_budget': weekly_budget,
        'spent_this_week': round(spent, 2),
        'remaining': round(weekly_budget - spent, 2),
        'week_start': datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday()),
        'week_end': datetime.date.today() + datetime.timedelta(days=(6 - datetime.date.today().weekday()))
    }), 200

@app.route('/api/beverages', methods=['GET'])
def get_beverages():
    mood = request.args.get('mood')
    max_price = request.args.get('max_price', type=float)
    
    conn = sqlite3.connect('starbucks_budget.db')
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    query = 'SELECT * FROM beverages WHERE 1=1'
    params = []
    
    if mood:
        query += ' AND suitable_moods LIKE ?'
        params.append(f'%{mood}%')
    
    if max_price:
        query += ' AND price <= ?'
        params.append(max_price)
    
    c.execute(query, params)
    beverages = c.fetchall()
    conn.close()
    
    result = [{
        'id': b['id'],
        'name': b['name'],
        'category': b['category'],
        'price': b['price'],
        'suitable_moods': b['suitable_moods'].split(',') if b['suitable_moods'] else []
    } for b in beverages]
    
    return jsonify({'beverages': result}), 200

@app.route('/api/beverages/<int:beverage_id>', methods=['GET'])
def get_beverage(beverage_id):
    conn = sqlite3.connect('starbucks_budget.db')
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM beverages WHERE id = ?', (beverage_id,))
    beverage = c.fetchone()
    conn.close()
    
    if not beverage:
        return jsonify({'success': False, 'message': 'Beverage not found'}), 404
    
    return jsonify({
        'id': beverage['id'],
        'name': beverage['name'],
        'category': beverage['category'],
        'price': beverage['price'],
        'suitable_moods': beverage['suitable_moods'].split(',')
    }), 200

from recommendation_engine import recommend

@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    mood = request.args.get("mood")
    budget = request.args.get("budget")

    results = recommend(user_id, mood, budget)
    return jsonify(results)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)



