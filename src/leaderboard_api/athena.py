"""Athena query execution and result processing."""

import time
from typing import Dict, List, Any, Optional
import boto3


def start_query(sql: str, database: str, results_s3: str, region: str) -> str:
    """Start an Athena query execution.
    
    Args:
        sql: SQL query to execute
        database: Athena database name
        results_s3: S3 location for query results
        region: AWS region
        
    Returns:
        Query execution ID
        
    Raises:
        Exception: If query fails to start
    """
    athena = boto3.client("athena", region_name=region)
    
    response = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={'Database': database},
        ResultConfiguration={'OutputLocation': results_s3}
    )
    
    return response['QueryExecutionId']


def wait_for_query(qid: str, region: str, timeout_seconds: int = 30) -> Dict[str, Any]:
    """Wait for an Athena query to complete.
    
    Args:
        qid: Query execution ID
        region: AWS region  
        timeout_seconds: Maximum time to wait
        
    Returns:
        Final query execution state dict
        
    Raises:
        TimeoutError: If query doesn't complete within timeout
        Exception: If query fails
    """
    athena = boto3.client("athena", region_name=region)
    
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        response = athena.get_query_execution(QueryExecutionId=qid)
        execution = response['QueryExecution']
        state = execution['Status']['State']
        
        if state == 'SUCCEEDED':
            return execution
        elif state in ['FAILED', 'CANCELLED']:
            reason = execution['Status'].get('StateChangeReason', 'Unknown error')
            raise Exception(f"Query {state.lower()}: {reason}")
        
        time.sleep(1)
    
    raise TimeoutError(f"Query {qid} did not complete within {timeout_seconds} seconds")


def get_results(qid: str, region: str) -> List[Dict[str, Any]]:
    """Get results from a completed Athena query.
    
    Args:
        qid: Query execution ID
        region: AWS region
        
    Returns:
        List of result rows as dictionaries
    """
    athena = boto3.client("athena", region_name=region)
    
    response = athena.get_query_results(QueryExecutionId=qid)
    
    # Get column names from ResultSetMetadata
    result_set = response['ResultSet']
    if not result_set['Rows']:
        return []
    
    # Column info is in ResultSetMetadata
    metadata = result_set.get('ResultSetMetadata', {})
    column_info = metadata.get('ColumnInfo', [])
    column_names = [col['Name'] for col in column_info]
    
    # Convert data rows to dictionaries
    results = []
    data_rows = result_set['Rows'][1:]  # Skip header row
    
    for row in data_rows:
        row_dict = {}
        for i, col_name in enumerate(column_names):
            if i < len(row['Data']):
                cell = row['Data'][i]
                value = cell.get('VarCharValue', '')
                
                # Convert 'value' column to int when possible
                if col_name == 'value' and value:
                    try:
                        row_dict[col_name] = int(value)
                    except ValueError:
                        row_dict[col_name] = None
                else:
                    row_dict[col_name] = value if value else None
            else:
                row_dict[col_name] = None
        
        results.append(row_dict)
    
    return results