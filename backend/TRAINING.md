# Model Training

Train the recommendation engine with purchase history.

## How It Works

- **Bayesian**: Learns from purchase history
- **MDP**: Optimizes for budget
- **CSP**: Filters by mood and budget

More purchases = better recommendations.

## Quick Start

```bash
python train_model.py auto
```

## Commands

**Auto (creates 5 test users)**
```bash
python train_model.py auto
```

Users: `alice_budget`, `bob_coffee`, `charlie_sweet`, `diana_balanced`, `eve_tea`  
Password: `password123`

**Train existing user**
```bash
python train_model.py train <user_id> <profile>
```

**Interactive menu**
```bash
python train_model.py
```

**Clear history**
```bash
python train_model.py clear [user_id]
```

## Profile Types

**budget_conscious**  
Cheap coffee ($2-$4), moods: Tired/Focused, 25 purchases

**caffeine_lover**  
Coffee/espresso ($4-$6), moods: Tired/Focused, 30 purchases

**sweet_tooth**  
Frappuccinos ($6+), moods: Happy/Stressed, 20 purchases

**balanced**  
Mixed drinks ($4-$6), all moods, 28 purchases

**tea_enthusiast**  
Tea drinks ($5-$6), moods: Stressed/Focused/Happy, 22 purchases

## Testing

**API**
```bash
curl "http://127.0.0.1:5000/api/recommendations/2?mood=Tired&budget=6"
```

**Frontend**
1. Login (e.g., alice_budget / password123)
2. Pick mood and budget
3. Get recommendations

**View History**
```bash
curl "http://127.0.0.1:5000/api/purchase/history/2"
```

### Before Training (No History)
The model uses only:
- CSP filtering (mood + budget)
- MDP scoring (budget state)

**Example**: All lattes get equal scores

### After Training (With History)
The model adds Bayesian inference:
- Learns user preferences
- Prioritizes frequently purchased drinks
- Adapts to user patterns

**Example**: If user often buys Vanilla Latte, it gets higher score

## Training Algorithm

### Bayesian Scoring
```
P(like | drink) = (count + 1) / (total + num_drinks)
```

With Laplace smoothing:
- Prevents zero probabilities
- New drinks get small initial probability
- Frequently purchased drinks get higher scores

### Example Calculation

User has purchased:
- Vanilla Latte: 10 times
- Cappuccino: 5 times
- Americano: 3 times
- New drink: 0 times

**Scores:**
- Vanilla Latte: (10+1) / (18+4) = 0.50
- Cappuccino: (5+1) / (18+4) = 0.27
- Americano: (3+1) / (18+4) = 0.18
- New drink: (0+1) / (18+4) = 0.05

## Database Schema

Purchase history is stored in the `purchases` table:

```sql
CREATE TABLE purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    beverage_id INTEGER NOT NULL,
    mood TEXT NOT NULL,
    price REAL NOT NULL,
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (beverage_id) REFERENCES beverages(id)
)
```

## Custom Training Scripts

You can create custom training scenarios by importing the functions:

```python
from train_model import create_sample_user, train_user_profile, add_purchase_history

# Create a user
user_id = create_sample_user('john_doe', 'john@example.com', 40.0)

# Train with specific profile
train_user_profile(user_id, 'caffeine_lover')

# Or manually add purchases
add_purchase_history(
    user_id=user_id,
    beverage_id=5,  # Grande Americano
    mood='Tired',
    price=4.25,
    days_ago=7
)
```

## Monitoring Training Results

### Check Database Stats

```bash
# Connect to database
sqlite3 starbucks_budget.db

# Count users
SELECT COUNT(*) FROM users;

# Count purchases
SELECT COUNT(*) FROM purchases;

# Top drinks by popularity
SELECT b.name, COUNT(*) as count 
FROM purchases p
JOIN beverages b ON p.beverage_id = b.id
GROUP BY b.name
ORDER BY count DESC
LIMIT 10;

# User purchase patterns
SELECT u.username, COUNT(p.id) as purchases, SUM(p.price) as total_spent
FROM users u
LEFT JOIN purchases p ON u.id = p.user_id
GROUP BY u.id;
```

### View User Preferences

```python
from recommendation_engine import recommend

# Get recommendations for trained user
results = recommend(user_id=2, mood='Tired', budget=6.0)

for drink in results:
    print(f"{drink['name']}: ${drink['price']} (score: {drink['score']})")
```

## Best Practices

1. **Start with Sample Users**: Run `python train_model.py auto` first to see how the system works

2. **Realistic Patterns**: When training custom users, create realistic purchase patterns (not all the same drink)

3. **Time Distribution**: Purchases are distributed over 60 days to simulate real usage

4. **Test Different Profiles**: Compare recommendations between different user profiles

5. **Gradual Training**: In production, users build their history naturally over time

6. **Privacy**: Purchase history is per-user and never shared between users

## Troubleshooting

### No Recommendations Returned

**Problem**: API returns empty array

**Solutions**:
1. Check if Flask server is running: `python app.py`
2. Verify user has purchase history: `python train_model.py` (option 3)
3. Check budget and mood parameters are valid

### Training Script Fails

**Problem**: Import or database errors

**Solutions**:
1. Ensure you're in the backend directory
2. Activate virtual environment: `source ../.venv/bin/activate`
3. Install requirements: `pip install -r requirements.txt`
4. Check database file exists: `ls -l starbucks_budget.db`

### User Already Exists

**Problem**: Cannot create sample user

**Solution**: Sample users persist between runs. Either:
- Train existing user: `python train_model.py train <user_id>`
- Clear and recreate: Delete `starbucks_budget.db` and run `python app.py` to reinitialize

## Advanced Usage

### Batch Training Multiple Users

```python
from train_model import get_users, train_user_profile

# Train all users
users = get_users()
for user in users:
    train_user_profile(user['id'], 'balanced')
```

### Custom Profile Creation

```python
# Add to train_model.py profiles dictionary
profiles['custom_profile'] = {
    'preferred_drinks': ['Your', 'Favorite', 'Drinks'],
    'mood_preference': ['Happy', 'Focused'],
    'purchase_count': 25
}
```

### Export Training Data

```bash
# Export purchases to CSV
sqlite3 -header -csv starbucks_budget.db "SELECT * FROM purchases;" > purchases.csv

# Export user stats
sqlite3 -header -csv starbucks_budget.db "
SELECT u.username, COUNT(p.id) as purchases, 
       AVG(p.price) as avg_price, SUM(p.price) as total_spent
FROM users u
LEFT JOIN purchases p ON u.id = p.user_id
GROUP BY u.id;" > user_stats.csv
```

## Next Steps

1. ✅ Train the model with sample users
2. Test recommendations with different moods and budgets
3. Login to frontend and try the trained user accounts
4. Add your own users and build their purchase history naturally
5. Monitor how recommendations improve over time

For more information, see:
- [API Documentation](../README.md)
- [Setup Guide](../SETUP.md)
- [Design Document](../DESIGN.md)
