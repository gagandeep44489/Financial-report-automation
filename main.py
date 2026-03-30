"""Entry point for financial report automation."""

from __future__ import annotations

import argparse
import logging
from datetime import datetime
from pathlib import Path

from analysis import (
    calculate_metrics,
    detect_trends,
    generate_insights,
    monthly_summary,
    top_expense_categories,
    yearly_summary,
)
from data_loader import DataLoaderError, load_financial_data
from report_generator import generate_excel_report, generate_html_dashboard, generate_pdf_report
from visualization import create_charts

DEFAULT_SAMPLE_RELATIVE_PATH = Path("data") / "example_transactions.csv"
DEFAULT_OUTPUT_DIR = Path.home() / "Downloads" / "financial_reports"


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s | %(levelname)s | %(message)s")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Automated Financial Report Generator")
    parser.add_argument(
        "input_path",
        nargs="?",
        default=None,
        help=(
            "Path to CSV, Excel, or SQLite data source. "
            "If omitted, the script uses data/example_transactions.csv next to main.py."
        ),
    )
    parser.add_argument("--table", default="transactions", help="SQLite table name (default: transactions)")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Output directory for generated reports (default: ~/Downloads/financial_reports)",
    )
    parser.add_argument(
        "--report-formats",
        nargs="+",
        choices=["excel", "pdf", "html"],
        default=["excel", "pdf", "html"],
        help="Choose report formats to generate (default: excel pdf html).",
    )
    parser.add_argument(
        "--data-export-format",
        choices=["none", "csv", "xlsx", "both"],
        default="none",
        help="Optional export of cleaned transaction data for users.",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser


def run(
    input_path: str,
    table_name: str,
    output_dir: str,
    report_formats: set[str],
    data_export_format: str,
) -> Path:
    data = load_financial_data(input_path, table_name=table_name)

    metrics = calculate_metrics(data)
    monthly_df = monthly_summary(data)
    yearly_df = yearly_summary(data)
    top_expenses_df = top_expense_categories(data)
    trends = detect_trends(monthly_df)
    insights = generate_insights(metrics, top_expenses_df, trends)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = Path(output_dir) / f"report_{timestamp}"
    charts_dir = report_dir / "charts"
    report_dir.mkdir(parents=True, exist_ok=True)

    chart_paths = create_charts(monthly_df, top_expenses_df, charts_dir)

    if "excel" in report_formats:
        excel_path = report_dir / "financial_report.xlsx"
        generate_excel_report(
            excel_path, metrics, monthly_df, yearly_df, top_expenses_df, insights, chart_paths
        )

    if "pdf" in report_formats:
        pdf_path = report_dir / "financial_report.pdf"
        generate_pdf_report(pdf_path, metrics, insights, chart_paths)

    if "html" in report_formats:
        html_path = report_dir / "dashboard.html"
        generate_html_dashboard(html_path, metrics, insights, chart_paths)

    if data_export_format in {"csv", "both"}:
        data.to_csv(report_dir / "cleaned_transactions.csv", index=False)
    if data_export_format in {"xlsx", "both"}:
        data.to_excel(report_dir / "cleaned_transactions.xlsx", index=False)

    logging.info("Report generated successfully at: %s", report_dir.resolve())
    return report_dir


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    configure_logging(args.verbose)

    try:
        if args.input_path:
            input_path = args.input_path
        else:
            script_dir = Path(__file__).resolve().parent
            input_path = str(script_dir / DEFAULT_SAMPLE_RELATIVE_PATH)

        if not Path(input_path).exists():
            logging.error(
                "Input file was not found at: %s. "
                "Please pass an input file path, e.g. `python main.py data/example_transactions.csv`.",
                input_path,
            )
            raise SystemExit(1)

        run(
            input_path=input_path,
            table_name=args.table,
            output_dir=args.output_dir,
            report_formats=set(args.report_formats),
            data_export_format=args.data_export_format,
        )
    except FileNotFoundError as error:
        logging.error("%s", error)
        raise SystemExit(1) from error
    except DataLoaderError as error:
        logging.error("Data loading error: %s", error)
        raise SystemExit(2) from error
    except Exception as error:  # pylint: disable=broad-except
        logging.exception("Unexpected error while generating report: %s", error)
        raise SystemExit(99) from error


if __name__ == "__main__":
    main()
