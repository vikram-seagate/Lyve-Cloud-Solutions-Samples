import os
import json
import boto3
from services.pull_and_upload_logs_service import PullAndUploadLogsService


def generate_cloudwatch_client(params):
    return boto3.client('logs',
        region_name = params.get("region_name"),
        aws_access_key_id = params.get("aws_access_key_id"),
        aws_secret_access_key = params.get("aws_secret_access_key"),
    )


def generate_lyvecloud_client(params):
    return boto3.client('s3',
        region_name = params.get("region_name"),
        aws_access_key_id = params.get("aws_access_key_id"),
        aws_secret_access_key = params.get("aws_secret_access_key"),
        endpoint_url = "https://s3." + params.get("region_name") + ".lyvecloud.seagate.com",
    )


def from_file(file_path):
    with open(file_path, 'r') as file:
        content_json = json.loads(file.read())

    return content_json


def extract_env():
        env_dict = {"lyvecloud": {}, "aws":{}}

        # Lyve Cloud credentials
        env_dict["lyvecloud"]["region_name"] = os.environ['LYVE_REGION']
        env_dict["lyvecloud"]["aws_access_key_id"] = os.environ['LYVE_ACCESS']
        env_dict["lyvecloud"]["aws_secret_access_key"] = os.environ['LYVE_SECRET']

        # AWS credentials
        env_dict["aws"]["region_name"] = os.environ['AWS_REGION']
        env_dict["aws"]["aws_access_key_id"] = os.environ['AWS_ACCESS']
        env_dict["aws"]["aws_secret_access_key"] = os.environ['AWS_SECRET']

        return env_dict


def main():
    config = from_file(os.path.dirname(os.path.realpath(__file__))+"/config.json")
    credentials = extract_env()

    # init boto3 S3 Lyve Cloud client and AWS CloudWatch client
    cloudwatch_client = generate_cloudwatch_client(credentials["aws"])
    lyvecloud_client = generate_lyvecloud_client(credentials["lyvecloud"])

    # calling service that pulls logs, and sends them in groups to CloudWatch
    PullAndUploadLogsService(
        s3 = lyvecloud_client,
        cloudwatch = cloudwatch_client,
        mode = config["lyvecloud"]["mode"],
        log_group = config["aws"]["log_group"],
        log_type = config["lyvecloud"]["log_type"],
        input_bucket = config["lyvecloud"]["input_bucket"]
        )()


if __name__ == '__main__':
    main()