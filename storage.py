import boto3
import uuid
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from config import Config

class S3Storage:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.AWS_REGION
        )
        self.bucket_name = Config.S3_BUCKET_NAME
    
    def upload_photo(self, file_data, file_extension):
        """Upload photo to S3 with unique key"""
        photo_key = f"{uuid.uuid4()}.{file_extension}"
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=photo_key,
                Body=file_data,
                ContentType=f'image/{file_extension}',
                Metadata={
                    'one-time': 'true',
                    'created': datetime.utcnow().isoformat()
                },
                Tagging='purpose=temporary&status=active'
            )
            return photo_key
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            return None
    
    def get_photo(self, photo_key):
        """Get photo from S3 without deleting"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=photo_key
            )
            photo_data = response['Body'].read()
            content_type = response.get('ContentType', 'image/jpeg')
            return photo_data, content_type
        except ClientError as e:
            print(f"Error retrieving from S3: {e}")
            return None, None
    
    def delete_photo(self, photo_key):
        """Delete photo from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=photo_key
            )
            return True
        except ClientError as e:
            print(f"Error deleting from S3: {e}")
            return False
    
    def get_and_delete_photo(self, photo_key):
        """Retrieve photo from S3 and immediately delete it"""
        photo_data, content_type = self.get_photo(photo_key)
        if photo_data:
            self.delete_photo(photo_key)
        return photo_data, content_type
    
    def photo_exists(self, photo_key):
        """Check if photo still exists in S3"""
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=photo_key
            )
            return True
        except ClientError:
            return False