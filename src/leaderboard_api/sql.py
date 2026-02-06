"""SQL query generation for Athena leaderboard queries."""

import re


def quote_ident(name: str) -> str:
    """Quote an identifier if it contains non-alphanumeric characters.
    
    Args:
        name: Column or table name to potentially quote
        
    Returns:
        Quoted identifier if needed, otherwise the original name
    """
    # If name contains anything other than letters, numbers, underscores, quote it
    if re.search(r'[^a-zA-Z0-9_]', name):
        # Escape any embedded double quotes by doubling them
        escaped_name = name.replace('"', '""')
        return f'"{escaped_name}"'
    return name


def sql_latest_dt(db: str, table: str, kingdom: str) -> str:
    """Generate SQL to find the latest dt for a kingdom.
    
    Args:
        db: Athena database name
        table: Athena table name  
        kingdom: Kingdom ID (already validated)
        
    Returns:
        SQL query string
    """
    return f"""SELECT max(dt) AS dt
FROM {db}.{table}
WHERE kingdom = '{kingdom}'"""


def sql_leaderboard(
    db: str, 
    table: str, 
    kingdom: str, 
    dt: str, 
    metric_column: str, 
    limit: int
) -> str:
    """Generate SQL for leaderboard query.
    
    Args:
        db: Athena database name
        table: Athena table name
        kingdom: Kingdom ID (already validated)
        dt: Date string (already validated) 
        metric_column: Column name for the metric (may contain spaces)
        limit: Result limit (already validated)
        
    Returns:
        SQL query string
    """
    quoted_metric = quote_ident(metric_column)
    
    return f"""SELECT id, name, {quoted_metric} AS value
FROM {db}.{table}
WHERE kingdom='{kingdom}' AND dt='{dt}'
ORDER BY {quoted_metric} DESC
LIMIT {limit}"""