"""Simple rule-based budgeting logic. No ML — just readable thresholds."""
from typing import Tuple

TARGET_SAVINGS_RATE = 0.20  # aim to save ~20% of income when possible


def compute_budget_suggestion(income: float, expenses: float) -> Tuple[str, float]:
    """Return (plain_language_suggestion, recommended_savings) for the given
    monthly income and expenses (both in INR).
    """
    surplus = income - expenses
    ideal_savings = income * TARGET_SAVINGS_RATE

    if surplus <= 0:
        recommended_savings = 0.0
        suggestion = (
            "Right now your monthly spending is the same as or more than what comes in, "
            "so there isn't anything left to save yet. A good first step is to write down "
            "every expense for one month and see which two or three items take up the "
            "biggest share — often it's small, frequent spends rather than one big one. "
            "Even a small cut in the largest category can create some breathing room."
        )
    elif surplus < ideal_savings:
        recommended_savings = round(surplus * 0.8, 2)
        suggestion = (
            f"You have some money left over each month. Try setting aside about "
            f"₹{recommended_savings:,.0f} of it regularly, somewhere safe like a bank "
            "recurring deposit or a post office savings scheme — ask your bank or post "
            "office which one suits you best. Once this feels comfortable, you can slowly "
            "try to save a little more each month."
        )
    else:
        recommended_savings = round(ideal_savings, 2)
        suggestion = (
            f"You're in a healthy position. A good goal is to save around "
            f"₹{recommended_savings:,.0f} every month — roughly a fifth of your income — "
            "keeping the rest for expenses and a small buffer for surprises. A recurring "
            "deposit or a goal-based savings scheme at your bank or post office could help "
            "you stay consistent — do check the current rates with them."
        )

    return suggestion, recommended_savings
