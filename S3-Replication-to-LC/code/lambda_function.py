import os
import json
import boto3
import logging
import urllib
import uuid
from botocore.exceptions import ClientError

log = logging.getLogger()
log.setLevel(logging.INFO)

smClient = boto3.client('secretsmanager')

def lambda_handler(event, context):
    secret_name   = os.environ['SECRET_KEY']
    region_name   = os.environ['REGION']
    target_bucket = os.environ['TARGET_BUCKET']
            
    log.info('Secret - {}: Region: {}, Target: {}'.format(secret_name, region_name, target_bucket))
    
    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = smClient.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        else:
            raise e
    else:
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            data = json.loads(secret)

    # Get the bucket and object key from the Event
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    source_key    = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    source_size   = event['Records'][0]['s3']['object']['size']

    log.info('Source size {:d}'.format(source_size))

    # This function cannot process objects larger than 10GB due to Lambda storage limitation.
    # So skip copying those objects...
    if source_size > 10737418240:
        log.info('Object: {} size {:d} larger than 10GB limit, so skipping'.format(source_key, source_size))
        return

    source_s3_client = boto3.client('s3')

    s3_session = boto3.Session(aws_access_key_id     = data['lc_access_key'],
                               aws_secret_access_key = data['lc_secret_key'],
                               region_name           = region_name)
    target_s3_client = s3_session.client('s3', endpoint_url = data['lc_endpoint_url'])
   
    source_download = '/tmp/' + uuid.uuid4().hex
    try:
        source_s3_client.download_file(source_bucket, source_key, source_download)
    except ClientError as e:
        raise e
    try:
        target_s3_client.upload_file(source_download, target_bucket, source_key)
    except ClientError as e:
        raise e
