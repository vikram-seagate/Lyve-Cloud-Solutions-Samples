import os
import json
import boto3
import boto3.session
from chalice import Chalice
from botocore.client import Config


region_n = os.environ['lc_region']
secret_name = os.environ['lc_secrets']
lc_endpoint = os.environ['lc_endpoint']


def getSecretData():
  session = boto3.session.Session()
  client = session.client(service_name='secretsmanager', region_name=region_n)
  get_secret_value_response = client.get_secret_value(SecretId=secret_name)
  secrets_response = get_secret_value_response['SecretString']
  return json.loads(secrets_response)


data = getSecretData()
lc_s3 = boto3.resource('s3',
    aws_access_key_id = data['lc_access_key'],
    aws_secret_access_key = data['lc_secret_key'],
    config = Config(signature_version='s3v4'),
    region_name = region_n,
    endpoint_url = lc_endpoint
)

aws_s3 = boto3.resource('s3')
target_bucket = os.environ['target_bucket']
app = Chalice(app_name='syncer', debug=True)
source_bucket = secret_name = os.environ['source_bucket']


@app.on_s3_event(bucket=source_bucket, prefix='', events=['s3:ObjectCreated:*'])
def added_object_sync(event):
    event_dic = event.to_dict()
    app.log.info(event_dic)
    action_name = event_dic['Records'][0]['eventName']
    size = event_dic['Records'][0]['s3']['object']['size']
    app.log.info("Event received for bucket: %s, key %s, eventName %s, size %s", event.bucket, event.key, action_name, size)

    if size > 0:
        app.log.info("Create sync start")
        app.log.info(source_bucket)
        file_path = '/tmp/' + event.key
        app.log.info(file_path)
        aws_s3.Bucket(source_bucket).download_file(event.key, file_path)
        app.log.info("Downloaded file")
        lc_s3.Object(target_bucket, event.key).upload_file(file_path)
        app.log.info("Create sync complete")


@app.on_s3_event(bucket=source_bucket, prefix='', events=['s3:ObjectRemoved:*'])
def Removed_object_sync(event):
    event_dic = event.to_dict()
    app.log.info(event_dic)
    action_name = event_dic['Records'][0]['eventName']
    app.log.info("Event received for bucket: %s, key %s, eventName %s", event.bucket, event.key, action_name)
    app.log.info("Remove sync start")
    lc_s3.Object(target_bucket, event.key).delete()
    app.log.info("Remove sync complete")
