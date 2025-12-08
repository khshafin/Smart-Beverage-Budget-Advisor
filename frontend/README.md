# Frontend

**Developer**: Kh Shafin Farhan

## Features

- User registration and login
- Mood selector (Happy, Tired, Stressed, Focused)
- Budget progress bar (color-coded)
- "Can I Splurge?" feature
- Top 3 recommendations
- Beverage menu with filters
- User profile
- Starbucks-inspired design

## Setup

**Backend**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

**Frontend**
Open `frontend/index.html` or run:
```bash
python -m http.server 8000
```

## Files

- `index.html` - UI structure
- `styles.css` - Starbucks design
- `app.js` - Frontend logic

## Feature Details

**Mood Selector**  
Four buttons with visual feedback

**Budget Progress Bar**  
Green (<60%), Orange (60-80%), Red (>80%)

**"Can I Splurge?"**  
Calculates 80% of remaining budget (max $10)

**Recommendations**  
Top 3 drinks with rankings, match scores, one-click ordering

**Orders**  
Records purchases, updates spending, shows confirmations

## Design

**Colors**  
Starbucks green (#00704A), dark green, light green, cream

**Layout**  
Card-based, responsive, mobile-friendly

**UX**  
Transitions, loading spinners, toast notifications, modals

## API

Base: `http://127.0.0.1:5000/api`

- POST /register
- POST /login
- GET /user/profile/:id
- GET /purchase/weekly-spending/:id
- GET /beverages
- GET /recommendations/:id?mood=X&budget=Y
- POST /purchase
- GET /purchase/history/:id
- PUT /user/budget/:id

## Feature Testing Procedures

### Mood Selector Verification:
1. Complete authentication
2. Navigate to recommendation interface
3. Select each mood option
4. Verify visual feedback (green highlighting)

### Budget Progress Verification:
1. Review progress bar display
2. Execute purchase transaction
3. Confirm automatic bar update
4. Verify color transitions based on spending thresholds

### Splurge Feature Verification:
1. Input various spending scenarios
2. Activate "Can I Splurge?" function
3. Verify calculated recommendation
4. Test edge cases (minimal budget, maximum budget)

### Recommendation System Verification:
1. Select mood parameter
2. Define budget constraint
3. Request recommendations
4. Verify three-result display
5. Confirm ranking visualization
6. Test order placement functionality

## Customization Guidelines

### Color Scheme Modification:
Edit root variables in `styles.css`:
```css
:root {
    --primary-green: #00704A;
    --dark-green: #005031;
}
```

### Mood Options Extension:
Add button elements in `index.html`:
```html
<button class="mood-btn" data-mood="Energetic">Energetic</button>
```

### Splurge Algorithm Adjustment:
Modify `handleSplurge()` in `app.js`:
```javascript
const suggestedBudget = Math.min(remaining * 0.8, 10);
```

## Known System Limitations

1. Backend server required for frontend operation (CORS)
2. JWT tokens stored in localStorage
3. Manual refresh required for certain data updates
4. Database resets upon backend server restart

## Presentation Guidelines

### Recommended Demonstration Sequence
1. Backend initialization verification
2. User registration and authentication workflow
3. Mood selection with visual feedback
4. Budget progress bar functionality
5. Intelligent splurge recommendation
6. AI recommendation retrieval and display
7. Order placement and budget update

### Key Discussion Points
- Complete implementation of Member C requirements
- Starbucks brand guideline adherence
- Responsive design implementation
- Successful integration with Member A and Member B systems
- Comprehensive user feedback mechanisms

## Troubleshooting Resources

- Browser console inspection (F12) for error diagnosis
- Backend operational status verification: http://127.0.0.1:5000/api/beverages
- Network tab analysis for failed API requests

## Project Credits

- Member A (Jing Xie): Backend API and Database Architecture
- Member B (Farhan Ansari): AI Recommendation Engine
- Member C (Kh Shafin Farhan): Frontend Interface and User Experience