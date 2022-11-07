# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates

import boto3
import io
import helpers.config_manager as config
from concurrent.futures import ThreadPoolExecutor

def connect():
    conn = boto3.client('s3', aws_access_key_id=config.Get('lyvecloud.access_key'), aws_secret_access_key=config.Get('lyvecloud.secret_key'), endpoint_url=config.Get('lyvecloud.endpoint_url')) 

    return conn

def create_bucket(conn, name):
    conn.create_bucket(Bucket=name)

def upload_file(conn, bucket, file_name, object_name=None):
    if object_name is None:
        object_name = file_name
    try:
        response = conn.upload_file(file_name, bucket, object_name)
    except Exception as e:
        print("[s3.upload_file] error", e)
        return False
    return True

def upload_bytesIO(conn, bucket, file_io, object_name):
    try:
        response = conn.upload_fileobj(file_io, bucket, object_name)
    except Exception as e:
        print("[s3.upload_bytesIO] error", e)
        return False
    return True

def download_file(conn, bucket, file_name, object_name=None):
    if object_name is None:
        object_name = file_name
    conn.download_file(bucket, object_name, file_name)

def download_bytesIO(conn, bucket, file_buffer, object_name):
    conn.download_fileobj(bucket, object_name, file_buffer)

def delete_file(conn, bucket, object_name):
    conn.delete_object(Bucket=bucket, Key=object_name)

def list_file(conn, bucket):
    my_bucket = conn.list_objects(Bucket=bucket)
    if not 'Contents' in my_bucket:
        return

    for c in my_bucket['Contents']:
        print(c['Key'], c['Size'], c['LastModified'])

def list_bucket(conn):
    response = conn.list_buckets()

    print('Existing buckets:')
    for bucket in response['Buckets']:
        print(f'{bucket["Name"]}')

def download_latest_file(conn, bucket, period):

    def download_by_executor(c):
        res = []
        if c['LastModified'] >= period:
            file_buffer = io.BytesIO()
            conn.download_fileobj(bucket, c['Key'], file_buffer)
            file_buffer.seek(0)

            found = {'key': c['Key'], 'last_modified': c['LastModified'], 'body': file_buffer}
            res.append(found)
        return res

    paginator = conn.get_paginator('list_objects')
    page_iterator = paginator.paginate(Bucket=bucket)

    contents = []
    for page in page_iterator: 
        contents += page['Contents']

    if not contents:
        return None

    latestFiles = []
    result = []

    with ThreadPoolExecutor(max_workers=20) as exe:
        result = exe.map(download_by_executor, contents)

    for r in result:
        latestFiles.extend(r)
    return latestFiles

