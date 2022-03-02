from datetime import datetime, timedelta
import boto3
import gzip
import json

class PullLogsService(object):
    def __init__(self, s3, bucket_name):
        self.s3 = s3
        self.bucket_name = bucket_name

    def __call__(self):
        prefix = self.__get_prefix__()
        logs = None
        all_objects = self.s3.list_objects(Bucket=self.bucket_name, Prefix=prefix) 
        current_log_file = all_objects["Contents"][0]["Key"]

        s3_response_object = self.s3.get_object(Bucket=self.bucket_name, Key=current_log_file)
        body = s3_response_object["Body"]

        with gzip.open(body, "rt") as gf:
            logs = self.__format_gz_file__(gf)

        return logs

    def __get_prefix__(self):
        today = datetime.utcnow() - timedelta(hours=1)
        string_month = today.strftime("%B")
        year = today.year
        month = today.strftime("%m")
        day = today.strftime("%d")
        hour = today.strftime("%H")
        return f"{string_month}-{year}/S3-{self.bucket_name}-{year}-{month}-{day}-{hour}"

    def __format_gz_file__(self, file):
        lines = file.readlines()
        return [json.loads(line) for line in lines]