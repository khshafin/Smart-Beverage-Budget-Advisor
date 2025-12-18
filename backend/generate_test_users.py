#!/usr/bin/env python3
"""
Generate Test Users for Training ML Models

Creates diverse user profiles with realistic purchasing patterns to train:
- MDP (Markov Decision Process) - budget-aware decisions
- CSP (Constraint Satisfaction) - preference constraints
- Bayesian Inference - preference learning
"""

import sqlite3
import random
import hashlib
from datetime import datetime, timedelta

# Test User Profiles
USER_PROFILES = [
    {
        'username': 'budget_conscious_user',
        'email': 'budget@test.com',
        'weekly_budget': 15.0,
        'pattern': 'frugal',  # Always buys cheapest options
        'mood_preference': ['Tired', 'Focused'],
        'category_preference': ['Coffee', 'Espresso'],
        'consistency': 0.85  # High consistency - buys same drinks
    },
    {
        'username': 'splurge_user',
        'email': 'splurge@test.com',
        'weekly_budget': 75.0,
        'pattern': 'premium',  # Prefers expensive options
        'mood_preference': ['Happy', 'Stressed'],
        'category_preference': ['Frappuccino', 'Latte'],
        'consistency': 0.3  # Low consistency - explores variety
    },
    {
        'username': 'balanced_user',
        'email': 'balanced@test.com',
        'weekly_budget': 35.0,
        'pattern': 'balanced',  # Mix of cheap and expensive
        'mood_preference': ['Happy', 'Focused', 'Tired'],
        'category_preference': ['Coffee', 'Latte', 'Tea'],
        'consistency': 0.6  # Medium consistency
    },
    {
        'username': 'coffee_addict',
        'email': 'addict@test.com',
        'weekly_budget': 50.0,
        'pattern': 'frequent',  # Buys frequently
        'mood_preference': ['Tired', 'Focused'],
        'category_preference': ['Coffee', 'Espresso'],
        'consistency': 0.9  # Very high consistency
    },
    {
        'username': 'mood_driven_user',
        'email': 'moody@test.com',
        'weekly_budget': 40.0,
        'pattern': 'mood_based',  # Strong mood-drink correlation
        'mood_preference': ['Happy', 'Stressed', 'Tired', 'Focused'],
        'category_preference': ['Frappuccino', 'Tea', 'Latte', 'Coffee'],
        'consistency': 0.5  # Medium consistency
    },
    {
        'username': 'variety_seeker',
        'email': 'variety@test.com',
        'weekly_budget': 45.0,
        'pattern': 'explorer',  # Tries everything
        'mood_preference': ['Happy', 'Focused'],
        'category_preference': ['Coffee', 'Latte', 'Frappuccino', 'Tea', 'Espresso'],
        'consistency': 0.2  # Very low consistency - max variety
    },
    {
        'username': 'weekend_warrior',
        'email': 'weekend@test.com',
        'weekly_budget': 30.0,
        'pattern': 'periodic',  # Buys only on weekends
        'mood_preference': ['Happy', 'Stressed'],
        'category_preference': ['Frappuccino', 'Latte'],
        'consistency': 0.7
    },
    {
        'username': 'budget_optimizer',
        'email': 'optimizer@test.com',
        'weekly_budget': 25.0,
        'pattern': 'strategic',  # Maximizes value/price ratio
        'mood_preference': ['Focused', 'Happy'],
        'category_preference': ['Coffee', 'Tea'],
        'consistency': 0.75
    }
]


def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()


def get_beverages(conn):
    """Fetch all beverages from database"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, price, suitable_moods FROM beverages")
    beverages = []
    for row in cursor.fetchall():
        beverages.append({
            'id': row[0],
            'name': row[1],
            'category': row[2],
            'price': row[3],
            'suitable_moods': row[4].split(',') if row[4] else []
        })
    return beverages


def select_beverage_for_profile(beverages, profile, mood):
    """
    Select beverage based on user profile pattern
    """
    pattern = profile['pattern']

    # Filter by mood if mood-driven
    if pattern == 'mood_based':
        mood_filtered = [b for b in beverages if mood in b['suitable_moods']]
        if mood_filtered:
            beverages = mood_filtered

    # Filter by category preference
    category_filtered = [b for b in beverages if b['category'] in profile['category_preference']]
    if category_filtered:
        beverages = category_filtered

    # Apply pattern-specific selection
    if pattern == 'frugal':
        # Always pick cheapest
        return min(beverages, key=lambda x: x['price'])

    elif pattern == 'premium':
        # Prefer expensive (70% expensive, 30% random)
        if random.random() < 0.7:
            expensive = sorted(beverages, key=lambda x: x['price'], reverse=True)
            return expensive[random.randint(0, min(2, len(expensive) - 1))]
        return random.choice(beverages)

    elif pattern == 'balanced':
        # Mix of price ranges
        mid_price = sum(b['price'] for b in beverages) / len(beverages)
        balanced = [b for b in beverages if abs(b['price'] - mid_price) < 2.0]
        return random.choice(balanced if balanced else beverages)

    elif pattern == 'frequent':
        # High consistency - same drinks often
        if random.random() < profile['consistency']:
            # Return favorite (cheapest coffee/espresso)
            favorites = [b for b in beverages if b['category'] in ['Coffee', 'Espresso']]
            if favorites:
                return min(favorites, key=lambda x: x['price'])
        return random.choice(beverages)

    elif pattern == 'explorer':
        # Maximum variety - random selection
        return random.choice(beverages)

    elif pattern == 'strategic':
        # Maximize value (quality/price ratio)
        # Assume price correlates with quality, find sweet spot
        value_drinks = sorted(beverages, key=lambda x: (1 / x['price']) *
                            (1 if x['category'] in profile['category_preference'] else 0.5))
        return value_drinks[0] if value_drinks else random.choice(beverages)

    elif pattern == 'periodic':
        # Random from preferences
        return random.choice(beverages)

    else:
        return random.choice(beverages)


def generate_purchases_for_user(conn, user_id, profile, beverages, weeks=8):
    """
    Generate realistic purchase history for a user over N weeks
    """
    cursor = conn.cursor()
    purchases = []

    moods = profile['mood_preference']
    pattern = profile['pattern']
    weekly_budget = profile['weekly_budget']

    # Track favorite drinks for consistency
    favorite_drinks = {}

    # Generate purchases week by week
    for week in range(weeks):
        week_start = datetime.now() - timedelta(weeks=weeks-week)
        weekly_spent = 0.0
        weekly_purchases = 0

        # Determine purchase frequency based on pattern
        if pattern == 'frequent':
            purchases_per_week = random.randint(8, 12)
        elif pattern == 'periodic':
            purchases_per_week = random.randint(2, 3)  # Weekend only
        elif pattern == 'frugal':
            purchases_per_week = random.randint(3, 5)
        elif pattern == 'premium':
            purchases_per_week = random.randint(4, 7)
        else:
            purchases_per_week = random.randint(4, 8)

        for _ in range(purchases_per_week):
            # Check budget constraint
            if weekly_spent >= weekly_budget * 0.95:  # Stop at 95% budget
                break

            # Select mood
            mood = random.choice(moods)

            # Apply consistency - reuse favorite drinks
            if random.random() < profile['consistency'] and favorite_drinks:
                # Use a favorite
                beverage = random.choice(list(favorite_drinks.values()))
            else:
                # Select new beverage
                beverage = select_beverage_for_profile(beverages, profile, mood)
                # Track as favorite
                if beverage['id'] not in favorite_drinks:
                    favorite_drinks[beverage['id']] = beverage

            # Check if we can afford it
            if weekly_spent + beverage['price'] > weekly_budget:
                # Try to find cheaper alternative
                cheaper = [b for b in beverages if b['price'] <= (weekly_budget - weekly_spent)]
                if not cheaper:
                    break
                beverage = random.choice(cheaper)

            # Generate purchase date
            if pattern == 'periodic':
                # Weekend purchases (Saturday/Sunday)
                day_offset = random.randint(5, 6)
            else:
                day_offset = random.randint(0, 6)

            hour = random.randint(7, 20)  # 7 AM to 8 PM
            minute = random.randint(0, 59)

            purchase_date = week_start + timedelta(days=day_offset, hours=hour, minutes=minute)

            # Insert purchase
            cursor.execute("""
                INSERT INTO purchases (user_id, beverage_id, mood, price, purchase_date)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, beverage['id'], mood, beverage['price'], purchase_date))

            purchases.append({
                'beverage': beverage['name'],
                'price': beverage['price'],
                'mood': mood,
                'date': purchase_date
            })

            weekly_spent += beverage['price']
            weekly_purchases += 1

    conn.commit()
    return purchases


def main():
    """Main function to generate test users and data"""

    print("=" * 80)
    print("GENERATING TEST USERS FOR ML MODEL TRAINING")
    print("=" * 80)

    # Connect to database
    conn = sqlite3.connect('starbucks_budget.db')
    cursor = conn.cursor()

    # Fetch beverages
    beverages = get_beverages(conn)
    print(f"\n✓ Loaded {len(beverages)} beverages from database")

    # Create test users
    print(f"\n{'=' * 80}")
    print(f"CREATING {len(USER_PROFILES)} TEST USERS")
    print(f"{'=' * 80}\n")

    user_stats = []

    for profile in USER_PROFILES:
        username = profile['username']
        email = profile['email']
        weekly_budget = profile['weekly_budget']

        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing = cursor.fetchone()

        if existing:
            user_id = existing[0]
            print(f"⚠️  User '{username}' already exists (ID: {user_id})")
            # Delete existing purchases for clean slate
            cursor.execute("DELETE FROM purchases WHERE user_id = ?", (user_id,))
            conn.commit()
            print(f"   Cleared existing purchase history")
        else:
            # Create new user
            password_hash = hash_password('test123')
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, weekly_budget)
                VALUES (?, ?, ?, ?)
            """, (username, email, password_hash, weekly_budget))
            conn.commit()
            user_id = cursor.lastrowid
            print(f"✓ Created user '{username}' (ID: {user_id})")

        # Generate purchases
        print(f"  Generating purchase history...")
        purchases = generate_purchases_for_user(conn, user_id, profile, beverages, weeks=8)

        total_spent = sum(p['price'] for p in purchases)
        avg_price = total_spent / len(purchases) if purchases else 0
        unique_drinks = len(set(p['beverage'] for p in purchases))

        user_stats.append({
            'username': username,
            'pattern': profile['pattern'],
            'budget': weekly_budget,
            'purchases': len(purchases),
            'total_spent': total_spent,
            'avg_price': avg_price,
            'unique_drinks': unique_drinks,
            'consistency': profile['consistency']
        })

        print(f"  ✓ Generated {len(purchases)} purchases over 8 weeks")
        print(f"  - Total spent: ${total_spent:.2f}")
        print(f"  - Avg price: ${avg_price:.2f}")
        print(f"  - Unique drinks: {unique_drinks}")
        print(f"  - Consistency score: {profile['consistency']:.2f}")
        print()

    # Print summary
    print(f"\n{'=' * 80}")
    print("TRAINING DATA SUMMARY")
    print(f"{'=' * 80}\n")

    print(f"{'User':<25} {'Pattern':<12} {'Purchases':<10} {'Avg $':<8} {'Unique':<8}")
    print("-" * 80)

    for stat in user_stats:
        print(f"{stat['username']:<25} {stat['pattern']:<12} {stat['purchases']:<10} "
              f"${stat['avg_price']:<7.2f} {stat['unique_drinks']:<8}")

    print("-" * 80)
    total_purchases = sum(s['purchases'] for s in user_stats)
    print(f"{'TOTAL':<25} {'':<12} {total_purchases:<10}")

    print(f"\n{'=' * 80}")
    print("DATABASE STATISTICS")
    print(f"{'=' * 80}\n")

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM purchases")
    total_db_purchases = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM beverages")
    total_beverages = cursor.fetchone()[0]

    print(f"Total Users: {total_users}")
    print(f"Total Purchases: {total_db_purchases}")
    print(f"Total Beverages: {total_beverages}")

    # Calculate some ML-relevant statistics
    print(f"\n{'=' * 80}")
    print("ML MODEL TRAINING READINESS")
    print(f"{'=' * 80}\n")

    print("✓ MDP (Markov Decision Process):")
    print("  - Budget states: 4 (HIGH, MEDIUM, LOW, CRITICAL)")
    print(f"  - Training samples: {total_db_purchases} state-action pairs")
    print(f"  - Users with diverse budgets: {len(set(s['budget'] for s in user_stats))}")

    print("\n✓ CSP (Constraint Satisfaction Problem):")
    print(f"  - Mood constraints: 4 types")
    print(f"  - Category constraints: {len(set(b['category'] for b in beverages))} categories")
    print(f"  - Budget constraints: {len(USER_PROFILES)} different budget levels")

    print("\n✓ Bayesian Inference:")
    print(f"  - User profiles: {len(USER_PROFILES)} with varying consistency")
    print(f"  - Purchase patterns: {total_db_purchases} observations")
    print(f"  - Temporal data: 8 weeks of history per user")

    avg_consistency = sum(s['consistency'] for s in user_stats) / len(user_stats)
    print(f"  - Average user consistency: {avg_consistency:.2f}")

    print(f"\n{'=' * 80}")
    print("✅ TEST DATA GENERATION COMPLETE!")
    print(f"{'=' * 80}\n")

    conn.close()


if __name__ == '__main__':
    main()
