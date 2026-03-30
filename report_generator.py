"""Excel, PDF, and HTML report generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from fpdf import FPDF

from analysis import FinancialMetrics


def generate_excel_report(
    output_path: Path,
    metrics: FinancialMetrics,
    monthly_df: pd.DataFrame,
    yearly_df: pd.DataFrame,
    top_expenses_df: pd.DataFrame,
    insights: list[str],
    chart_paths: dict[str, Path],
) -> None:
    """Generate an Excel report with tables and embedded charts."""

    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        summary_df = pd.DataFrame(
            {
                "Metric": ["Total Revenue", "Total Expenses", "Net Profit", "Profit Margin %"],
                "Value": [
                    metrics.total_revenue,
                    metrics.total_expenses,
                    metrics.net_profit,
                    metrics.profit_margin_pct,
                ],
            }
        )
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        monthly_df.to_excel(writer, sheet_name="Monthly Summary", index=False)
        yearly_df.to_excel(writer, sheet_name="Yearly Summary", index=False)
        top_expenses_df.to_excel(writer, sheet_name="Top Expenses", index=False)

        insights_df = pd.DataFrame({"Key Insights": insights})
        insights_df.to_excel(writer, sheet_name="Insights", index=False)

        workbook = writer.book
        charts_ws = workbook.add_worksheet("Charts")
        charts_ws.insert_image("A1", str(chart_paths["bar"]))
        charts_ws.insert_image("A24", str(chart_paths["pie"]))
        charts_ws.insert_image("J1", str(chart_paths["line"]))


def generate_pdf_report(
    output_path: Path,
    metrics: FinancialMetrics,
    insights: list[str],
    chart_paths: dict[str, Path],
) -> None:
    """Generate a PDF report with summary, insights, and charts."""

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Financial Performance Report", ln=True)

    pdf.set_font("Helvetica", size=11)
    pdf.ln(2)
    pdf.cell(0, 8, f"Total Revenue: ${metrics.total_revenue:,.2f}", ln=True)
    pdf.cell(0, 8, f"Total Expenses: ${metrics.total_expenses:,.2f}", ln=True)
    pdf.cell(0, 8, f"Net Profit: ${metrics.net_profit:,.2f}", ln=True)
    pdf.cell(0, 8, f"Profit Margin: {metrics.profit_margin_pct:.2f}%", ln=True)

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Key Insights", ln=True)
    pdf.set_font("Helvetica", size=11)
    for insight in insights:
        pdf.multi_cell(0, 7, f"- {insight}")

    for chart_key in ["bar", "pie", "line"]:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, f"Chart: {chart_key.upper()}", ln=True)
        pdf.image(str(chart_paths[chart_key]), x=10, y=25, w=190)

    pdf.output(str(output_path))


def generate_html_dashboard(
    output_path: Path,
    metrics: FinancialMetrics,
    insights: list[str],
    chart_paths: dict[str, Path],
) -> None:
    """Generate a lightweight HTML dashboard."""

    html = f"""
    <html>
    <head>
      <title>Financial Dashboard</title>
      <style>
        body {{ font-family: Arial, sans-serif; margin: 24px; }}
        .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin-bottom: 16px; }}
        img {{ max-width: 900px; width: 100%; margin-bottom: 24px; }}
      </style>
    </head>
    <body>
      <h1>Financial Dashboard</h1>
      <div class="card">
        <h2>Summary</h2>
        <ul>
          <li>Total Revenue: ${metrics.total_revenue:,.2f}</li>
          <li>Total Expenses: ${metrics.total_expenses:,.2f}</li>
          <li>Net Profit: ${metrics.net_profit:,.2f}</li>
          <li>Profit Margin: {metrics.profit_margin_pct:.2f}%</li>
        </ul>
      </div>
      <div class="card">
        <h2>Insights</h2>
        <ul>
          {''.join(f'<li>{i}</li>' for i in insights)}
        </ul>
      </div>
      <h2>Charts</h2>
      <img src="{chart_paths['bar'].name}" alt="Income vs Expenses">
      <img src="{chart_paths['pie'].name}" alt="Expense Categories">
      <img src="{chart_paths['line'].name}" alt="Monthly Trends">
    </body>
    </html>
    """

    output_path.write_text(html.strip(), encoding="utf-8")
