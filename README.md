# Smart Beverage Budget Advisor

AI-powered drink recommendations using Bayesian learning, MDP optimization, and CSP constraints.

## Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Open `frontend/index.html` in your browser.

## Usage

1. Create account or sign in
2. Select mood and budget
3. Get personalized recommendations
4. Order drinks

## API

- POST `/api/register` - Create account
- POST `/api/login` - Authenticate
- GET `/api/recommendations/:user_id?mood=X&budget=Y` - Get recommendations
- GET `/api/beverages` - List all drinks
- POST `/api/purchase` - Record purchase