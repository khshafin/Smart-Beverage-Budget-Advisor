#!/usr/bin/env python3
"""
Training Script for Starbucks Budget Advisor
Populates database with sample purchase history to train the recommendation engine.
"""

import sqlite3
import random
from datetime import datetime, timedelta

def get_db_connection():
    """Create a database connection."""
    conn = sqlite3.connect('starbucks_budget.db')
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def get_beverages():
    """Fetch all beverages from the database."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, name, price, suitable_moods FROM beverages')
    beverages = c.fetchall()
    conn.close()
    return beverages

def get_users():
    """Fetch all users from the database."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, username FROM users')
    users = c.fetchall()
    conn.close()
    return users

def create_sample_user(username, email, weekly_budget=50.0):
    """Create a sample user for training."""
    import bcrypt
    password = "password123"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('INSERT INTO users (username, email, password_hash, weekly_budget) VALUES (?, ?, ?, ?)',
                  (username, email, password_hash, weekly_budget))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        print(f"✅ Created user '{username}' (ID: {user_id}) with budget ${weekly_budget}/week")
        return user_id
    except sqlite3.IntegrityError:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        if user:
            print(f"ℹ️  User '{username}' already exists (ID: {user['id']})")
            return user['id']
        raise

def add_purchase_history(user_id, beverage_id, mood, price, days_ago=0):
    """Add a purchase to the history."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Calculate purchase date
    purchase_date = datetime.now() - timedelta(days=days_ago)
    
    c.execute('''INSERT INTO purchases (user_id, beverage_id, mood, price, purchase_date) 
                 VALUES (?, ?, ?, ?, ?)''',
              (user_id, beverage_id, mood, price, purchase_date.strftime('%Y-%m-%d %H:%M:%S')))
    purchase_id = c.lastrowid
    conn.commit()
    conn.close()
    return purchase_id

def train_user_profile(user_id, profile_type="balanced"):
    """
    Train a user profile with specific purchase patterns.
    
    Profile types:
    - budget_conscious: Prefers cheaper drinks
    - caffeine_lover: Loves coffee and espresso
    - sweet_tooth: Prefers frappuccinos and sweet drinks
    - balanced: Mixed preferences
    - tea_enthusiast: Prefers tea-based drinks
    """
    beverages = get_beverages()
    moods = ['Happy', 'Tired', 'Stressed', 'Focused']
    
    # Define preferences for each profile
    profiles = {
        'budget_conscious': {
            'preferred_drinks': ['Tall Brewed Coffee', 'Grande Brewed Coffee', 'Tall Americano', 'Tall Hot Chocolate'],
            'mood_preference': ['Tired', 'Focused'],
            'purchase_count': 50,
            'preference_strength': 0.85  # 85% preferred drinks
        },
        'caffeine_lover': {
            'preferred_drinks': ['Grande Americano', 'Tall Cappuccino', 'Grande Cappuccino', 'Tall Latte', 'Tall Americano'],
            'mood_preference': ['Tired', 'Focused'],
            'purchase_count': 45,
            'preference_strength': 0.80
        },
        'sweet_tooth': {
            'preferred_drinks': ['Grande Caramel Frappuccino', 'Grande Mocha Frappuccino', 'Grande Java Chip Frappuccino', 'Grande White Chocolate Mocha', 'Venti Caramel Frappuccino'],
            'mood_preference': ['Happy', 'Stressed'],
            'purchase_count': 40,
            'preference_strength': 0.85
        },
        'balanced': {
            'preferred_drinks': ['Tall Latte', 'Grande Vanilla Latte', 'Grande Chai Tea Latte', 'Grande Americano', 'Tall Cappuccino'],
            'mood_preference': moods,
            'purchase_count': 48,
            'preference_strength': 0.75
        },
        'tea_enthusiast': {
            'preferred_drinks': ['Grande Chai Tea Latte', 'Grande Green Tea Latte'],
            'mood_preference': ['Stressed', 'Focused', 'Happy'],
            'purchase_count': 45,
            'preference_strength': 0.90  # Very strong tea preference
        }
    }
    
    profile = profiles.get(profile_type, profiles['balanced'])
    preferred_drinks = profile['preferred_drinks']
    mood_preference = profile['mood_preference']
    purchase_count = profile['purchase_count']
    preference_strength = profile.get('preference_strength', 0.70)
    
    print(f"\n📊 Training user {user_id} with '{profile_type}' profile ({purchase_count} purchases, {int(preference_strength*100)}% preference)...")
    
    # Get beverage IDs for preferred drinks
    preferred_bevs = [b for b in beverages if b['name'] in preferred_drinks]
    
    purchases_added = 0
    
    # Add purchases over the last 60 days
    for i in range(purchase_count):
        # Use preference_strength for better user differentiation
        if random.random() < preference_strength and preferred_bevs:
            beverage = random.choice(preferred_bevs)
        else:
            beverage = random.choice(beverages)
        
        # Select mood based on preference
        if random.random() < 0.8:
            mood = random.choice(mood_preference)
        else:
            mood = random.choice(moods)
        
        # Random day in the last 60 days
        days_ago = random.randint(0, 60)
        
        purchase_id = add_purchase_history(
            user_id=user_id,
            beverage_id=beverage['id'],
            mood=mood,
            price=beverage['price'],
            days_ago=days_ago
        )
        purchases_added += 1
    
    print(f"✅ Added {purchases_added} purchase records for user {user_id}")
    
    # Show summary
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT b.name, COUNT(*) as count 
        FROM purchases p
        JOIN beverages b ON p.beverage_id = b.id
        WHERE p.user_id = ?
        GROUP BY b.name
        ORDER BY count DESC
        LIMIT 5
    ''', (user_id,))
    top_drinks = c.fetchall()
    conn.close()
    
    print(f"   Top drinks for user {user_id}:")
    for drink in top_drinks:
        print(f"      - {drink['name']}: {drink['count']} times")

def train_all_sample_users():
    """Create and train multiple sample users with different profiles."""
    print("=" * 70)
    print("🚀 STARBUCKS BUDGET ADVISOR - MODEL TRAINING")
    print("=" * 70)
    
    sample_users = [
        ('alice_budget', 'alice@example.com', 'budget_conscious', 30.0),
        ('bob_coffee', 'bob@example.com', 'caffeine_lover', 50.0),
        ('charlie_sweet', 'charlie@example.com', 'sweet_tooth', 45.0),
        ('diana_balanced', 'diana@example.com', 'balanced', 40.0),
        ('eve_tea', 'eve@example.com', 'tea_enthusiast', 35.0),
    ]
    
    for username, email, profile_type, budget in sample_users:
        user_id = create_sample_user(username, email, budget)
        train_user_profile(user_id, profile_type)
    
    print("\n" + "=" * 70)
    print("✅ MODEL TRAINING COMPLETE!")
    print("=" * 70)
    
    # Summary
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) as count FROM users')
    user_count = c.fetchone()['count']
    c.execute('SELECT COUNT(*) as count FROM purchases')
    purchase_count = c.fetchone()['count']
    conn.close()
    
    print(f"\n📈 Database Summary:")
    print(f"   - Total Users: {user_count}")
    print(f"   - Total Purchases: {purchase_count}")
    print(f"\n💡 Sample User Credentials:")
    print(f"   Username: alice_budget, bob_coffee, charlie_sweet, diana_balanced, eve_tea")
    print(f"   Password: password123 (for all sample users)")
    print(f"\n🔍 Test the recommendations with:")
    print(f"   curl http://127.0.0.1:5000/api/recommendations/<user_id>?mood=Tired&budget=6")

def train_existing_user(user_id, profile_type="balanced"):
    """Train an existing user with purchase history."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    
    if not user:
        print(f"❌ User with ID {user_id} not found!")
        return False
    
    print(f"🎯 Training user '{user['username']}' (ID: {user_id})")
    train_user_profile(user_id, profile_type)
    print(f"✅ Training complete for user {user_id}")
    return True

def clear_purchase_history(user_id=None):
    """Clear purchase history for a user or all users."""
    conn = get_db_connection()
    c = conn.cursor()
    
    if user_id:
        c.execute('DELETE FROM purchases WHERE user_id = ?', (user_id,))
        print(f"🗑️  Cleared purchase history for user {user_id}")
    else:
        c.execute('DELETE FROM purchases')
        print(f"🗑️  Cleared all purchase history")
    
    conn.commit()
    conn.close()

def show_menu():
    """Display interactive menu."""
    print("\n" + "=" * 70)
    print("STARBUCKS BUDGET ADVISOR - MODEL TRAINING")
    print("=" * 70)
    print("\nOptions:")
    print("1. Create and train sample users (recommended)")
    print("2. Train existing user with purchase history")
    print("3. List all users")
    print("4. Clear purchase history")
    print("5. Exit")
    print("-" * 70)

if __name__ == '__main__':
    import sys
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'auto':
            # Automatic training mode
            train_all_sample_users()
        
        elif command == 'train' and len(sys.argv) > 2:
            # Train specific user
            user_id = int(sys.argv[2])
            profile = sys.argv[3] if len(sys.argv) > 3 else 'balanced'
            train_existing_user(user_id, profile)
        
        elif command == 'clear':
            # Clear history
            user_id = int(sys.argv[2]) if len(sys.argv) > 2 else None
            clear_purchase_history(user_id)
        
        else:
            print("Usage:")
            print("  python train_model.py auto                    - Create and train sample users")
            print("  python train_model.py train <user_id> [type]  - Train existing user")
            print("  python train_model.py clear [user_id]         - Clear purchase history")
            print("\nProfile types: budget_conscious, caffeine_lover, sweet_tooth, balanced, tea_enthusiast")
    
    else:
        # Interactive mode
        while True:
            show_menu()
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                train_all_sample_users()
            
            elif choice == '2':
                users = get_users()
                if not users:
                    print("❌ No users found in database!")
                    continue
                
                print("\n📋 Available users:")
                for user in users:
                    print(f"   ID {user['id']}: {user['username']}")
                
                user_id = input("\nEnter user ID: ").strip()
                if not user_id.isdigit():
                    print("❌ Invalid user ID!")
                    continue
                
                print("\n📊 Profile types:")
                print("   1. budget_conscious - Prefers cheaper drinks")
                print("   2. caffeine_lover - Loves coffee and espresso")
                print("   3. sweet_tooth - Prefers frappuccinos")
                print("   4. balanced - Mixed preferences (default)")
                print("   5. tea_enthusiast - Prefers tea-based drinks")
                
                profile_choice = input("\nEnter profile type (1-5) or press Enter for balanced: ").strip()
                profile_map = {
                    '1': 'budget_conscious',
                    '2': 'caffeine_lover',
                    '3': 'sweet_tooth',
                    '4': 'balanced',
                    '5': 'tea_enthusiast'
                }
                profile = profile_map.get(profile_choice, 'balanced')
                
                train_existing_user(int(user_id), profile)
            
            elif choice == '3':
                users = get_users()
                if not users:
                    print("❌ No users found in database!")
                    continue
                
                print("\n📋 All users:")
                for user in users:
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute('SELECT COUNT(*) as count FROM purchases WHERE user_id = ?', (user['id'],))
                    purchase_count = c.fetchone()['count']
                    conn.close()
                    print(f"   ID {user['id']}: {user['username']} ({purchase_count} purchases)")
            
            elif choice == '4':
                confirm = input("Clear history for specific user? (y/N): ").strip().lower()
                if confirm == 'y':
                    users = get_users()
                    print("\n📋 Available users:")
                    for user in users:
                        print(f"   ID {user['id']}: {user['username']}")
                    user_id = input("\nEnter user ID: ").strip()
                    if user_id.isdigit():
                        clear_purchase_history(int(user_id))
                else:
                    confirm_all = input("⚠️  Clear ALL purchase history? (yes/N): ").strip().lower()
                    if confirm_all == 'yes':
                        clear_purchase_history()
            
            elif choice == '5':
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice!")
