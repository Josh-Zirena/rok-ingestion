"""Local I/O operations for development and testing."""

import shutil
from pathlib import Path

import pandas as pd


def read_input_file(path: str) -> pd.DataFrame:
    """
    Read CSV or JSON file from local filesystem.
    
    Args:
        path: Local file path
        
    Returns:
        DataFrame containing the parsed data
        
    Raises:
        ValueError: If file extension is not supported
    """
    path_obj = Path(path)
    extension = path_obj.suffix.lower()
    
    if extension == ".csv":
        return pd.read_csv(path)
    elif extension == ".json":
        # Try standard JSON array first
        try:
            return pd.read_json(path)
        except ValueError:
            # Retry with newline-delimited JSON
            return pd.read_json(path, lines=True)
    else:
        raise ValueError(f"Unsupported file extension: {extension}. Supported: .csv, .json")


def write_parquet(df: pd.DataFrame, path: str) -> None:
    """
    Write DataFrame to Parquet file.
    
    Args:
        df: DataFrame to write
        path: Output file path
    """
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def copy_raw_file(src_path: str, dest_path: str) -> None:
    """
    Copy raw file to destination (for immutable raw storage).
    
    Args:
        src_path: Source file path
        dest_path: Destination file path
    """
    dest_obj = Path(dest_path)
    dest_obj.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, dest_path)
