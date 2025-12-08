# Backend

Member A: Jing Xie  
Member B: Farhan Ansari

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

Runs at http://localhost:5000

**Train model:**
```bash
python train_model.py auto
```

## API Endpoints

**Authentication**
- POST /api/register
- POST /api/login
- GET /api/user/profile/:id

**Purchases**
- POST /api/purchase
- GET /api/purchase/history/:id
- GET /api/purchase/weekly-spending/:id

**Beverages**
- GET /api/beverages (optional: `mood`, `max_price`)
- GET /api/beverages/:id

**Recommendations**
- GET /api/recommendations/:user_id?mood=X&budget=Y
  - Bayesian learning from history
  - MDP for budget optimization
  - CSP for constraints

## Notes

- All endpoints return JSON
- Auth uses JWT tokens
- CORS enabled
