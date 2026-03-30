# Financial Report Automation System

A production-oriented Python project to automate financial reporting from raw transactions in **CSV / Excel / SQLite** and generate professional reports in **Excel, PDF, and optional HTML dashboard**.

## Features

- Data ingestion from CSV, Excel (`.xls/.xlsx`), and SQLite databases.
- Data cleaning (null handling, type normalization, date/amount parsing).
- Monthly and yearly aggregation.
- Core KPIs:
  - Total Revenue
  - Total Expenses
  - Net Profit
  - Profit Margin %
- Auto analysis:
  - Top expense categories
  - Trend detection (income, expense, profitability)
  - Insight text generation
- Visualizations:
  - Bar chart (income vs expenses)
  - Pie chart (expense categories)
  - Line chart (monthly trends)
- Automated report export to timestamped `reports/` folder.
- Logging and error handling.
- CLI support with `argparse`.

## Project Structure

```text
.
├── data_loader.py
├── analysis.py
├── visualization.py
├── report_generator.py
├── main.py
├── requirements.txt
├── data/
│   └── example_transactions.csv
└── reports/
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Basic

```bash
python main.py data/example_transactions.csv
```

By default, reports are generated under:

`~/Downloads/financial_reports/report_<timestamp>/`

### Quick start (no arguments)

If `data/example_transactions.csv` exists in the project folder (same base folder as `main.py`), you can run:

```bash
python main.py
```

### With custom output directory

```bash
python main.py data/example_transactions.csv --output-dir reports
```

### Generate only selected report formats

```bash
python main.py data/example_transactions.csv --report-formats excel
python main.py data/example_transactions.csv --report-formats pdf html
```

### Export cleaned data for users (CSV/XLSX)

```bash
python main.py data/example_transactions.csv --data-export-format csv
python main.py data/example_transactions.csv --data-export-format both
```

### SQLite input

```bash
python main.py finance.sqlite --table transactions
```

### Disable HTML dashboard

```bash
python main.py data/example_transactions.csv --report-formats excel pdf
```

## Automation / Scheduling

### Cron (Linux/Mac)

Run every day at 7 AM:

```cron
0 7 * * * /usr/bin/python /path/to/project/main.py /path/to/project/data/example_transactions.csv --output-dir /path/to/project/reports
```

### Windows Task Scheduler

Use `python.exe` as program and pass `main.py <input_path> --output-dir <reports_dir>` as arguments.

## Sample Run Output

```text
2026-03-30 12:00:00,123 | INFO | Loading data from data/example_transactions.csv
2026-03-30 12:00:01,020 | INFO | Report generated successfully at: /project/reports/report_20260330_120001
```

Generated artifacts:

- `financial_report.xlsx`
- `financial_report.pdf`
- `dashboard.html` (optional)
- `charts/*.png`

## Deploy to GitHub

1. Create a new repository on GitHub.
2. Push your code:

```bash
git init
git add .
git commit -m "Add financial report automation system"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

3. Add screenshots of generated dashboard/charts in README for portfolio impact.
4. Share on LinkedIn with title:

> Automated financial reporting system using Python (Excel + PDF + Charts)

## Notes

- This starter is designed for extensibility (e.g., OpenAI-generated narratives, web app dashboard, cloud deployment).
- Works well as a freelance deliverable or SaaS MVP foundation.
