"""Main AWS Lambda handler for player data ingestion."""

from datetime import datetime, timezone
from pathlib import Path

from .hashing import add_ingestion_metadata, add_record_hash
from .io_local import copy_raw_file, read_input_file, write_parquet
from .normalize import normalize_df
from .validation import validate_required_columns, validate_unique_id


def lambda_handler(event, context):
    """
    AWS Lambda entrypoint.
    Will parse S3 event, call processing, write outputs.
    """
    raise NotImplementedError("AWS Lambda integration will be implemented in a later step")


def process_ingestion(input_path: str, kingdom: str, dt: str, out_dir: str = "local_out") -> dict:
    """
    Local-friendly entrypoint used by scripts/run_local.py.
    
    Args:
        input_path: Local file path to CSV or JSON
        kingdom: Kingdom identifier
        dt: Date string (YYYY-MM-DD)
        out_dir: Output directory (default: "local_out")
        
    Returns:
        Dictionary with ingestion summary
    """
    # Step 1: Read input file
    df = read_input_file(input_path)
    
    # Step 1b: Normalize column names to lowercase
    df.columns = df.columns.str.lower()
    
    # Step 2: Validate required columns
    validate_required_columns(df)
    
    # Step 3: Validate unique id
    validate_unique_id(df)
    
    # Step 4: Normalize data
    df = normalize_df(df, kingdom, dt)
    
    # Step 5: Add ingestion metadata
    df = add_ingestion_metadata(df)
    
    # Step 6: Add record hash
    df = add_record_hash(df)
    
    # Step 7: Compute run_ts
    run_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    
    # Step 8: Create output paths (mirror S3 conventions)
    input_filename = Path(input_path).name
    
    raw_path = (
        f"{out_dir}/raw/source=rok_players/"
        f"kingdom={kingdom}/dt={dt}/run_ts={run_ts}/{input_filename}"
    )
    
    curated_path = (
        f"{out_dir}/curated/source=rok_players/"
        f"kingdom={kingdom}/dt={dt}/players.parquet"
    )
    
    # Step 9: Copy raw file
    copy_raw_file(input_path, raw_path)
    
    # Step 10: Write curated parquet
    write_parquet(df, curated_path)
    
    # Step 11: Return summary
    return {
        "kingdom": kingdom,
        "dt": dt,
        "run_ts": run_ts,
        "rows": len(df),
        "raw_path": raw_path,
        "curated_path": curated_path,
    }
