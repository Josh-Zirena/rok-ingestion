"""Lambda handler for the leaderboard API."""

import json
from typing import Dict, Any, Optional

from config import Config
from metrics import get_metric_column
from validation import parse_params, error_response, ok_response, options_response
from sql import sql_latest_dt, sql_leaderboard
from athena import start_query, wait_for_query, get_results


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda handler for leaderboard API requests.
    
    Args:
        event: API Gateway HTTP API event
        context: Lambda context object
        
    Returns:
        API Gateway response dict
    """
    try:
        # Handle CORS preflight requests
        request_context = event.get("requestContext", {})
        http_context = request_context.get("http", {})
        method = http_context.get("method", "")
        path = http_context.get("path", "")
        
        if method == "OPTIONS":
            return options_response()
        
        # Route to appropriate handler
        if path == "/health":
            return handle_health_check(context)
        elif path == "/leaderboard":
            return handle_leaderboard(event, context)
        else:
            return error_response(404, "Not found")
        
    except Exception as e:
        # Log error with request ID if available
        request_id = getattr(context, 'aws_request_id', 'unknown')
        print(f"Error processing request {request_id}: {e}")
        return error_response(500, "Internal server error")


def handle_health_check(context: Any) -> Dict[str, Any]:
    """Handle health check requests.
    
    Args:
        context: Lambda context object
        
    Returns:
        API Gateway response dict
    """
    response_data = {
        "status": "healthy",
        "service": "leaderboard-api",
        "version": "1.0.0",
        "request_id": getattr(context, 'aws_request_id', None)
    }
    
    return ok_response(response_data)


def handle_leaderboard(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle leaderboard query requests.
    
    Args:
        event: API Gateway HTTP API event
        context: Lambda context object
        
    Returns:
        API Gateway response dict
    """
    try:
        # Load configuration
        config = Config.from_env()
        
        # Parse and validate request parameters
        params = parse_params(event)
        kingdom = params["kingdom"]
        metric = params["metric"] 
        dt = params["dt"]
        limit = params["limit"]
        
        print(f"Leaderboard request: kingdom={kingdom}, metric={metric}, dt={dt}, limit={limit}")
        
        # Get the metric column name
        metric_column = get_metric_column(metric)
        
        resolved_dt = dt
        
        # If dt is "latest", resolve it to the actual latest date
        if dt == "latest":
            latest_sql = sql_latest_dt(config.athena_database, config.athena_table, kingdom)
            
            latest_qid = start_query(
                latest_sql, 
                config.athena_database, 
                config.athena_results_s3, 
                config.aws_region
            )
            print(f"Latest dt query execution ID: {latest_qid}")
            
            wait_for_query(latest_qid, config.aws_region)
            latest_results = get_results(latest_qid, config.aws_region)
            
            if not latest_results or not latest_results[0].get("dt"):
                return error_response(404, f"No data found for kingdom {kingdom}")
            
            resolved_dt = latest_results[0]["dt"]
            print(f"Resolved latest dt to: {resolved_dt}")
        
        # Execute leaderboard query
        leaderboard_sql = sql_leaderboard(
            config.athena_database,
            config.athena_table, 
            kingdom,
            resolved_dt,
            metric_column,
            limit
        )
        
        leaderboard_qid = start_query(
            leaderboard_sql,
            config.athena_database,
            config.athena_results_s3, 
            config.aws_region
        )
        print(f"Leaderboard query execution ID: {leaderboard_qid}")
        
        wait_for_query(leaderboard_qid, config.aws_region)
        rows = get_results(leaderboard_qid, config.aws_region)
        
        # Return successful response
        response_data = {
            "kingdom": kingdom,
            "dt": resolved_dt,
            "metric": metric,
            "limit": limit,
            "rows": rows
        }
        
        return ok_response(response_data)
        
    except ValueError as e:
        # Validation errors
        print(f"Validation error: {e}")
        return error_response(400, str(e))
        
    except Exception as e:
        # Log error with request ID if available
        request_id = getattr(context, 'aws_request_id', 'unknown')
        print(f"Error processing request {request_id}: {e}")
        return error_response(500, "Internal server error")