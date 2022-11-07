
# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates

import helpers.config_manager as config
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timezone
from tqdm import tqdm

def __connect():
    try:
        client = InfluxDBClient(url=config.Get('influxdb.host'), token=config.Get('influxdb.token'), org=config.Get('influxdb.org'))
        return client, client.buckets_api()
    except Exception as e:
       print('[influxdb.connect] error', e)
    return None

def __hasBucket(api, bucket_name):
    for b in api.find_buckets().buckets:
        if b.name == bucket_name:
            return True
    return False

def __create_bucket(api, bucket_name, description=''):
    bucket = api.create_bucket(bucket_name=bucket_name, description=description, org=config.Get('influxdb.org'))

    return bucket

def make_point(measurement, tags, fields, time = datetime.now(timezone.utc)):
    if time:
        timestamp = time
    else:
        timestamp = datetime.now(timezone.utc)
    data = { 
        "measurement": measurement, 
        "tags": tags,
        "fields": fields,
        "time": timestamp
    }
    return Point.from_dict(data) 

def write(point):
    client, api = __connect()
    bucket_name = config.Get('influxdb.bucket')

    try:
        writor_api = client.write_api(write_options=SYNCHRONOUS)
        writor_api.write(bucket=bucket_name, record=point)
    except Exception as e:
        # influxdb_client.rest.ApiException: (404)
        # HTTP response body: {"code":"not found","message":"bucket \"test-with-missing-bucket-name\" not found"}
        print('[influxdb.write] error', e)

        if not __hasBucket(api, bucket_name):
            __create_bucket(api, bucket_name)

            # Reclursive call
            write(point)

        raise Exception(e)


def is_init_influx():
    client, api = __connect()
    bucket_name = config.Get('influxdb.bucket')
    if __hasBucket(api, bucket_name):
        return False
    else:
        return True

def BatchWrite(points):
    """
    Receives a list of points and writes them to influxdb
    """
    client, api = __connect()
    bucket_name = config.Get('influxdb.bucket')
    try:
        with client.write_api(write_options=WriteOptions(batch_size=500,
                                                        flush_interval=10_000,
                                                        jitter_interval=2_000,
                                                        retry_interval=5_000,
                                                        max_retries=5,
                                                        max_retry_delay=30_000,
                                                        exponential_base=2)) as _write_client:
            pBar = tqdm(total=len(points), desc='Batch writing: ')
            for point in points:
                _write_client.write(bucket=bucket_name, record=point)
                pBar.update(1)
            pBar.close() 
    
    except Exception as e:
        # influxdb_client.rest.ApiException: (404)
        # HTTP response body: {"code":"not found","message":"bucket \"test-with-missing-bucket-name\" not found"}
        print('[influxdb.write] error', e)

        if not __hasBucket(api, bucket_name):
            __create_bucket(api, bucket_name)

            # Reclursive call
            write(point)

        raise Exception(e)