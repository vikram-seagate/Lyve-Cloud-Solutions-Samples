""" AWS STATIC """
import datetime
from dateutil.tz import tzutc


AWS_LIST_BUCKET_OK: dict = {
    "Buckets": [
        {
            "Name": "testvarchive",
            "CreationDate": "2022-01-07T09:09:01+00:00"
        },
    ],
    "Owner": {
        "DisplayName": "hello",
        "ID": "xxx"
    }
}

AWS_HEAD_BUCKET_OK: dict = {
  "ResponseMetadata": {
    "RequestId": "EGW5Y6CJ5BSQWHHQ",
    "HostId": "OnVI7yBGkwRlzoVChj5+BE/+WcrFBzToZvlydhoqpHkZzMDX3PrtpN4TwbkYualvtLHWu8RATSE=",
    "HTTPStatusCode": 200,
    "HTTPHeaders": {
      "x-amz-id-2": "OnVI7yBGkwRlzoVChj5+BE/+WcrFBzToZvlydhoqpHkZzMDX3PrtpN4TwbkYualvtLHWu8RATSE=",
      "x-amz-request-id": "EGW5Y6CJ5BSQWHHQ",
      "date": "Fri, 06 May 2022 01:49:21 GMT",
      "x-amz-bucket-region": "ap-southeast-1",
      "x-amz-access-point-alias": "false",
      "content-type": "application/xml",
      "server": "AmazonS3"
    },
    "RetryAttempts": 1
  }
}


AWS_LIST_OBJECT_NO_RECURSE: dict = {
  "ResponseMetadata": {
    "RequestId": "R7WV4MBR1D0VBQAP",
    "HostId": "SUdIZNW+faduWmmhzIAH5VEIi3k6T92ywZL8LqrbfCu4NR4PLJviRxsadNge8FXF9+5UOt5v9Gk=",
    "HTTPStatusCode": 200,
    "HTTPHeaders": {
      "x-amz-id-2": "SUdIZNW+faduWmmhzIAH5VEIi3k6T92ywZL8LqrbfCu4NR4PLJviRxsadNge8FXF9+5UOt5v9Gk=",
      "x-amz-request-id": "R7WV4MBR1D0VBQAP",
      "date": "Sat, 07 May 2022 06:32:37 GMT",
      "x-amz-bucket-region": "ap-southeast-1",
      "content-type": "application/xml",
      "transfer-encoding": "chunked",
      "server": "AmazonS3"
    },
    "RetryAttempts": 0
  },
  "IsTruncated": False,
  "Name": "testvarchive",
  "Prefix": "TEST_OUTLAY/medium_files/",
  "Delimiter": "/",
  "MaxKeys": 1000,
  "CommonPrefixes": [
    {
      "Prefix": "TEST_OUTLAY/medium_files/a/"
    },
    {
      "Prefix": "TEST_OUTLAY/medium_files/b/"
    },
    {
      "Prefix": "TEST_OUTLAY/medium_files/d/"
    }
  ],
  "EncodingType": "url",
  "KeyCount": 3
}

AWS_LIST_OBJECT_PREFIX: dict = {
    'ResponseMetadata': {
        'RequestId': '8FW6A2N62XTHMHEX',
        'HostId': 'LZQwTbEV69iJbYsBGar/J/1TkDpI6+lXfJyp0zQlufG7bq1vqG53HehEKZv0aWnL0kmhskT6RiI=',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'x-amz-id-2': 'LZQwTbEV69iJbYsBGar/J/1TkDpI6+lXfJyp0zQlufG7bq1vqG53HehEKZv0aWnL0kmhskT6RiI=',
            'x-amz-request-id': '8FW6A2N62XTHMHEX',
            'date': 'Sat, 07 May 2022 07:01:55 GMT',
            'x-amz-bucket-region': 'ap-southeast-1',
            'content-type': 'application/xml',
            'transfer-encoding': 'chunked',
            'server': 'AmazonS3',
        },
        'RetryAttempts': 0,
    },
    'IsTruncated': False,
    'Contents': [
        {
            'Key': 'TEST_OUTLAY/large_files/large_0.txt',
            'LastModified': datetime.datetime(2022, 5, 7, 3, 41, 34, tzinfo=tzutc()),
            'ETag': '"50b52adb0eee4202821f2987f5b77f66-259"',
            'Size': 2166358016,
            'StorageClass': 'STANDARD',
        },
        {
            'Key': 'TEST_OUTLAY/large_files/large_1.txt',
            'LastModified': datetime.datetime(2022, 5, 7, 3, 41, 34, tzinfo=tzutc()),
            'ETag': '"247928eca3113e6acb26c934777aabba-136"',
            'Size': 1135607808,
            'StorageClass': 'STANDARD',
        },
    ],
    'Name': 'testvarchive',
    'Prefix': 'TEST_OUTLAY/large_files',
    'MaxKeys': 1000,
    'EncodingType': 'url',
    'KeyCount': 9,
}
