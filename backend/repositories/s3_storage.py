import boto3


class S3Handler:
    """A class to handle S3 operations."""

    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, bucket_name: str):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.bucket_name = bucket_name

    def upload_file(self, file_name: str, body: str) -> str:
        """Upload a file to the S3 bucket."""
        s3 = boto3.client(
            "s3", aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key
        )

        s3.put_object(Bucket=self.bucket_name, Key=file_name, Body=body)
        return f"File {file_name} uploaded to {self.bucket_name}"

    def list_files(self) -> list[str]:
        """List all files in the bucket. Include the file size in bytes."""
        s3 = boto3.client(
            "s3", aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key
        )
        response = s3.list_objects_v2(Bucket=self.bucket_name)
        return [f"{obj['Key']} - {obj['Size']} bytes" for obj in response["Contents"]]

    def download_file(self, file_name: str) -> str:
        """Download a file from the S3 bucket."""
        s3 = boto3.client(
            "s3", aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key
        )
        response = s3.get_object(Bucket=self.bucket_name, Key=file_name)
        return response["Body"].read().decode("utf-8")

    def delete_file(self, file_name: str) -> str:
        """Delete a file from the S3 bucket."""
        s3 = boto3.client(
            "s3", aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key
        )
        s3.delete_object(Bucket=self.bucket_name, Key=file_name)
        return f"File {file_name} deleted from {self.bucket_name}"
