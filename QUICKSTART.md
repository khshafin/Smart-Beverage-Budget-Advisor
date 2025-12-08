# Quick Start

## Setup

**1. Start Backend**
```bash
cd backend
pip install -r requirements.txt
python app.py
```
Runs at http://127.0.0.1:5000

**2. Open Frontend**
Open `frontend/index.html` in your browser

Or use a server:
```bash
cd frontend
python -m http.server 8000
```

**3. Train Model (Optional)**
```bash
cd backend
python train_model.py auto
```

Creates test accounts:
- Usernames: `alice_budget`, `bob_coffee`, `charlie_sweet`, `diana_balanced`, `eve_tea`
- Password: `password123`

## Test It Out

1. Sign in or create an account
2. Pick a mood (e.g., Tired)
3. Set your budget (e.g., $5)
4. Get recommendations
5. Try ordering a drink

## Testing Trained Users

```bash
# Budget user
curl "http://127.0.0.1:5000/api/recommendations/2?mood=Tired&budget=6"

# Coffee lover
curl "http://127.0.0.1:5000/api/recommendations/3?mood=Tired&budget=6"

# Sweet drinks
curl "http://127.0.0.1:5000/api/recommendations/4?mood=Happy&budget=8"
```

Same mood and budget give different results based on each user's history.

## Troubleshooting

**"Failed to fetch"**  
Make sure backend is running

**No recommendations**  
- Select a mood (should highlight green)
- Enter a budget amount
- Try a higher budget

**Not personalized**  
New users need purchase history. Either:
- Use a trained account (alice_budget, bob_coffee, etc.)
- Make some purchases first
- Run `python train_model.py train <user_id>`

## File References

- `frontend/index.html` - Primary page structure
- `frontend/styles.css` - Starbucks-style design implementation
- `frontend/app.js` - Interactive functionality
- `backend/app.py` - API interface

## Key Demonstration Features

1. **Mood Selection Interface** - Visual feedback system with selection highlighting
2. **Progress Bar Visualization** - Real-time budget tracking with updates
3. **Intelligent Splurge Feature** - Dynamic budget recommendation algorithm
4. **AI Recommendation Display** - Ranked results with match scoring
5. **Order Processing System** - Transaction simulation and budget updating


## Documentation Resources

- SETUP.md for comprehensive technical details
- frontend/README.md for frontend-specific information
- Browser developer console (F12) for error diagnosis
- Backend operational verification required

---

