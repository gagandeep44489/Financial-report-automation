"""Financial analysis and insight generation."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class FinancialMetrics:
    total_revenue: float
    total_expenses: float
    net_profit: float
    profit_margin_pct: float


def calculate_metrics(df: pd.DataFrame) -> FinancialMetrics:
    """Compute core financial metrics."""

    total_revenue = float(df.loc[df["type"] == "income", "amount"].sum())
    total_expenses = float(df.loc[df["type"] == "expense", "amount"].sum())
    net_profit = total_revenue - total_expenses
    profit_margin_pct = (net_profit / total_revenue * 100) if total_revenue else 0.0

    return FinancialMetrics(
        total_revenue=round(total_revenue, 2),
        total_expenses=round(total_expenses, 2),
        net_profit=round(net_profit, 2),
        profit_margin_pct=round(profit_margin_pct, 2),
    )


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate monthly income, expenses, and net profit."""

    monthly = (
        df.pivot_table(index="month", columns="type", values="amount", aggfunc="sum", fill_value=0)
        .reset_index()
        .rename_axis(None, axis=1)
    )
    monthly["net_profit"] = monthly.get("income", 0) - monthly.get("expense", 0)
    return monthly.sort_values("month")


def yearly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate yearly income, expenses, and net profit."""

    yearly = (
        df.pivot_table(index="year", columns="type", values="amount", aggfunc="sum", fill_value=0)
        .reset_index()
        .rename_axis(None, axis=1)
    )
    yearly["net_profit"] = yearly.get("income", 0) - yearly.get("expense", 0)
    return yearly.sort_values("year")


def top_expense_categories(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """Return highest expense categories."""

    expense_df = df[df["type"] == "expense"]
    result = (
        expense_df.groupby("category", as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
        .head(top_n)
    )
    return result


def detect_trends(monthly_df: pd.DataFrame) -> dict[str, str]:
    """Detect trend directions for income, expenses, and profit."""

    def trend_for(column: str) -> str:
        if column not in monthly_df.columns or len(monthly_df) < 2:
            return "insufficient data"
        delta = monthly_df[column].iloc[-1] - monthly_df[column].iloc[0]
        if delta > 0:
            return "increasing"
        if delta < 0:
            return "decreasing"
        return "stable"

    return {
        "income_trend": trend_for("income"),
        "expense_trend": trend_for("expense"),
        "profit_trend": trend_for("net_profit"),
    }


def generate_insights(metrics: FinancialMetrics, top_expenses: pd.DataFrame, trends: dict[str, str]) -> list[str]:
    """Generate executive-style summary insights."""

    insights = [
        f"Total revenue is ${metrics.total_revenue:,.2f} and total expenses are ${metrics.total_expenses:,.2f}.",
        f"Net profit is ${metrics.net_profit:,.2f} with a profit margin of {metrics.profit_margin_pct:.2f}%.",
        f"Income trend is {trends['income_trend']}, while expense trend is {trends['expense_trend']}.",
        f"Overall monthly profitability trend is {trends['profit_trend']}.",
    ]

    if not top_expenses.empty:
        top = top_expenses.iloc[0]
        insights.append(
            f"Top expense category is '{top['category']}' at ${float(top['amount']):,.2f}."
        )

    if metrics.net_profit < 0:
        insights.append("Business is running at a loss; cost control actions are recommended.")
    elif metrics.profit_margin_pct < 10:
        insights.append("Profit margin is thin; review high-cost categories for optimization opportunities.")
    else:
        insights.append("Profitability is healthy based on current margin levels.")

    return insights
