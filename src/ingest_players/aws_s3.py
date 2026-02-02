"""AWS S3 helper functions for file operations."""

import boto3

s3_client = boto3.client("s3")


def download_s3_object(bucket: str, key: str, local_path: str) -> None:
    """
    Download an S3 object to a local file.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
        local_path: Local file path to save to
    """
    s3_client.download_file(bucket, key, local_path)


def upload_file_to_s3(local_path: str, bucket: str, key: str) -> None:
    """
    Upload a local file to S3.
    
    Args:
        local_path: Local file path to upload
        bucket: S3 bucket name
        key: S3 object key
    """
    s3_client.upload_file(local_path, bucket, key)


def upload_bytes_to_s3(data_bytes: bytes, bucket: str, key: str) -> None:
    """
    Upload bytes directly to S3.
    
    Args:
        data_bytes: Bytes to upload
        bucket: S3 bucket name
        key: S3 object key
    """
    s3_client.put_object(Bucket=bucket, Key=key, Body=data_bytes)
