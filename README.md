# Smart Budget Beverage Advisor

Member A: Jing Xie  
Member B: Farhan Ansari  
Member C: Kh Shafin Farhan

## Quick Start

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Server runs at http://localhost:5000

### Training the Model (Recommended)

For better recommendations, train with sample data:

```bash
cd backend
python train_model.py auto
```

This creates 5 users with different drink preferences.

**Test Accounts:**
- Usernames: `alice_budget`, `bob_coffee`, `charlie_sweet`, `diana_balanced`, `eve_tea`
- Password: `password123`

## API Endpoints

**Authentication**
- POST /api/register – Create account
- POST /api/login – Sign in
- GET /api/user/profile/:id – Get user info

**Purchases**
- POST /api/purchase – Record purchase
- GET /api/purchase/history/:id – Purchase history
- GET /api/purchase/weekly-spending/:id – Weekly spending

**Beverages**
- GET /api/beverages – List drinks (optional: `mood`, `max_price`)
- GET /api/beverages/:id – Drink details

**Recommendations**
- GET /api/recommendations/:user_id?mood=<mood>&budget=<amount>
  - Uses Bayesian learning from purchase history
  - MDP for budget optimization
  - CSP for mood/budget constraints  

## Model Training

Recommendations improve as users make more purchases. Train with sample data:

```bash
cd backend
python train_model.py auto
```

**Sample Users:**
- **alice_budget** – Budget-conscious
- **bob_coffee** – Coffee lover
- **charlie_sweet** – Sweet drinks
- **diana_balanced** – Varied tastes
- **eve_tea** – Tea drinker

Each has 20-30 purchases over 60 days.

**Test:**
```bash
curl "http://127.0.0.1:5000/api/recommendations/2?mood=Tired&budget=6"
```
- All endpoints return JSON
- Authentication uses JWT tokens in Authorization header
- CORS is enabled for all origins

- `POST /api/register` & `POST /api/login` - User authentication
- `GET /api/user/profile/:user_id` - Display user info
- `GET /api/beverages` - Show drink catalog
- `POST /api/purchase` - Record when user buys a drink
- `GET /api/purchase/weekly-spending/:user_id` - Show budget progress bar