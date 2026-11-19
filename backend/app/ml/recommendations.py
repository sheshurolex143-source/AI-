"""Personalized recommendation engine and financial health score calculator."""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd


class RecommendationEngine:
    """Rule-based and data-driven financial recommendation and health score engine."""

    def calculate_health_score(
        self,
        transactions_df: pd.DataFrame,
        budgets: Optional[List[Any]] = None,
        goals: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """Calculate a transparent 0-100 financial health score.

        Score breakdown:
        - Savings Rate (0-25 pts): >=20% ideal
        - Budget Adherence (0-25 pts): % of categories within monthly limit
        - Debt / Fixed Commitments Ratio (0-20 pts): EMI + rent vs income (<40% ideal)
        - Spending Stability (0-15 pts): Low MoM variance
        - Emergency Fund / Goals Progress (0-15 pts): Progress on emergency/savings goals
        """
        if transactions_df.empty:
            return {
                "score": 50,
                "breakdown": {
                    "savings_rate": 10.0,
                    "budget_adherence": 15.0,
                    "debt_ratio": 10.0,
                    "spending_stability": 8.0,
                    "emergency_fund": 7.0,
                },
                "grade": "C",
                "tips": ["Add transactions to get an accurate financial health assessment."],
            }

        df = transactions_df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M")

        income_total = df[df["type"] == "income"]["amount"].sum()
        expense_total = df[df["type"] == "expense"]["amount"].sum()

        # Monthly averages
        months_count = max(df["month"].nunique(), 1)
        avg_monthly_income = income_total / months_count
        avg_monthly_expense = expense_total / months_count

        # 1. Savings Rate Score (0 - 25 pts)
        if avg_monthly_income > 0:
            savings_rate = max(0.0, (avg_monthly_income - avg_monthly_expense) / avg_monthly_income)
        else:
            savings_rate = 0.0

        if savings_rate >= 0.30:
            savings_score = 25.0
        elif savings_rate >= 0.20:
            savings_score = 20.0 + (savings_rate - 0.20) * 50.0
        elif savings_rate >= 0.10:
            savings_score = 10.0 + (savings_rate - 0.10) * 100.0
        else:
            savings_score = max(0.0, savings_rate * 100.0)

        # 2. Budget Adherence Score (0 - 25 pts)
        budget_score = 20.0  # default baseline
        if budgets and len(budgets) > 0:
            adherence_counts = 0
            for b in budgets:
                cat = getattr(b, "category", None) or b.get("category")
                limit = getattr(b, "monthly_limit", None) or b.get("monthly_limit", 0)
                spent = getattr(b, "spent", None) or b.get("spent", 0)
                if spent <= limit:
                    adherence_counts += 1
            adherence_ratio = adherence_counts / len(budgets)
            budget_score = adherence_ratio * 25.0

        # 3. Debt Ratio / Fixed Commitments (0 - 20 pts)
        debt_expense = df[(df["type"] == "expense") & (df["category"].isin(["Rent & Housing", "Bills & Utilities"]))]["amount"].sum()
        avg_debt_monthly = debt_expense / months_count
        if avg_monthly_income > 0:
            debt_ratio = avg_debt_monthly / avg_monthly_income
        else:
            debt_ratio = 0.5

        if debt_ratio <= 0.30:
            debt_score = 20.0
        elif debt_ratio <= 0.45:
            debt_score = 20.0 - (debt_ratio - 0.30) * (10.0 / 0.15)
        else:
            debt_score = max(2.0, 10.0 - (debt_ratio - 0.45) * 20.0)

        # 4. Spending Stability Score (0 - 15 pts)
        monthly_expenses = df[df["type"] == "expense"].groupby("month")["amount"].sum()
        if len(monthly_expenses) > 1:
            std_dev = monthly_expenses.std()
            mean_exp = monthly_expenses.mean()
            cv = (std_dev / mean_exp) if mean_exp > 0 else 0
            if cv < 0.15:
                stability_score = 15.0
            elif cv < 0.30:
                stability_score = 12.0
            elif cv < 0.50:
                stability_score = 8.0
            else:
                stability_score = 4.0
        else:
            stability_score = 12.0

        # 5. Emergency Fund & Goal Progress (0 - 15 pts)
        emergency_score = 8.0
        if goals and len(goals) > 0:
            progresses = []
            for g in goals:
                target = getattr(g, "target_amount", 0) or g.get("target_amount", 1)
                curr = getattr(g, "current_amount", 0) or g.get("current_amount", 0)
                if target > 0:
                    progresses.append(min(1.0, curr / target))
            if progresses:
                emergency_score = np.mean(progresses) * 15.0

        total_score = int(round(savings_score + budget_score + debt_score + stability_score + emergency_score))
        total_score = max(0, min(100, total_score))

        # Grade assignment
        if total_score >= 90:
            grade = "A+"
        elif total_score >= 80:
            grade = "A"
        elif total_score >= 70:
            grade = "B"
        elif total_score >= 60:
            grade = "C"
        elif total_score >= 50:
            grade = "D"
        else:
            grade = "F"

        tips = []
        if savings_score < 15.0:
            tips.append("Aim to set aside at least 20% of your net income into savings/investments.")
        if budget_score < 18.0:
            tips.append("Review categories exceeding monthly limits and set realistic alerts.")
        if debt_score < 12.0:
            tips.append("Fixed obligations (rent, EMI, bills) exceed 40% of income; consider debt consolidation.")
        if stability_score < 10.0:
            tips.append("Your monthly expenses fluctuate significantly. Track impulse purchases.")
        if emergency_score < 10.0:
            tips.append("Accelerate contributions to your Emergency Fund to cover 3-6 months of living costs.")
        if not tips:
            tips.append("Excellent financial hygiene! Keep maintaining your savings habits.")

        return {
            "score": total_score,
            "breakdown": {
                "savings_rate": round(savings_score, 1),
                "budget_adherence": round(budget_score, 1),
                "debt_ratio": round(debt_score, 1),
                "spending_stability": round(stability_score, 1),
                "emergency_fund": round(emergency_score, 1),
            },
            "grade": grade,
            "tips": tips,
        }

    def generate_recommendations(
        self,
        transactions_df: pd.DataFrame,
        budgets: Optional[List[Any]] = None,
        goals: Optional[List[Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Generate ranked, evidence-based recommendations."""
        if transactions_df.empty:
            return []

        df = transactions_df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M")
        months_count = max(df["month"].nunique(), 1)

        recommendations = []

        # 1. Food delivery & Dining out check
        food_exp = df[(df["type"] == "expense") & (df["category"] == "Food & Dining")]["amount"].sum()
        monthly_food = food_exp / months_count
        if monthly_food > 5000:
            est_saving = round(monthly_food * 0.25)
            recommendations.append({
                "title": "Optimize Food Delivery Spending",
                "reason": "High frequency of restaurant & food delivery orders",
                "evidence": f"You spend approx ₹{monthly_food:,.0f}/month on Food & Dining. Cutting delivery by 25% frees up money for investments.",
                "estimated_saving": float(est_saving),
                "priority": "high" if monthly_food > 8000 else "medium",
                "category": "Food & Dining",
            })

        # 2. Overlapping or Unused Subscriptions
        sub_df = df[(df["type"] == "expense") & (df["category"] == "Entertainment & Subscriptions")]
        monthly_subs = sub_df["amount"].sum() / months_count
        if monthly_subs > 1500:
            recommendations.append({
                "title": "Review Active Streaming & Entertainment Subscriptions",
                "reason": "Multiple recurring entertainment subscriptions detected",
                "evidence": f"Total subscriptions cost ₹{monthly_subs:,.0f}/month across platforms (Netflix, Prime, Spotify, etc.).",
                "estimated_saving": 650.0,
                "priority": "medium",
                "category": "Entertainment & Subscriptions",
            })

        # 3. High Shopping Spend Spikes
        shop_df = df[(df["type"] == "expense") & (df["category"] == "Shopping")]
        monthly_shop = shop_df["amount"].sum() / months_count
        if monthly_shop > 6000:
            est_saving = round(monthly_shop * 0.20)
            recommendations.append({
                "title": "Establish 48-Hour Rule for Non-Essential Shopping",
                "reason": "Discretionary retail and e-commerce purchases are elevated",
                "evidence": f"E-commerce spend averages ₹{monthly_shop:,.0f}/month across Amazon, Flipkart, Myntra.",
                "estimated_saving": float(est_saving),
                "priority": "medium",
                "category": "Shopping",
            })

        # 4. Emergency Fund Coverage
        income_total = df[df["type"] == "income"]["amount"].sum()
        monthly_income = income_total / months_count
        monthly_expense = df[df["type"] == "expense"]["amount"].sum() / months_count

        ef_target = monthly_expense * 6
        ef_current = 0
        if goals:
            for g in goals:
                name = getattr(g, "name", "").lower()
                if "emergency" in name:
                    ef_current = getattr(g, "current_amount", 0)

        if ef_current < ef_target * 0.5:
            recommendations.append({
                "title": "Under-funded Emergency Buffer",
                "reason": "Emergency reserves are below 6 months of mandatory living expenses",
                "evidence": f"Current estimated buffer is ₹{ef_current:,.0f} vs ideal target of ₹{ef_target:,.0f} (₹{monthly_expense:,.0f}/month).",
                "estimated_saving": 0.0,
                "priority": "high",
                "category": "Investments & Savings",
            })

        # 5. Fixed Debt / EMI burden
        bill_emi = df[(df["type"] == "expense") & (df["category"].isin(["Rent & Housing", "Bills & Utilities"]))]["amount"].sum() / months_count
        if monthly_income > 0 and (bill_emi / monthly_income) > 0.40:
            ratio_pct = round((bill_emi / monthly_income) * 100)
            recommendations.append({
                "title": "High Fixed Commitments Ratio",
                "reason": "Fixed living expenses & EMI consume over 40% of net income",
                "evidence": f"Fixed obligations (Rent, Utilities, EMI) account for {ratio_pct}% of total monthly inflow (₹{bill_emi:,.0f}).",
                "estimated_saving": 1500.0,
                "priority": "high",
                "category": "Bills & Utilities",
            })

        # 6. Budget Overrun Warnings
        if budgets:
            for b in budgets:
                cat = getattr(b, "category", "")
                spent = getattr(b, "spent", 0)
                limit = getattr(b, "monthly_limit", 0)
                if limit > 0 and spent > limit:
                    over_amt = spent - limit
                    recommendations.append({
                        "title": f"Budget Breach in {cat}",
                        "reason": f"Current spend exceeds designated monthly cap of ₹{limit:,.0f}",
                        "evidence": f"Spent ₹{spent:,.0f} against a limit of ₹{limit:,.0f} (₹{over_amt:,.0f} overspent).",
                        "estimated_saving": float(over_amt),
                        "priority": "high",
                        "category": cat,
                    })

        # Fallback default if very few recommendations
        if not recommendations:
            recommendations.append({
                "title": "Automate Monthly SIPs on Salary Day",
                "reason": "Pay yourself first habit ensures consistent wealth compounding",
                "evidence": "Consistent monthly SIPs can boost net portfolio yield by 12-14% CAGR over 5 years.",
                "estimated_saving": 2000.0,
                "priority": "low",
                "category": "Investments & Savings",
            })

        # Priority sort: high -> medium -> low
        priority_map = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda r: priority_map.get(r["priority"], 3))
        return recommendations

    def what_if_simulation(
        self,
        transactions_df: pd.DataFrame,
        adjustments: Dict[str, float],
        budgets: Optional[List[Any]] = None,
        goals: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """Simulate budget reductions by category and evaluate impact on health score."""
        if transactions_df.empty:
            return {
                "current_monthly_spend": 0.0,
                "projected_monthly_spend": 0.0,
                "monthly_savings": 0.0,
                "yearly_savings": 0.0,
                "new_health_score": 50,
                "category_impact": [],
            }

        df = transactions_df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M")
        months_count = max(df["month"].nunique(), 1)

        expenses_df = df[df["type"] == "expense"]
        cat_monthly_spend = expenses_df.groupby("category")["amount"].sum() / months_count

        total_current_monthly = float(cat_monthly_spend.sum())
        total_monthly_saving = 0.0
        impacts = []

        # Copy dataframe for modified simulation
        sim_df = df.copy()

        for cat, curr_spend in cat_monthly_spend.items():
            curr_spend_val = float(curr_spend)
            reduction_pct = float(adjustments.get(cat, 0.0))
            reduction_pct = max(0.0, min(100.0, reduction_pct))
            saving = curr_spend_val * (reduction_pct / 100.0)
            new_spend = curr_spend_val - saving
            total_monthly_saving += saving

            impacts.append({
                "category": cat,
                "current_spend": round(curr_spend_val, 2),
                "reduction_percent": round(reduction_pct, 1),
                "new_spend": round(new_spend, 2),
                "saving": round(saving, 2),
            })

            # Scale amounts in sim_df for this category
            if reduction_pct > 0:
                mask = (sim_df["type"] == "expense") & (sim_df["category"] == cat)
                sim_df.loc[mask, "amount"] = sim_df.loc[mask, "amount"] * (1.0 - reduction_pct / 100.0)

        projected_monthly = max(0.0, total_current_monthly - total_monthly_saving)
        yearly_savings = total_monthly_saving * 12.0

        # Recalculate health score with modified spend
        new_health = self.calculate_health_score(sim_df, budgets, goals)

        return {
            "current_monthly_spend": round(total_current_monthly, 2),
            "projected_monthly_spend": round(projected_monthly, 2),
            "monthly_savings": round(total_monthly_saving, 2),
            "yearly_savings": round(yearly_savings, 2),
            "new_health_score": new_health["score"],
            "category_impact": impacts,
        }


recommendation_engine = RecommendationEngine()
