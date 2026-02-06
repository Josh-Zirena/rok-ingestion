"""Tests for leaderboard API parameter validation."""

import pytest
from src.leaderboard_api.validation import parse_params, error_response, ok_response


def test_parse_params_missing_kingdom():
    """Test that missing kingdom parameter raises ValueError."""
    event = {"queryStringParameters": {"metric": "power"}}
    
    with pytest.raises(ValueError, match="kingdom parameter is required"):
        parse_params(event)


def test_parse_params_non_digit_kingdom():
    """Test that non-digit kingdom raises ValueError."""
    event = {"queryStringParameters": {"kingdom": "abc", "metric": "power"}}
    
    with pytest.raises(ValueError, match="kingdom must be 1-6 digits"):
        parse_params(event)


def test_parse_params_kingdom_too_long():
    """Test that kingdom longer than 6 digits raises ValueError."""
    event = {"queryStringParameters": {"kingdom": "1234567", "metric": "power"}}
    
    with pytest.raises(ValueError, match="kingdom must be 1-6 digits"):
        parse_params(event)


def test_parse_params_missing_metric():
    """Test that missing metric parameter raises ValueError."""
    event = {"queryStringParameters": {"kingdom": "1234"}}
    
    with pytest.raises(ValueError, match="metric parameter is required"):
        parse_params(event)


def test_parse_params_unknown_metric():
    """Test that unknown metric raises ValueError."""
    event = {"queryStringParameters": {"kingdom": "1234", "metric": "unknown_metric"}}
    
    with pytest.raises(ValueError, match="unknown metric: unknown_metric"):
        parse_params(event)


def test_parse_params_invalid_dt():
    """Test that invalid dt format raises ValueError."""
    event = {"queryStringParameters": {"kingdom": "1234", "metric": "power", "dt": "invalid-date"}}
    
    with pytest.raises(ValueError, match="dt must be 'latest' or YYYY-MM-DD format"):
        parse_params(event)


def test_parse_params_limit_too_high():
    """Test that limit > 500 raises ValueError."""
    event = {"queryStringParameters": {"kingdom": "1234", "metric": "power", "limit": "501"}}
    
    with pytest.raises(ValueError, match="limit must be between 1 and 500"):
        parse_params(event)


def test_parse_params_limit_too_low():
    """Test that limit < 1 raises ValueError."""
    event = {"queryStringParameters": {"kingdom": "1234", "metric": "power", "limit": "0"}}
    
    with pytest.raises(ValueError, match="limit must be between 1 and 500"):
        parse_params(event)


def test_parse_params_limit_not_integer():
    """Test that non-integer limit raises ValueError."""
    event = {"queryStringParameters": {"kingdom": "1234", "metric": "power", "limit": "abc"}}
    
    with pytest.raises(ValueError, match="limit must be an integer"):
        parse_params(event)


def test_parse_params_valid_minimal():
    """Test that valid minimal params return correct defaults."""
    event = {"queryStringParameters": {"kingdom": "1234", "metric": "power"}}
    
    result = parse_params(event)
    
    assert result == {
        "kingdom": "1234",
        "metric": "power", 
        "dt": "latest",
        "limit": 100
    }


def test_parse_params_valid_complete():
    """Test that valid complete params are parsed correctly."""
    event = {"queryStringParameters": {
        "kingdom": "1234",
        "metric": "killpoints",
        "dt": "2026-01-26", 
        "limit": "50"
    }}
    
    result = parse_params(event)
    
    assert result == {
        "kingdom": "1234", 
        "metric": "killpoints",
        "dt": "2026-01-26",
        "limit": 50
    }


def test_parse_params_no_query_params():
    """Test that event with no queryStringParameters raises ValueError."""
    event = {}
    
    with pytest.raises(ValueError, match="kingdom parameter is required"):
        parse_params(event)


def test_parse_params_null_query_params():
    """Test that event with null queryStringParameters raises ValueError."""
    event = {"queryStringParameters": None}
    
    with pytest.raises(ValueError, match="kingdom parameter is required"):
        parse_params(event)


def test_error_response():
    """Test that error_response returns correct format."""
    response = error_response(400, "Test error message")
    
    assert response["statusCode"] == 400
    assert response["headers"]["Content-Type"] == "application/json"
    assert response["headers"]["Access-Control-Allow-Origin"] == "*"
    assert response["body"] == '{"error": "Test error message"}'


def test_ok_response():
    """Test that ok_response returns correct format."""
    payload = {"kingdom": "1234", "metric": "power", "rows": []}
    response = ok_response(payload)
    
    assert response["statusCode"] == 200
    assert response["headers"]["Content-Type"] == "application/json"  
    assert response["headers"]["Access-Control-Allow-Origin"] == "*"
    
    import json
    body_data = json.loads(response["body"])
    assert body_data == payload