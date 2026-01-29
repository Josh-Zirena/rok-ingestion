"""Data validation utilities."""

import pandas as pd

from .config import REQUIRED_COLUMNS


def validate_required_columns(df: pd.DataFrame) -> None:
    """
    Validate that DataFrame has required columns.
    
    Args:
        df: DataFrame to validate
        
    Raises:
        ValueError: If required columns are missing
    """
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")


def validate_unique_id(df: pd.DataFrame) -> None:
    """
    Validate that id column has unique values.
    
    Args:
        df: DataFrame to validate
        
    Raises:
        ValueError: If id has null/empty values or duplicates
    """
    # Check for null or empty values
    if df["id"].isna().any():
        raise ValueError("id column contains null values")
    
    # Convert to string and check for empty strings
    id_str = df["id"].astype(str).str.strip()
    if (id_str == "").any():
        raise ValueError("id column contains empty values")
    
    # Check for duplicates
    duplicates = df[df["id"].duplicated(keep=False)]
    if not duplicates.empty:
        # Show first few duplicate values
        duplicate_ids = duplicates["id"].unique()[:5]
        raise ValueError(
            f"id column contains duplicate values. "
            f"Examples: {list(duplicate_ids)}"
        )
