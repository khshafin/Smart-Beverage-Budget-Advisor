#!/usr/bin/env python3
"""
Test and Validate ML Models with Test Users

Tests the improved algorithms:
- MDP (Markov Decision Process) with policy iteration
- CSP (Constraint Satisfaction) with MRV heuristics
- Bayesian Inference with hierarchical priors and Thompson sampling
"""

import sqlite3
import sys
from recommendation_engine import recommend, MDPOptimizer, CSPFilter, BayesianPredictor

# Test scenarios for each user
TEST_SCENARIOS = [
    {
        'user_id': 6,
        'username': 'budget_conscious_user',
        'mood': 'Tired',
        'budget': 5.00,
        'expected_behavior': 'Should recommend cheap coffee/espresso'
    },
    {
        'user_id': 7,
        'username': 'splurge_user',
        'mood': 'Happy',
        'budget': 15.00,
        'expected_behavior': 'Should recommend premium frappuccinos/lattes'
    },
    {
        'user_id': 8,
        'username': 'balanced_user',
        'mood': 'Focused',
        'budget': 10.00,
        'expected_behavior': 'Should recommend mid-range options'
    },
    {
        'user_id': 9,
        'username': 'coffee_addict',
        'mood': 'Tired',
        'budget': 6.00,
        'expected_behavior': 'Should strongly recommend their usual cheap coffee'
    },
    {
        'user_id': 10,
        'username': 'mood_driven_user',
        'mood': 'Stressed',
        'budget': 8.00,
        'expected_behavior': 'Should match mood to suitable beverages'
    },
    {
        'user_id': 11,
        'username': 'variety_seeker',
        'mood': 'Happy',
        'budget': 10.00,
        'expected_behavior': 'Should recommend diverse drinks, possibly new ones'
    },
    {
        'user_id': 12,
        'username': 'weekend_warrior',
        'mood': 'Happy',
        'budget': 12.00,
        'expected_behavior': 'Should recommend higher-end weekend treats'
    },
    {
        'user_id': 13,
        'username': 'budget_optimizer',
        'mood': 'Focused',
        'budget': 7.00,
        'expected_behavior': 'Should optimize value/price ratio'
    }
]


def get_user_stats(user_id):
    """Get statistics for a user"""
    conn = sqlite3.connect('starbucks_budget.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            u.username,
            u.weekly_budget,
            COUNT(p.id) as total_purchases,
            SUM(p.price) as total_spent,
            AVG(p.price) as avg_price
        FROM users u
        LEFT JOIN purchases p ON u.id = p.user_id
        WHERE u.id = ?
        GROUP BY u.id
    """, (user_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            'username': row[0],
            'weekly_budget': row[1],
            'total_purchases': row[2],
            'total_spent': row[3],
            'avg_price': row[4]
        }
    return None


def analyze_recommendations(recommendations, scenario, user_stats):
    """Analyze if recommendations match expected behavior"""
    if not recommendations:
        return {
            'score': 0,
            'analysis': 'No recommendations returned',
            'passes': False
        }

    analysis = []
    score = 0.0
    max_score = 100.0

    # Get recommendation details
    prices = [r['price'] for r in recommendations]
    categories = [r['category'] for r in recommendations]
    avg_rec_price = sum(prices) / len(prices)

    # Test 1: Budget constraint (20 points)
    if all(p <= scenario['budget'] for p in prices):
        score += 20
        analysis.append("✓ All recommendations within budget")
    else:
        analysis.append("✗ Some recommendations exceed budget")

    # Test 2: Price appropriateness for user (25 points)
    user_avg = user_stats['avg_price']
    if abs(avg_rec_price - user_avg) <= 2.0:
        score += 25
        analysis.append(f"✓ Recommended price (${avg_rec_price:.2f}) matches user average (${user_avg:.2f})")
    elif avg_rec_price < user_avg:
        score += 15
        analysis.append(f"⚠ Recommended price (${avg_rec_price:.2f}) lower than user average (${user_avg:.2f})")
    else:
        score += 10
        analysis.append(f"⚠ Recommended price (${avg_rec_price:.2f}) higher than user average (${user_avg:.2f})")

    # Test 3: Diversity (15 points)
    unique_categories = len(set(categories))
    if unique_categories >= 2:
        score += 15
        analysis.append(f"✓ Good diversity ({unique_categories} categories)")
    else:
        score += 5
        analysis.append(f"⚠ Limited diversity ({unique_categories} category)")

    # Test 4: Scoring quality (20 points)
    scores = [r.get('score', 0) for r in recommendations]
    if scores and scores == sorted(scores, reverse=True):
        score += 20
        analysis.append("✓ Recommendations properly scored (descending)")
    else:
        score += 10
        analysis.append("⚠ Scoring order could be improved")

    # Test 5: Algorithm components present (20 points)
    bayesian_scores = [r.get('bayesian_score', 0) for r in recommendations]
    mdp_scores = [r.get('mdp_score', 0) for r in recommendations]
    csp_scores = [r.get('csp_score', 0) for r in recommendations]

    if all(bayesian_scores) and all(mdp_scores) and all(csp_scores):
        score += 20
        analysis.append("✓ All three algorithms (Bayesian, MDP, CSP) contributing")
    else:
        score += 10
        analysis.append("⚠ Some algorithm scores missing")

    passes = score >= 70  # Pass threshold

    return {
        'score': score,
        'analysis': '\n    '.join(analysis),
        'passes': passes,
        'avg_price': avg_rec_price
    }


def test_individual_components():
    """Test individual ML components"""
    print("\n" + "=" * 80)
    print("TESTING INDIVIDUAL ML COMPONENTS")
    print("=" * 80 + "\n")

    # Test MDP
    print("1. MDP (Markov Decision Process)")
    print("-" * 40)
    mdp = MDPOptimizer()

    # Test budget state computation
    state, ratio = mdp.compute_budget_state(25, 50)
    print(f"   Budget state for $25/$50: {state} (ratio: {ratio})")
    assert state == "MEDIUM", "Budget state computation failed"

    # Test utility function
    utility = mdp.utility_function(5.0, 0.5, 0.5)
    print(f"   Utility for $5 drink at 50% budget: {utility:.4f}")
    assert 0 <= utility <= 1, "Utility function failed"

    # Test Q-learning
    q_score = mdp.q_learning_score(5.0, "MEDIUM", 0.5, 50, [4.0, 5.0, 6.0], 0.5)
    print(f"   Q-learning score: {q_score:.4f}")
    assert q_score > 0, "Q-learning failed"

    print("   ✓ MDP tests passed\n")

    # Test CSP
    print("2. CSP (Constraint Satisfaction Problem)")
    print("-" * 40)
    csp = CSPFilter()

    candidates = [
        {'name': 'Latte', 'category': 'Latte', 'price': 4.5},
        {'name': 'Mocha', 'category': 'Latte', 'price': 5.0},
        {'name': 'Coffee', 'category': 'Coffee', 'price': 2.5}
    ]

    categories = {
        'Latte': candidates[:2],
        'Coffee': [candidates[2]]
    }

    sorted_cats = csp.minimum_remaining_values(categories)
    print(f"   MRV heuristic sorted {len(sorted_cats)} categories")
    assert len(sorted_cats) == 2, "MRV heuristic failed"

    print("   ✓ CSP tests passed\n")

    # Test Bayesian
    print("3. Bayesian Inference")
    print("-" * 40)
    bayesian = BayesianPredictor(alpha_prior=1.5)

    all_drinks = ['Latte', 'Mocha', 'Coffee']
    priors = bayesian.compute_hierarchical_prior(all_drinks)
    print(f"   Hierarchical priors computed for {len(priors)} drinks")
    assert len(priors) == 3, "Hierarchical priors failed"

    # Test Beta-Bernoulli
    alpha, beta = bayesian.beta_bernoulli_preference('Latte', [])
    print(f"   Beta-Bernoulli parameters: α={alpha}, β={beta}")
    assert alpha == 2.0 and beta == 2.0, "Beta-Bernoulli failed"

    # Test Thompson sampling
    thompson = bayesian.thompson_sampling('Latte', alpha, beta)
    print(f"   Thompson sampling score: {thompson:.4f}")
    assert 0 <= thompson <= 1, "Thompson sampling failed"

    print("   ✓ Bayesian tests passed\n")

    print("=" * 80)
    print("✅ ALL COMPONENT TESTS PASSED")
    print("=" * 80 + "\n")


def main():
    """Main testing function"""
    print("\n" + "=" * 80)
    print("ML MODEL VALIDATION WITH TEST USERS")
    print("=" * 80)

    # Test individual components first
    test_individual_components()

    # Test with real user scenarios
    print("=" * 80)
    print("TESTING RECOMMENDATIONS FOR EACH USER PROFILE")
    print("=" * 80 + "\n")

    results = []

    for scenario in TEST_SCENARIOS:
        user_id = scenario['user_id']
        username = scenario['username']
        mood = scenario['mood']
        budget = scenario['budget']

        print(f"\n{'=' * 80}")
        print(f"USER: {username} (ID: {user_id})")
        print(f"{'=' * 80}")
        print(f"Scenario: Mood={mood}, Budget=${budget}")
        print(f"Expected: {scenario['expected_behavior']}")
        print()

        # Get user stats
        user_stats = get_user_stats(user_id)
        if not user_stats:
            print(f"✗ User {user_id} not found")
            continue

        print(f"User Stats:")
        print(f"  - Weekly Budget: ${user_stats['weekly_budget']:.2f}")
        print(f"  - Total Purchases: {user_stats['total_purchases']}")
        print(f"  - Average Price: ${user_stats['avg_price']:.2f}")
        print()

        # Get recommendations
        print("Getting recommendations...")
        try:
            recommendations = recommend(user_id, mood, budget)

            if recommendations:
                print(f"\n✓ Received {len(recommendations)} recommendations:\n")
                for i, rec in enumerate(recommendations, 1):
                    print(f"{i}. {rec['name']:<30} ${rec['price']:>6.2f}  [{rec['category']}]")
                    print(f"   Scores → Bayesian: {rec['bayesian_score']:.5f} | "
                          f"MDP: {rec['mdp_score']:.5f} | CSP: {rec['csp_score']:.3f}")
                    print(f"   Final Score: {rec['score']:.5f}")
                    print()

                # Analyze recommendations
                analysis = analyze_recommendations(recommendations, scenario, user_stats)

                print(f"\n{'─' * 80}")
                print("ANALYSIS:")
                print(f"{'─' * 80}")
                print(f"  {analysis['analysis']}")
                print(f"\nQuality Score: {analysis['score']:.1f}/100")
                print(f"Result: {'✅ PASS' if analysis['passes'] else '❌ FAIL'}")

                results.append({
                    'username': username,
                    'score': analysis['score'],
                    'passes': analysis['passes']
                })

            else:
                print("✗ No recommendations returned")
                results.append({
                    'username': username,
                    'score': 0,
                    'passes': False
                })

        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'username': username,
                'score': 0,
                'passes': False
            })

    # Print summary
    print(f"\n\n{'=' * 80}")
    print("VALIDATION SUMMARY")
    print(f"{'=' * 80}\n")

    print(f"{'User':<30} {'Score':<10} {'Result'}")
    print("-" * 80)

    passed = 0
    total_score = 0

    for result in results:
        status = '✅ PASS' if result['passes'] else '❌ FAIL'
        print(f"{result['username']:<30} {result['score']:>6.1f}/100  {status}")
        if result['passes']:
            passed += 1
        total_score += result['score']

    print("-" * 80)
    avg_score = total_score / len(results) if results else 0
    pass_rate = (passed / len(results) * 100) if results else 0

    print(f"\nPass Rate: {passed}/{len(results)} ({pass_rate:.1f}%)")
    print(f"Average Score: {avg_score:.1f}/100")

    print(f"\n{'=' * 80}")
    if pass_rate >= 75:
        print("✅ ML MODELS VALIDATION: EXCELLENT")
    elif pass_rate >= 50:
        print("⚠️  ML MODELS VALIDATION: GOOD (Some improvements needed)")
    else:
        print("❌ ML MODELS VALIDATION: NEEDS IMPROVEMENT")
    print(f"{'=' * 80}\n")


if __name__ == '__main__':
    main()
