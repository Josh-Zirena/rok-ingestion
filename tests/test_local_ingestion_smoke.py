"""End-to-end smoke test for local ingestion."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from ingest_players.handler import process_ingestion


def test_local_ingestion_csv_smoke():
    """Test complete ingestion pipeline with a CSV file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create a test CSV file
        test_data = pd.DataFrame({
            "id": ["player1", "player2", "player3"],
            "name": ["Alice", "Bob", "Charlie"],
            "dkp": [1000, 2000, 1500],
            "kills": [50, 75, 60],
        })
        
        input_csv = tmpdir / "test_players.csv"
        test_data.to_csv(input_csv, index=False)
        
        out_dir = tmpdir / "output"
        
        # Run ingestion
        result = process_ingestion(
            input_path=str(input_csv),
            kingdom="51",
            dt="2026-01-26",
            out_dir=str(out_dir)
        )
        
        # Verify result summary
        assert result["kingdom"] == "51"
        assert result["dt"] == "2026-01-26"
        assert result["rows"] == 3
        assert "run_ts" in result
        assert "raw_path" in result
        assert "curated_path" in result
        
        # Verify raw file was copied
        raw_path = Path(result["raw_path"])
        assert raw_path.exists()
        assert raw_path.name == "test_players.csv"
        
        # Verify curated parquet was created
        curated_path = Path(result["curated_path"])
        assert curated_path.exists()
        assert curated_path.name == "players.parquet"
        
        # Read curated parquet and verify columns
        df_curated = pd.read_parquet(curated_path)
        
        # Check expected columns
        expected_cols = {
            "id", "name", "dkp", "kills",  # Original
            "kingdom", "snapshot_date",  # Normalized
            "ingested_at", "run_id", "record_hash",  # Metadata
        }
        assert set(df_curated.columns) == expected_cols
        
        # Verify metadata values
        assert (df_curated["kingdom"] == "51").all()
        assert (df_curated["snapshot_date"] == "2026-01-26").all()
        assert df_curated["run_id"].nunique() == 1  # Same run_id for all rows
        assert df_curated["record_hash"].nunique() == 3  # Unique hash per row
        
        # Verify id normalization (string type, trimmed)
        assert pd.api.types.is_string_dtype(df_curated["id"])
        assert list(df_curated["id"]) == ["player1", "player2", "player3"]


def test_local_ingestion_json_smoke():
    """Test complete ingestion pipeline with a JSON file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create a test JSON file
        test_data = [
            {"id": "player1", "name": "Alice", "dkp": 1000},
            {"id": "player2", "name": "Bob", "dkp": 2000},
        ]
        
        input_json = tmpdir / "test_players.json"
        pd.DataFrame(test_data).to_json(input_json, orient="records")
        
        out_dir = tmpdir / "output"
        
        # Run ingestion
        result = process_ingestion(
            input_path=str(input_json),
            kingdom="99",
            dt="2026-01-27",
            out_dir=str(out_dir)
        )
        
        # Verify basic result
        assert result["rows"] == 2
        assert Path(result["curated_path"]).exists()
        
        # Verify curated data
        df = pd.read_parquet(result["curated_path"])
        assert len(df) == 2
        assert "record_hash" in df.columns
        assert "run_id" in df.columns


def test_validation_missing_id():
    """Test that validation fails when id column is missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create CSV without id column
        test_data = pd.DataFrame({
            "name": ["Alice", "Bob"],
            "dkp": [1000, 2000],
        })
        
        input_csv = tmpdir / "bad.csv"
        test_data.to_csv(input_csv, index=False)
        
        out_dir = tmpdir / "output"
        
        # Expect validation error
        with pytest.raises(ValueError, match="Missing required columns"):
            process_ingestion(
                input_path=str(input_csv),
                kingdom="51",
                dt="2026-01-26",
                out_dir=str(out_dir)
            )


def test_validation_duplicate_id():
    """Test that validation fails when id has duplicates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create CSV with duplicate ids
        test_data = pd.DataFrame({
            "id": ["player1", "player2", "player1"],  # duplicate
            "dkp": [1000, 2000, 1500],
        })
        
        input_csv = tmpdir / "bad.csv"
        test_data.to_csv(input_csv, index=False)
        
        out_dir = tmpdir / "output"
        
        # Expect validation error
        with pytest.raises(ValueError, match="duplicate values"):
            process_ingestion(
                input_path=str(input_csv),
                kingdom="51",
                dt="2026-01-26",
                out_dir=str(out_dir)
            )
