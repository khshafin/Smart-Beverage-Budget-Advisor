# Setup Guide

## Overview

AI-powered drink recommendations based on mood, budget, and purchase history.

**Team:**
- Member A (Jing Xie): Backend, Database
- Member B (Farhan Ansari): AI Engine
- Member C (Kh Shafin Farhan): Frontend

## Requirements

- Python 3.8+
- Web browser
- Terminal

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Server starts at http://127.0.0.1:5000

Keep this terminal open.

## Frontend Setup

**Option 1: Direct**
Double-click `frontend/index.html`

**Option 2: Server**
```bash
cd frontend
python -m http.server 8000
```
Go to http://localhost:8000

## Testing

**Create Account**
1. Click "Sign In"
2. Click "Sign Up"
3. Fill in details (username, email, password, budget)
4. Sign in

**Try Recommendations**
1. Pick a mood
2. Set a budget
3. Get recommendations
4. Order a drink

**Check Budget**
- Make purchases
- Watch progress bar
- Try "Can I Splurge?"
- View profile

## Project Structure

```
starbucks-budget-advisor/
│
├── backend/
│   ├── app.py                      # Main Flask application
│   │   - User authentication (register/login)
│   │   - Purchase tracking
│   │   - Beverage catalog API
│   │   - Weekly spending calculation
│   │
│   ├── recommendation_engine.py    # AI recommendation system
│   │   - CSP filtering (mood + budget constraints)
│   │   - Bayesian inference (purchase history learning)
│   │   - MDP model (budget state optimization)
│   │   - Scoring algorithm (combines all 3 methods)
│   │
│   ├── requirements.txt            # Python dependencies
│   └── starbucks_budget.db        # SQLite database (auto-created)
│
├── frontend/
│   ├── index.html                  # Main HTML structure
│   │   - Navigation
│   │   - Auth modal
│   │   - Hero section
│   │   - Recommendation interface
│   │   - Menu display
│   │   - Profile page
│   │
│   ├── styles.css                  # Starbucks-inspired styling
│   │   - Green color palette (#00704A)
│   │   - Card-based layout
│   │   - Responsive design
│   │   - Modern animations
│   │
│   ├── app.js                      # Frontend logic
│   │   - API integration
│   │   - State management
│   │   - UI interactions
│   │   - Event handlers
│   │
│   └── README.md                   # Frontend-specific docs
│
└── README.md                       # This file
```

## API Endpoints Reference

### Authentication
- `POST /api/register` - Create new user account
- `POST /api/login` - Authenticate user
- `GET /api/user/profile/:id` - Get user profile

### Beverages
- `GET /api/beverages` - List all beverages
  - Query params: `?mood=Happy&max_price=5.00`
- `GET /api/beverages/:id` - Get specific beverage

### Purchases
- `POST /api/purchase` - Record a purchase
- `GET /api/purchase/history/:id` - Get purchase history
- `GET /api/purchase/weekly-spending/:id` - Get weekly spending stats

### Recommendations
- `GET /api/recommendations/:id?mood=X&budget=Y` - Get AI recommendations

### User Management
- `PUT /api/user/budget/:id` - Update weekly budget

## Features Implemented

### Member A Features ✅
- [x] User registration with password hashing
- [x] JWT-based authentication
- [x] Purchase history tracking
- [x] Database design (Users, Purchases, Beverages)
- [x] Weekly spending calculation
- [x] RESTful API endpoints

### Member B Features ✅
- [x] CSP filter (mood + budget constraints)
- [x] Bayesian learning (user preference analysis)
- [x] MDP model (budget state optimization)
- [x] Recommendation scoring algorithm
- [x] Integration with Flask API

### Member C Features ✅
- [x] Starbucks-inspired UI design
- [x] Mood selector interface
- [x] Budget progress bar with colors
- [x] "Can I Splurge?" button
- [x] Recommendation results display
- [x] Complete user workflow
- [x] Responsive design

## Database Schema

### Users Table
```sql
id INTEGER PRIMARY KEY
username TEXT UNIQUE
email TEXT UNIQUE
password_hash TEXT
weekly_budget REAL (default: 25.0)
created_at TIMESTAMP
```

### Purchases Table
```sql
id INTEGER PRIMARY KEY
user_id INTEGER (FK to users)
beverage_id INTEGER (FK to beverages)
mood TEXT
price REAL
purchase_date TIMESTAMP
```

### Beverages Table
```sql
id INTEGER PRIMARY KEY
name TEXT
category TEXT
price REAL
suitable_moods TEXT (comma-separated)
```

## Sample Beverages

The database includes 20 pre-loaded beverages:

**Budget-Friendly ($2-4):**
- Tall Brewed Coffee - $2.45
- Grande Brewed Coffee - $2.95
- Tall Americano - $3.75
- Tall Hot Chocolate - $3.75

**Mid-Range ($4-6):**
- Grande Americano - $4.25
- Tall Latte - $4.45
- Grande Iced Latte - $5.45
- Grande Vanilla Latte - $5.65

**Premium ($6+):**
- Grande Caramel Frappuccino - $6.25
- Grande White Chocolate Mocha - $6.25
- Grande Pumpkin Spice Latte - $6.45
- Venti Caramel Frappuccino - $6.95

## AI Recommendation Algorithm

The system uses three AI methods combined:

### 1. CSP (Constraint Satisfaction Problem)
- Filters beverages by mood
- Filters by budget (max_price)
- Returns only feasible options

### 2. Bayesian Inference
- Learns user preferences from history
- Uses Laplace smoothing
- Score = (purchase_count + 1) / (total + num_drinks)

### 3. MDP (Markov Decision Process)
- Models budget state (LOW/MEDIUM/HIGH)
- Optimizes for long-term budget health
- Adjusts recommendations based on spending

### Final Score
```
final_score = 0.6 × bayesian_score + 0.4 × mdp_score
```

Top 3 highest scores = recommendations

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'flask'`
**Solution**: Run `pip install -r requirements.txt`

**Problem**: `Address already in use`
**Solution**: Change port in `app.py`: `app.run(port=5001)`

**Problem**: Database locked
**Solution**: Delete `starbucks_budget.db` and restart backend

### Frontend Issues

**Problem**: "Failed to fetch" errors
**Solution**: Make sure backend is running on port 5000

**Problem**: CORS errors
**Solution**: Backend has CORS enabled, but check browser console

**Problem**: Recommendations not showing
**Solution**: 
1. Check if mood is selected (green highlight)
2. Check if budget is entered
3. Check browser console for errors

### General Tips

1. Always start backend BEFORE opening frontend
2. Use browser DevTools (F12) to debug
3. Check Network tab for API call failures
4. Look at Console for JavaScript errors

## Testing Checklist

- [ ] Can register new user
- [ ] Can login successfully
- [ ] Can select mood (visual feedback)
- [ ] Budget progress bar displays correctly
- [ ] "Can I Splurge?" button works
- [ ] Can get recommendations
- [ ] Recommendations display with ranking
- [ ] Can order drinks
- [ ] Budget updates after purchase
- [ ] Can view purchase history
- [ ] Can update weekly budget
- [ ] Menu displays all beverages
- [ ] Menu filters work

## Development Tips

### Backend Development
- Use Postman or curl to test APIs
- Check `starbucks_budget.db` with SQLite browser
- Add print statements for debugging
- Test each endpoint individually

### Frontend Development
- Use browser DevTools for debugging
- Test responsive design with device toolbar
- Use Lighthouse for performance analysis
- Test in multiple browsers

## Known Limitations

1. No image uploads for beverages
2. No real-time updates (need to refresh)
3. Database resets on server restart
4. No email verification
5. No password reset feature
6. No data visualization/charts

## Future Enhancements

- [ ] Add beverage images
- [ ] Implement data visualization
- [ ] Add social features
- [ ] Mobile app version
- [ ] Payment integration
- [ ] Multi-user chat
- [ ] Admin dashboard
- [ ] Analytics and reporting

## Support

For issues or questions:
1. Check this README
2. Review frontend/README.md for UI issues
3. Check browser console for errors
4. Verify backend is running
5. Test API endpoints directly

## License

MIT License - Educational Project

## Presentation Tips

1. **Start Clean**: Delete `starbucks_budget.db` for fresh demo
2. **Demo Flow**: Register → Login → Select Mood → Set Budget → Get Recs → Order
3. **Highlight AI**: Show how recommendations change with mood/budget
4. **Show Learning**: Order drinks and show how recs adapt
5. **Mobile View**: Demonstrate responsive design

## Credits

Built for [Your Course Name] - Fall 2024
Team Project: Smart Budget Beverage Advisor

---

**Ready to start? Run the backend, open the frontend, and enjoy! ☕**