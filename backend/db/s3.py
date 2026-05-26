import boto3
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

s3 = boto3.client('s3')
BUCKET = os.getenv('S3_BUCKET')

def upload_model(local_path='models/model.pkl'):
    s3.upload_file(local_path, BUCKET, 'models/model.pkl')
    print(f" The model was uploaded to s3://{BUCKET}/models/model.pkl")

def download_model(local_path='/tmp/model.pkl'):
    s3.download_file(BUCKET, 'models/model.pkl', local_path)
    print(f" The model was downloaded to {local_path}")
    return local_path