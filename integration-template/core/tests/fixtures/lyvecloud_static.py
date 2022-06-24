""" LYVECLOUD STATIC """
LYC_LIST_BUCKET_OK: dict = {
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

LYC_HEAD_BUCKET_OK: dict = {
  "ResponseMetadata": {
    "RequestId": "16ECB0CF54BB15EE",
    "HostId": "",
    "HTTPStatusCode": 200,
    "HTTPHeaders": {
      "content-length": "0",
      "connection": "keep-alive",
      "server": "nginx/1.21.3",
      "date": "Sat, 07 May 2022 02:12:47 GMT",
      "accept-ranges": "bytes",
      "content-security-policy": "block-all-mixed-content",
      "vary": "Origin",
      "x-amz-bucket-region": "ap-southeast-1",
      "x-amz-request-id": "16ECB0CF54BB15EE",
      "x-xss-protection": "1; mode=block"
    },
    "RetryAttempts": 0
  }
}
