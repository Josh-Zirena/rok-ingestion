"""Request validation and response formatting for the leaderboard API."""

import re
from typing import Dict, Any, Optional

from metrics import is_valid_metric


def parse_params(event: Dict[str, Any]) -> Dict[str, Any]:
    """Parse and validate parameters from an API Gateway event.
    
    Args:
        event: API Gateway HTTP API event
        
    Returns:
        Normalized parameters dict with keys: kingdom, metric, dt, limit
        
    Raises:
        ValueError: If any parameter is invalid
    """
    query_params = event.get("queryStringParameters", {}) or {}
    
    # Extract and validate kingdom (required)
    kingdom = query_params.get("kingdom")
    if not kingdom:
        raise ValueError("kingdom parameter is required")
    
    if not re.match(r"^\d{1,6}$", kingdom):
        raise ValueError("kingdom must be 1-6 digits")
    
    # Extract and validate metric (required)
    metric = query_params.get("metric")
    if not metric:
        raise ValueError("metric parameter is required")
    
    if not is_valid_metric(metric):
        raise ValueError(f"unknown metric: {metric}")
    
    # Extract and validate dt (optional, defaults to "latest")
    dt = query_params.get("dt", "latest")
    if dt != "latest" and not re.match(r"^\d{4}-\d{2}-\d{2}$", dt):
        raise ValueError("dt must be 'latest' or YYYY-MM-DD format")
    
    # Extract and validate limit (optional, defaults to 100)
    limit_str = query_params.get("limit", "100")
    try:
        limit = int(limit_str)
    except ValueError:
        raise ValueError("limit must be an integer")
    
    if limit < 1 or limit > 500:
        raise ValueError("limit must be between 1 and 500")
    
    return {
        "kingdom": kingdom,
        "metric": metric, 
        "dt": dt,
        "limit": limit
    }


def get_cors_headers() -> Dict[str, str]:
    """Get comprehensive CORS headers for API responses.
    
    Returns:
        Dict of CORS headers
    """
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Max-Age": "300"
    }


def error_response(status: int, message: str) -> Dict[str, Any]:
    """Create an error response for API Gateway.
    
    Args:
        status: HTTP status code
        message: Error message
        
    Returns:
        API Gateway response dict
    """
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            **get_cors_headers()
        },
        "body": f'{{"error": "{message}"}}'
    }


def ok_response(payload_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Create a success response for API Gateway.
    
    Args:
        payload_dict: Response payload to serialize as JSON
        
    Returns:
        API Gateway response dict
    """
    import json
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            **get_cors_headers()
        },
        "body": json.dumps(payload_dict)
    }


def options_response() -> Dict[str, Any]:
    """Handle CORS preflight requests.
    
    Returns:
        API Gateway response dict for OPTIONS requests
    """
    return {
        "statusCode": 200,
        "headers": get_cors_headers(),
        "body": ""
    }