"""Main AWS Lambda handler for player data ingestion."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote_plus

import pandas as pd

from .aws_s3 import download_s3_object, upload_bytes_to_s3, upload_file_to_s3
from .hashing import add_ingestion_metadata, add_record_hash
from .normalize import normalize_df
from .s3_paths import build_curated_key, build_raw_key, parse_inbox_key
from .validation import validate_required_columns, validate_unique_id


def lambda_handler(event, context):
    """
    AWS Lambda entrypoint for S3 event processing.
    
    Args:
        event: S3 event containing bucket and object key
        context: Lambda context object
    
    Returns:
        Dict with statusCode and body
    """
    try:
        # Parse S3 event
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])
        
        # Process the ingestion
        summary = process_s3_ingestion(bucket, key)
        
        return {
            "statusCode": 200,
            "body": json.dumps(summary)
        }
    except Exception as e:
        print(f"Error processing S3 event: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


def process_s3_ingestion(bucket: str, key: str) -> dict:
    """
    Process an S3 ingestion event.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key (URL-decoded)
    
    Returns:
        Dict with processing summary
    """
    print(f"Processing s3://{bucket}/{key}")
    
    # Parse the inbox key to extract metadata
    key_info = parse_inbox_key(key)
    source = key_info["source"]
    kingdom = key_info["kingdom"]
    dt = key_info["dt"]
    filename = key_info["filename"]
    
    # Download file to /tmp
    tmp_input = f"/tmp/{filename}"
    download_s3_object(bucket, key, tmp_input)
    
    # Parse based on extension
    if key_info["ext"] == "csv":
        df = pd.read_csv(tmp_input)
    elif key_info["ext"] == "json":
        df = pd.read_json(tmp_input)
    else:
        raise ValueError(f"Unsupported file type: {key_info['ext']}")
    
    # Normalize column names
    df.columns = df.columns.str.lower()
    
    # Validate
    validate_required_columns(df)
    validate_unique_id(df)
    
    # Normalize data
    df = normalize_df(df, kingdom, dt)
    
    # Add metadata
    df = add_ingestion_metadata(df)
    df = add_record_hash(df)
    
    # Generate run timestamp
    run_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    
    # Build S3 keys
    raw_key = build_raw_key(source, kingdom, dt, run_ts, filename)
    curated_key = build_curated_key(source, kingdom, dt)
    
    # Upload raw file to raw prefix
    upload_file_to_s3(tmp_input, bucket, raw_key)
    
    # Write curated parquet to /tmp and upload
    tmp_parquet = f"/tmp/curated_{run_ts}.parquet"
    df.to_parquet(tmp_parquet, index=False)
    upload_file_to_s3(tmp_parquet, bucket, curated_key)
    
    # Clean up temp files
    os.remove(tmp_input)
    os.remove(tmp_parquet)
    
    result = {
        "kingdom": kingdom,
        "dt": dt,
        "run_ts": run_ts,
        "rows": len(df),
        "raw_key": raw_key,
        "curated_key": curated_key,
    }
    
    print(f"Ingestion complete: {json.dumps(result)}")
    return result


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
