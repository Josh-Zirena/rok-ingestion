"""Metric definitions and registry for leaderboard queries."""

from typing import Dict, Any

# Registry of available metrics for leaderboard queries
# Each entry maps a metric key to its Athena column name and human-readable label
METRICS: Dict[str, Dict[str, str]] = {
    "power": {
        "column": "power",
        "label": "Power"
    },
    "killpoints": {
        "column": "killpoints", 
        "label": "Kill Points"
    },
    "deads": {
        "column": "deads",
        "label": "Deaths"
    },
    "total_kills": {
        "column": "total kills",
        "label": "Total Kills"
    },
    "t1_kills": {
        "column": "t1 kills",
        "label": "T1 Kills"
    },
    "t2_kills": {
        "column": "t2 kills", 
        "label": "T2 Kills"
    },
    "t3_kills": {
        "column": "t3 kills",
        "label": "T3 Kills"
    },
    "t4_kills": {
        "column": "t4 kills",
        "label": "T4 Kills"
    },
    "t5_kills": {
        "column": "t5 kills",
        "label": "T5 Kills"
    },
    "t45_kills": {
        "column": "t45 kills",
        "label": "T4+T5 Kills"
    },
    "rss_gathered": {
        "column": "rss gathered",
        "label": "RSS Gathered"
    },
    "rss_assistance": {
        "column": "rss assistance",
        "label": "RSS Assistance"
    },
    "helps": {
        "column": "helps",
        "label": "Helps"
    },
    "ranged": {
        "column": "ranged",
        "label": "Ranged"
    }
}


def get_metric_column(metric_key: str) -> str:
    """Get the Athena column name for a metric key.
    
    Args:
        metric_key: The metric key to lookup
        
    Returns:
        The Athena column name
        
    Raises:
        KeyError: If metric key is not found
    """
    return METRICS[metric_key]["column"]


def is_valid_metric(metric_key: str) -> bool:
    """Check if a metric key is valid.
    
    Args:
        metric_key: The metric key to validate
        
    Returns:
        True if the metric key exists in the registry
    """
    return metric_key in METRICS