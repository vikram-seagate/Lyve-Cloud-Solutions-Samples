import boto3
import os
from botocore.client import Config
import base64


# Set the access key ID and secret access key
access_key_id = os.environ['ACCESS_KEY']
secret_access_key = os.environ['SECRET_KEY']

# Set the bucket name, object key, endpoint
bucket_name = os.environ['BUCKET_NAME']
object_key = os.environ['OBJECT_KEY']
endpoint = os.environ['ENDPOINT']

# Create an S3 client
client = boto3.client(
    "s3",
    endpoint_url=endpoint,
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    config=Config(signature_version="s3v4"),
)

def lambda_handler(event, context):    
    file_object = client.get_object(Bucket=bucket_name, Key=object_key)
    file_data = file_object['Body'].read()
    content_type = file_object['ContentType']
    
    return {
        'headers': { "Content-Type": content_type },
        'statusCode': 200,
        'body': base64.b64encode(file_data).decode('utf-8'),
        'isBase64Encoded': True
    }