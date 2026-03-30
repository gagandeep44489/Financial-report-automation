"""Data loading and cleaning utilities for financial report automation."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {"date", "category", "type", "amount"}


class DataLoaderError(Exception):
    """Raised when input data cannot be loaded or validated."""


def _validate_columns(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(df.columns.str.lower())
    if missing:
        raise DataLoaderError(
            f"Missing required columns: {sorted(missing)}. "
            "Expected columns include: date, category, type, amount"
        )


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [column.strip().lower() for column in df.columns]
    return df


def load_financial_data(path: str, table_name: str = "transactions") -> pd.DataFrame:
    """Load transactions from CSV, Excel, or SQLite database.

    Args:
        path: Source file path.
        table_name: SQLite table name when a database file is supplied.

    Returns:
        Cleaned transaction DataFrame.
    """

    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Input file not found: {source}")

    logging.info("Loading data from %s", source)

    suffix = source.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(source)
    elif suffix in {".xls", ".xlsx"}:
        df = pd.read_excel(source)
    elif suffix in {".db", ".sqlite", ".sqlite3"}:
        with sqlite3.connect(source) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    else:
        raise DataLoaderError(
            f"Unsupported format '{suffix}'. Use CSV, Excel, or SQLite database files."
        )

    df = _normalize_columns(df)
    _validate_columns(df)

    return clean_financial_data(df)


def clean_financial_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize transaction data."""

    cleaned = df.copy()

    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
    cleaned["category"] = cleaned["category"].astype(str).str.strip().replace({"": "Unknown"})
    cleaned["type"] = (
        cleaned["type"]
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({"revenue": "income", "expense": "expense", "expenses": "expense"})
    )
    cleaned["amount"] = pd.to_numeric(cleaned["amount"], errors="coerce")

    null_rows = cleaned[cleaned[["date", "amount"]].isna().any(axis=1)]
    if not null_rows.empty:
        logging.warning("Dropping %d rows with invalid date/amount values", len(null_rows))

    cleaned = cleaned.dropna(subset=["date", "amount"])

    invalid_types = ~cleaned["type"].isin(["income", "expense"])
    if invalid_types.any():
        logging.warning("Normalizing %d rows with unknown type as 'expense'", invalid_types.sum())
        cleaned.loc[invalid_types, "type"] = "expense"

    cleaned["year"] = cleaned["date"].dt.year
    cleaned["month"] = cleaned["date"].dt.to_period("M").astype(str)

    return cleaned.sort_values("date").reset_index(drop=True)
