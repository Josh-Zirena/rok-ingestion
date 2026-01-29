#!/usr/bin/env python3
"""Local runner script for testing the ingestion handler."""

import argparse
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ingest_players.handler import process_ingestion


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Local ingestion runner for RoK player data"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Local file path to CSV or JSON file"
    )
    parser.add_argument(
        "--kingdom",
        required=True,
        help="Kingdom identifier (e.g., '51')"
    )
    parser.add_argument(
        "--dt",
        required=True,
        help="Date in YYYY-MM-DD format (e.g., '2026-01-26')"
    )
    parser.add_argument(
        "--out-dir",
        default="local_out",
        help="Output directory (default: local_out)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ROK Ingestion - Local Runner")
    print("=" * 60)
    print(f"Input: {args.input}")
    print(f"Kingdom: {args.kingdom}")
    print(f"Date: {args.dt}")
    print(f"Output: {args.out_dir}")
    print("=" * 60)
    print()
    
    try:
        result = process_ingestion(args.input, args.kingdom, args.dt, args.out_dir)
        print()
        print("✓ Ingestion completed successfully!")
        print()
        print("Summary:")
        print(json.dumps(result, indent=2))
    except NotImplementedError:
        print("✗ process_ingestion() not yet implemented (Step 1 stub)")
        return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
