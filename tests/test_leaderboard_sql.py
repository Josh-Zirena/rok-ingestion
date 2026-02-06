"""Tests for SQL query generation."""

import pytest
from src.leaderboard_api.sql import quote_ident, sql_latest_dt, sql_leaderboard


def test_quote_ident_simple():
    """Test that simple identifiers don't get quoted."""
    assert quote_ident("killpoints") == "killpoints"
    assert quote_ident("power") == "power"
    assert quote_ident("player_id") == "player_id"


def test_quote_ident_with_spaces():
    """Test that identifiers with spaces get quoted."""
    assert quote_ident("t1 kills") == '"t1 kills"'
    assert quote_ident("total kills") == '"total kills"'
    assert quote_ident("rss gathered") == '"rss gathered"'


def test_quote_ident_with_special_chars():
    """Test that identifiers with special characters get quoted."""
    assert quote_ident("player-name") == '"player-name"'
    assert quote_ident("kills/deaths") == '"kills/deaths"'
    assert quote_ident("power%") == '"power%"'


def test_quote_ident_with_embedded_quotes():
    """Test that embedded quotes are escaped."""
    assert quote_ident('name with "quotes"') == '"name with ""quotes"""'


def test_sql_latest_dt():
    """Test SQL generation for latest dt query."""
    sql = sql_latest_dt("rok_ingestion_data", "rok_players_curated", "1234")
    
    expected = """SELECT max(dt) AS dt
FROM rok_ingestion_data.rok_players_curated
WHERE kingdom = '1234'"""
    
    assert sql == expected


def test_sql_leaderboard_simple_metric():
    """Test leaderboard SQL with simple metric (no spaces)."""
    sql = sql_leaderboard(
        db="rok_ingestion_data",
        table="rok_players_curated", 
        kingdom="1234",
        dt="2026-01-26",
        metric_column="power",
        limit=100
    )
    
    expected = """SELECT id, name, power AS value
FROM rok_ingestion_data.rok_players_curated
WHERE kingdom='1234' AND dt='2026-01-26'
ORDER BY power DESC
LIMIT 100"""
    
    assert sql == expected


def test_sql_leaderboard_metric_with_spaces():
    """Test leaderboard SQL with metric containing spaces."""
    sql = sql_leaderboard(
        db="rok_ingestion_data", 
        table="rok_players_curated",
        kingdom="1234",
        dt="2026-01-26",
        metric_column="t1 kills",
        limit=50
    )
    
    expected = """SELECT id, name, "t1 kills" AS value
FROM rok_ingestion_data.rok_players_curated
WHERE kingdom='1234' AND dt='2026-01-26'
ORDER BY "t1 kills" DESC
LIMIT 50"""
    
    assert sql == expected


def test_sql_leaderboard_includes_order_by_quoted():
    """Test that ORDER BY clause uses quoted column when metric has spaces."""
    sql = sql_leaderboard(
        db="test_db",
        table="test_table", 
        kingdom="999",
        dt="2026-01-01",
        metric_column="total kills",
        limit=10
    )
    
    # Both SELECT and ORDER BY should use quoted column
    assert '"total kills" AS value' in sql
    assert 'ORDER BY "total kills" DESC' in sql


def test_sql_leaderboard_references_correct_database_table():
    """Test that SQL references the correct database and table."""
    sql = sql_leaderboard(
        db="rok_ingestion_data",
        table="rok_players_curated",
        kingdom="1234", 
        dt="2026-01-26",
        metric_column="power",
        limit=100
    )
    
    assert "FROM rok_ingestion_data.rok_players_curated" in sql