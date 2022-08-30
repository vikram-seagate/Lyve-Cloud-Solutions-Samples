"""AWS Secrets Static"""
# pylint: disable=line-too-long
import datetime
from dateutil.tz import tzlocal


CREATE_SECRET_OK: dict = {
    "ARN": "arn:aws:secretsmanager:ap-southeast-1:204282492273:secret:/cstor/dev/1/secrets/AWSConn1-T5zIxQ",
    "Name": "/cstor/dev/1/secrets/AWSConn1",
    "VersionId": "8b0c0f21-ea46-402b-a4f5-f163957d5595",
    "ResponseMetadata": {
        "RequestId": "06081dad-2f3f-4933-9913-25f87a63b95a",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "x-amzn-requestid":
            "06081dad-2f3f-4933-9913-25f87a63b95a",
            "content-type":
            "application/x-amz-json-1.1",
            "content-length": "194",
            "date": "Sun, 15 May 2022 14:41:42 GMT"},
            "RetryAttempts": 0
    },
}

GET_SECRET_OK: dict = {
    "ARN": "arn:aws:secretsmanager:ap-southeast-1:204282492273:secret:/cstor/dev/1/secrets/AWSConn1-T5zIxQ",
    "Name": "/cstor/dev/1/secrets/AWSConn1",
    "VersionId": "8b0c0f21-ea46-402b-a4f5-f163957d5595",
    "SecretString": "{\"AWS_ACCESS_KEY_ID\": \"abc123\", \"AWS_SECRET_ACCESS_KEY\": \"Test123!\"}",
    "VersionStages": ["AWSCURRENT"],
    "CreatedDate": datetime.datetime(2022, 5, 15, 14, 41, 43, 275000, tzinfo=tzlocal()),
    "ResponseMetadata": {
        "RequestId": "42d89cd4-c83a-450e-8412-2ce6f51969c5",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "x-amzn-requestid": "42d89cd4-c83a-450e-8412-2ce6f51969c5",
            "content-type": "application/x-amz-json-1.1",
            "content-length": "350",
            "date": "Mon, 16 May 2022 01:38:49 GMT"},
            "RetryAttempts": 0,
    },
}

DELETE_SECRET_OK : dict = {
	"ARN": "arn:aws:secretsmanager:ap-southeast-1:204282492273:secret:/cstor/dev/1/secrets/AWSConn1-T5zIxQ",
    "Name": "/cstor/dev/1/secrets/AWSConn1",
    "DeletionDate": datetime.datetime(2022, 5, 16, 2, 27, 35, 463000, tzinfo=tzlocal()),
    "ResponseMetadata": {
        "RequestId": "748ac67b-7809-4e07-a164-ae7e718ae45d",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "x-amzn-requestid": "748ac67b-7809-4e07-a164-ae7e718ae45d",
            "content-type": "application/x-amz-json-1.1",
            "content-length": "175",
            "date": "Mon, 16 May 2022 02:27:34 GMT",
        },
        "RetryAttempts": 0,
    },
}
