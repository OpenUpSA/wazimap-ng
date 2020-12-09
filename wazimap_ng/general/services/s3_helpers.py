import boto3

from wazimap_ng.config import Local
from wazimap_ng.general.error_handling import handle_s3_errors


def upload_files_to_s3(files):
    with handle_s3_errors():
        client = boto3.client(
            "s3",
            aws_access_key_id=Local.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Local.AWS_SECRET_ACCESS_KEY,
            region_name=Local.AWS_S3_REGION_NAME
        )
    for file in files:
        with open(file, "rb") as f:
            file_content = f.read()
            with handle_s3_errors():
                client.put_object(
                    Body=file_content,
                    Key=f"{file}",
                    Bucket=Local.AWS_STORAGE_BUCKET_NAME,
                )
