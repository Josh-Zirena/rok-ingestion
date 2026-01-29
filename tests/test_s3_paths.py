"""Unit tests for S3 path parsing."""

import pytest

from ingest_players.s3_paths import (
    parse_inbox_key,
    build_raw_key,
    build_curated_key,
)


class TestParseInboxKey:
    """Tests for parse_inbox_key function."""
    
    def test_parse_rok_players_csv(self):
        """Test parsing inbox/source=rok_players/kingdom=51/dt=2026-01-26/players.csv"""
        key = "inbox/source=rok_players/kingdom=51/dt=2026-01-26/players.csv"
        result = parse_inbox_key(key)
        
        assert result["source"] == "rok_players"
        assert result["kingdom"] == "51"
        assert result["dt"] == "2026-01-26"
        assert result["filename"] == "players.csv"
        assert result["ext"] == "csv"
    
    def test_parse_rok_players_json(self):
        """Test parsing inbox/source=rok_players/kingdom=50/dt=2026-01-26/players.json"""
        key = "inbox/source=rok_players/kingdom=50/dt=2026-01-26/players.json"
        result = parse_inbox_key(key)
        
        assert result["source"] == "rok_players"
        assert result["kingdom"] == "50"
        assert result["dt"] == "2026-01-26"
        assert result["filename"] == "players.json"
        assert result["ext"] == "json"
    
    def test_missing_inbox_prefix(self):
        """Test that missing inbox/ prefix raises ValueError"""
        key = "source=rok_players/kingdom=51/dt=2026-01-26/players.csv"
        with pytest.raises(ValueError, match="must start with 'inbox/'"):
            parse_inbox_key(key)
    
    def test_missing_dt_segment(self):
        """Test that missing dt segment raises ValueError"""
        key = "inbox/source=rok_players/kingdom=51/players.csv"
        with pytest.raises(ValueError, match="missing 'dt=' segment"):
            parse_inbox_key(key)
    
    def test_invalid_dt_format_slashes(self):
        """Test that dt with slashes instead of dashes raises ValueError"""
        key = "inbox/source=rok_players/kingdom=51/dt=2026/01/26/players.csv"
        with pytest.raises(ValueError, match="Invalid dt format"):
            parse_inbox_key(key)
    
    def test_invalid_dt_format_wrong_pattern(self):
        """Test that dt with wrong pattern raises ValueError"""
        key = "inbox/source=rok_players/kingdom=51/dt=26-01-2026/players.csv"
        with pytest.raises(ValueError, match="Invalid dt format"):
            parse_inbox_key(key)
    
    def test_unsupported_extension_txt(self):
        """Test that .txt extension raises ValueError"""
        key = "inbox/source=rok_players/kingdom=51/dt=2026-01-26/players.txt"
        with pytest.raises(ValueError, match="Unsupported file extension"):
            parse_inbox_key(key)
    
    def test_unsupported_extension_parquet(self):
        """Test that .parquet extension raises ValueError"""
        key = "inbox/source=rok_players/kingdom=51/dt=2026-01-26/players.parquet"
        with pytest.raises(ValueError, match="Unsupported file extension"):
            parse_inbox_key(key)
    
    def test_missing_filename(self):
        """Test that missing filename raises ValueError"""
        key = "inbox/source=rok_players/kingdom=51/dt=2026-01-26/"
        with pytest.raises(ValueError, match="must end with a filename"):
            parse_inbox_key(key)
    
    def test_missing_source_segment(self):
        """Test that missing source segment raises ValueError"""
        key = "inbox/kingdom=51/dt=2026-01-26/players.csv"
        with pytest.raises(ValueError, match="missing 'source=' segment"):
            parse_inbox_key(key)
    
    def test_missing_kingdom_segment(self):
        """Test that missing kingdom segment raises ValueError"""
        key = "inbox/source=rok_players/dt=2026-01-26/players.csv"
        with pytest.raises(ValueError, match="missing 'kingdom=' segment"):
            parse_inbox_key(key)


class TestBuildRawKey:
    """Tests for build_raw_key function."""
    
    def test_build_raw_key_basic(self):
        """Test building a raw key with valid inputs"""
        result = build_raw_key(
            source="rok_players",
            kingdom="51",
            dt="2026-01-26",
            run_ts="20260126T153012Z",
            filename="players.csv"
        )
        expected = "raw/source=rok_players/kingdom=51/dt=2026-01-26/run_ts=20260126T153012Z/players.csv"
        assert result == expected
    
    def test_build_raw_key_json(self):
        """Test building a raw key with JSON file"""
        result = build_raw_key(
            source="rok_players",
            kingdom="50",
            dt="2026-01-26",
            run_ts="20260126T120000Z",
            filename="players.json"
        )
        expected = "raw/source=rok_players/kingdom=50/dt=2026-01-26/run_ts=20260126T120000Z/players.json"
        assert result == expected
    
    def test_build_raw_key_empty_run_ts(self):
        """Test that empty run_ts raises ValueError"""
        with pytest.raises(ValueError, match="run_ts must be non-empty"):
            build_raw_key(
                source="rok_players",
                kingdom="51",
                dt="2026-01-26",
                run_ts="",
                filename="players.csv"
            )


class TestBuildCuratedKey:
    """Tests for build_curated_key function."""
    
    def test_build_curated_key_basic(self):
        """Test building a curated key with valid inputs"""
        result = build_curated_key(
            source="rok_players",
            kingdom="51",
            dt="2026-01-26"
        )
        expected = "curated/source=rok_players/kingdom=51/dt=2026-01-26/players.parquet"
        assert result == expected
    
    def test_build_curated_key_different_kingdom(self):
        """Test building a curated key for different kingdom"""
        result = build_curated_key(
            source="rok_players",
            kingdom="100",
            dt="2026-01-27"
        )
        expected = "curated/source=rok_players/kingdom=100/dt=2026-01-27/players.parquet"
        assert result == expected
