"""S3 path parsing utilities."""

import re
from pathlib import Path


def parse_inbox_key(key: str) -> dict:
    """
    Parse an S3 inbox key and extract metadata.
    
    Expected format:
        inbox/source=<source>/kingdom=<kingdom>/dt=<dt>/<filename>
    
    Example:
        inbox/source=rok_players/kingdom=51/dt=2026-01-26/players.csv
    
    Args:
        key: S3 key string to parse
    
    Returns:
        Dictionary with keys: source, kingdom, dt, filename, ext
    
    Raises:
        ValueError: If key format is invalid, dt format is wrong, or extension unsupported
    """
    # Validate key starts with "inbox/"
    if not key.startswith("inbox/"):
        raise ValueError(f"Key must start with 'inbox/', got: {key}")
    
    # Split the key into parts
    parts = key.split("/")
    
    # Parse key-value segments (all parts between "inbox" and filename)
    segments = {}
    for part in parts[1:]:  # Skip "inbox"
        if "=" in part:
            k, v = part.split("=", 1)
            segments[k] = v
    
    # Validate required segments exist
    if "source" not in segments:
        raise ValueError(f"Key missing 'source=' segment: {key}")
    if "kingdom" not in segments:
        raise ValueError(f"Key missing 'kingdom=' segment: {key}")
    if "dt" not in segments:
        raise ValueError(f"Key missing 'dt=' segment: {key}")
    
    # Validate dt format (YYYY-MM-DD)
    dt = segments["dt"]
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", dt):
        raise ValueError(f"Invalid dt format (expected YYYY-MM-DD): {dt}")
    
    # Extract filename and extension
    filename = parts[-1]
    if not filename:
        raise ValueError(f"Key must end with a filename: {key}")
    
    path_obj = Path(filename)
    ext = path_obj.suffix.lstrip(".").lower()
    
    if not ext:
        raise ValueError(f"Filename must have an extension: {filename}")
    
    # Validate extension is csv or json
    if ext not in ("csv", "json"):
        raise ValueError(f"Unsupported file extension (must be csv or json): {ext}")
    
    return {
        "source": segments["source"],
        "kingdom": segments["kingdom"],
        "dt": dt,
        "filename": filename,
        "ext": ext,
    }


def build_raw_key(source: str, kingdom: str, dt: str, run_ts: str, filename: str) -> str:
    """
    Build an S3 key for the raw storage tier.
    
    Format:
        raw/source=<source>/kingdom=<kingdom>/dt=<dt>/run_ts=<run_ts>/<filename>
    
    Args:
        source: Source name (e.g., "rok_players")
        kingdom: Kingdom identifier (e.g., "51")
        dt: Date in YYYY-MM-DD format
        run_ts: Run timestamp (e.g., "20260126T153012Z")
        filename: Filename to store
    
    Returns:
        S3 key string
    
    Raises:
        ValueError: If run_ts is empty
    """
    if not run_ts:
        raise ValueError("run_ts must be non-empty")
    
    return f"raw/source={source}/kingdom={kingdom}/dt={dt}/run_ts={run_ts}/{filename}"


def build_curated_key(source: str, kingdom: str, dt: str) -> str:
    """
    Build an S3 key for the curated storage tier (Parquet format).
    
    Format:
        curated/source=<source>/kingdom=<kingdom>/dt=<dt>/players.parquet
    
    Args:
        source: Source name (e.g., "rok_players")
        kingdom: Kingdom identifier (e.g., "51")
        dt: Date in YYYY-MM-DD format
    
    Returns:
        S3 key string
    """
    return f"curated/source={source}/kingdom={kingdom}/dt={dt}/players.parquet"
