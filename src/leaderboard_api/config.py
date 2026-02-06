"""Configuration management for the leaderboard API."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration settings for the leaderboard API."""
    
    athena_database: str
    athena_table: str
    athena_results_s3: str
    aws_region: str
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables with defaults."""
        athena_results_s3 = os.getenv(
            "ATHENA_RESULTS_S3", 
            "s3://rok-ingestion-full-octopus/athena-results/"
        )
        
        if not athena_results_s3:
            raise ValueError("ATHENA_RESULTS_S3 environment variable is required")
        
        return cls(
            athena_database=os.getenv("ATHENA_DATABASE", "rok_ingestion_data"),
            athena_table=os.getenv("ATHENA_TABLE", "rok_players_curated"),
            athena_results_s3=athena_results_s3,
            aws_region=os.getenv("AWS_REGION", "us-east-1")
        )