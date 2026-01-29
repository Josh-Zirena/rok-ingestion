"""Hashing utilities for data deduplication."""

import hashlib
from datetime import datetime, timezone
from uuid import uuid4

import pandas as pd


def add_record_hash(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a hash column to DataFrame for deduplication.
    
    The hash is computed from business fields only (excluding metadata).
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with added record_hash column
    """
    df = df.copy()
    
    # Columns to exclude from hash computation
    exclude_cols = {"record_hash", "ingested_at", "run_id", "kingdom", "snapshot_date"}
    
    # Get columns to include in hash (sorted for determinism)
    hash_cols = sorted([col for col in df.columns if col not in exclude_cols])
    
    # Compute hash for each row
    def hash_row(row):
        # Create deterministic string representation
        values = [str(row[col]) for col in hash_cols]
        row_str = "|".join(values)
        return hashlib.sha256(row_str.encode("utf-8")).hexdigest()
    
    df["record_hash"] = df.apply(hash_row, axis=1)
    
    return df


def add_ingestion_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add ingestion metadata columns.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with added ingested_at and run_id columns
    """
    df = df.copy()
    
    # Add UTC timestamp in ISO format
    df["ingested_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Add run_id (same for all rows in this ingestion)
    df["run_id"] = str(uuid4())
    
    return df
