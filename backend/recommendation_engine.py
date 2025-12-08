# recommendation_engine.py

import math
import requests
import sqlite3

BACKEND_URL = "http://127.0.0.1:5001"
   # Your Flask server

# -------------------------------------------------------------
# 1. CSP FILTERING (Mood + Budget)
# -------------------------------------------------------------
def csp_filter(mood, budget):
    """
    Uses beverage API to filter based on:
    - mood
    - budget (max_price)
    """
    try:
        url = f"{BACKEND_URL}/api/beverages?mood={mood}&max_price={budget}"
        response = requests.get(url)
        data = response.json()
        return data.get("beverages", [])
    except Exception as e:
        print("ERROR in CSP filter:", e)
        return []

# -------------------------------------------------------------
# 2. BAYESIAN INFERENCE (User Preferences)
# -------------------------------------------------------------
def bayesian_score(drink_name, history_counts):
    """
    Simple Bayesian model:
        P(like | drink) = (count + 1) / (total + num_drinks)
    Laplace smoothing ensures no zero probabilities.
    """
    total = sum(history_counts.values()) + len(history_counts)
    count = history_counts.get(drink_name, 0) + 1
    return count / (total or 1)  # avoid division by zero

# -------------------------------------------------------------
# 3. MDP MODEL (Budget State → Next Drink)
# -------------------------------------------------------------
def mdp_score(drink_price, budget_state):
    if budget_state == "LOW":
        return 1 / (drink_price + 1)
    elif budget_state == "MEDIUM":
        return 1 / math.sqrt(drink_price + 1)
    else:  # HIGH budget
        return 1.0

def compute_budget_state(weekly_spending):
    """
    Simple classification:
    LOW:    spending > 80% of weekly budget
    MEDIUM: spending 40%–80%
    HIGH:   spending < 40%
    """
    budget_limit = 50  # You can adjust
    percent = weekly_spending / budget_limit

    if percent > 0.8:
        return "LOW"
    elif percent > 0.4:
        return "MEDIUM"
    else:
        return "HIGH"

# -------------------------------------------------------------
# 4. MAIN RECOMMENDATION PIPELINE
# -------------------------------------------------------------
def recommend(user_id, mood, budget):
    # ---------------------------------------------------------
    # A) GET PURCHASE HISTORY
    # ---------------------------------------------------------
    try:
        hist_url = f"{BACKEND_URL}/api/purchase/history/{user_id}"
        history_data = requests.get(hist_url).json()
        print("HISTORY JSON:", history_data)
    except Exception as e:
        print("ERROR fetching history:", e)
        history_data = {}

    # Extract list safely
    history_list = history_data.get("history", []) if isinstance(history_data, dict) else []
    print("History list extracted:", history_list)

    history_counts = {}
    for item in history_list:
        name = item.get("beverage_name", "")
        if name:
            history_counts[name] = history_counts.get(name, 0) + 1
    print("History counts:", history_counts)

    # ---------------------------------------------------------
    # B) GET WEEKLY SPENDING
    # ---------------------------------------------------------
    try:
        spend_url = f"{BACKEND_URL}/api/purchase/weekly-spending/{user_id}"
        weekly_data = requests.get(spend_url).json()
        if isinstance(weekly_data, dict):
            weekly_spending = weekly_data.get("spent_this_week", 0)
        else:
            weekly_spending = 0
        print("Weekly spending:", weekly_spending)
    except Exception as e:
        print("ERROR fetching weekly spending:", e)
        weekly_spending = 0

    budget_state = compute_budget_state(weekly_spending)
    print("Budget state:", budget_state)

    # ---------------------------------------------------------
    # C) CSP FILTERING (Mood + Budget)
    # ---------------------------------------------------------
    drinks = csp_filter(mood, budget)
    print("Drinks after parsing CSP result:", drinks)

    # ------------------ FALLBACK ----------------------------
    if not drinks:
        print("No drinks from CSP filter, using fallback")
        conn = sqlite3.connect('starbucks_budget.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        query = "SELECT * FROM beverages WHERE 1=1"
        params = []
        if budget:
            query += " AND price <= ?"
            params.append(float(budget))
        c.execute(query, params)
        rows = c.fetchall()
        drinks = [{"name": r["name"], "price": r["price"]} for r in rows[:3]]
        print("Fallback drinks:", drinks)
        conn.close()

    # ---------------------------------------------------------
    # D) SCORE EACH DRINK WITH BAYES + MDP
    # ---------------------------------------------------------
    results = []

    for drink in drinks:
        name = drink["name"]
        price = float(drink["price"])

        b_score = bayesian_score(name, history_counts)
        m_score = mdp_score(price, budget_state)
        final_score = 0.6 * b_score + 0.4 * m_score

        results.append({
            "name": name,
            "price": price,
            "score": round(final_score, 4)
        })
        print(f"Drink: {name}, Price: {price}, Bayes: {b_score}, MDP: {m_score}, Final: {final_score}")

    # ---------------------------------------------------------
    # E) SORT + RETURN TOP 3
    # ---------------------------------------------------------
    results.sort(key=lambda x: x["score"], reverse=True)
    print("Final sorted results:", results[:3])
    return results[:3]
