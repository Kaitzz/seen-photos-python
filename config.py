import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-2')
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
    
    # Photo expiration in seconds (if not viewed)
    PHOTO_EXPIRATION = 43200  # 12 hours
    
    # Max file size (10MB)
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    
    # Allowed extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}