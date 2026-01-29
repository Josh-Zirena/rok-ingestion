"""Data normalization utilities."""

import pandas as pd


def normalize_df(df: pd.DataFrame, kingdom: str, dt: str) -> pd.DataFrame:
    """
    Normalize a DataFrame by adding kingdom and dt columns.
    
    Args:
        df: Input DataFrame (column names should already be lowercase)
        kingdom: Kingdom identifier
        dt: Date string (YYYY-MM-DD)
        
    Returns:
        Normalized DataFrame
    """
    # Create a copy to avoid modifying the original
    df = df.copy()
    
    # Ensure id is string type and strip whitespace
    df["id"] = df["id"].astype(str).str.strip()
    
    # Add metadata columns
    df["kingdom"] = str(kingdom)
    df["snapshot_date"] = dt
    
    return df
