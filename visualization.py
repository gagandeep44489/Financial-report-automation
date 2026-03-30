"""Chart generation for financial reporting."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


plt.style.use("ggplot")


def create_charts(monthly_df: pd.DataFrame, expense_category_df: pd.DataFrame, output_dir: Path) -> dict[str, Path]:
    """Create bar, pie, and line charts and save as PNG files."""

    output_dir.mkdir(parents=True, exist_ok=True)

    chart_paths: dict[str, Path] = {}

    # Bar chart: income vs expenses
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(monthly_df["month"], monthly_df.get("income", 0), label="Income")
    ax.bar(monthly_df["month"], monthly_df.get("expense", 0), label="Expenses")
    ax.set_title("Income vs Expenses by Month")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    path_bar = output_dir / "income_vs_expenses_bar.png"
    fig.savefig(path_bar, dpi=150)
    plt.close(fig)
    chart_paths["bar"] = path_bar

    # Pie chart: expense categories
    fig, ax = plt.subplots(figsize=(7, 7))
    if not expense_category_df.empty:
        ax.pie(
            expense_category_df["amount"],
            labels=expense_category_df["category"],
            autopct="%1.1f%%",
            startangle=140,
        )
        ax.set_title("Expense Category Distribution")
    else:
        ax.text(0.5, 0.5, "No expense data", ha="center", va="center")
    plt.tight_layout()
    path_pie = output_dir / "expense_categories_pie.png"
    fig.savefig(path_pie, dpi=150)
    plt.close(fig)
    chart_paths["pie"] = path_pie

    # Line chart: monthly trend
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(monthly_df["month"], monthly_df.get("income", 0), marker="o", label="Income")
    ax.plot(monthly_df["month"], monthly_df.get("expense", 0), marker="o", label="Expenses")
    ax.plot(monthly_df["month"], monthly_df.get("net_profit", 0), marker="o", label="Net Profit")
    ax.set_title("Monthly Financial Trends")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    path_line = output_dir / "monthly_trends_line.png"
    fig.savefig(path_line, dpi=150)
    plt.close(fig)
    chart_paths["line"] = path_line

    return chart_paths
