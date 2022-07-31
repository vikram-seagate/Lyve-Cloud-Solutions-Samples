# Bari Arviv - S3 Actions Code Sample - Python
import json
import boto3
import logging
import argparse
from botocore.exceptions import ClientError


# The function prints the list of the existing buckets
def list_buckets():
    buckets = s3_client.list_buckets()
    print("List Buckets:")
    if buckets['Buckets']:
        for bucket in buckets['Buckets']:
            print('* %s' % bucket['Name'])


# The function performs the operation according to the parameter obtained. In case of
# an exception, print it. You can create, delete and print the list of existing buckets
def bucket_operations(bucket_name=None, operation='list'):
    if operation != 'list' and not bucket_name:
        logging.error('The bucket name cannot be empty! Please provide a bucket name')
        return False
    try:
        if operation == 'remove':
            s3_client.delete_bucket(Bucket=bucket_name)
            print('The bucket %s was successfully deleted' % bucket_name)
        elif operation == 'make':
            s3_client.create_bucket(Bucket=bucket_name)
            print('Bucket %s was created successfully' % bucket_name)
        elif operation == 'list':
            list_buckets()
        else:
            logging.error('Unknown operation!!')
            return False
    except ClientError as err:
        logging.error(err)
        return False

    return True


# The function prints the list of the objects in the bucket
def list_objects(bucket_name):
    current_bucket = s3_resource.Bucket(bucket_name)
    for obj in current_bucket.objects.all():
        print('Object Name: %s, Object Size: %d, Last modified: %s' % (obj.key, obj.size, str(obj.last_modified)))


# The function performs the operation according to the parameter obtained. In case of an exception,
# print it. You can upload, download and delete an object and print the list of the objects inside the bucket.
def object_operations(bucket_name, operation='list', objectname=None, object_location=None):
    if not bucket_name:
        logging.error('The bucket name cannot be empty! Please provide a bucket name')
        return False
    try:
        if operation == 'list':
            list_objects(bucket_name)
        elif operation == 'remove':
            s3_client.delete_object(Bucket=bucket_name, Key=objectname)
            print('The object %q was successfully deleted' % objectname)
        elif operation == 'get':
            s3_resource.Bucket(bucket_name).download_file(objectname, object_location)
            print('The object %s has been successfully downloaded' % objectname)
        elif operation == 'put':
            s3_resource.Bucket(bucket_name).upload_file(object_location, objectname)
            print('The object %s has been uploaded successfully' % objectname)
        else:
            logging.error('Unknown operation!!')
            return False
    except ClientError as err:
        logging.error(err)
        return False

    return True


# The function returns the credentials from the config file
def read_config(file_path):
    with open(file_path, 'r') as file:
        content_json = json.loads(file.read())

    return content_json


def flags_init():
    # Args contains user inputs
    parser = argparse.ArgumentParser(description='python3 s3-actions.py --Operation=put --BucketName=bari-test --ObjectPath=example.txt')
    parser.add_argument('-B', '--BucketName', type=str, help='The bucket name')
    parser.add_argument('-C', '--ConfigPath', type=str, default='config.json', help='The config file path')
    parser.add_argument('-Path', '--ObjectPath', type=str, help='The object path for delete, put, and get object')
    parser.add_argument('-Op', '--Operation', type=str, required=True, help='mb[MakeBucket]/rb[RemoveBucket]/lb[ListBuckets]/put[PutObject]/rm[RemoveObject]/get[GetObject]/ls[ListObjects]')
    return parser.parse_args()


def verify_flags():
    if args.Operation == "":
        print("ERROR: --Operation flag cannot be empty! Please provide an operation")
        return 0
    if args.BucketName == "" and args.Operation != "ls":
        print("ERROR: --BucketName flag cannot be empty! Please provide a bucket name")
        return 0
    if (args.Operation == "put" or args.Operation == "rm" or args.Operation == "get") and args.ObjectPath == "":
        print("ERROR: --ObjectPath flag cannot be empty! Please provide an object path")
        return 0

    return 1


def main():
    # Makes a new bucket
    if args.Operation == 'mb' or args.Operation == 'MakeBucket':
        bucket_operations(args.BucketName, 'make')
    # Removes a bucket
    elif args.Operation == 'rb' or args.Operation == 'RemoveBucket':
        bucket_operations(args.BucketName, 'remove')
    # Prints the list of the existing buckets
    elif args.Operation == 'lb' or args.Operation == 'ListBuckets':
        bucket_operations()
    # Puts a file to the bucket
    elif args.Operation == 'put' or args.Operation == 'PutObject':
        object_operations(args.BucketName, 'put', args.ObjectPath, args.ObjectPath)
    # Removes an object from the bucket
    elif args.Operation == 'rm' or args.Operation == 'RemoveObject':
        object_operations(args.BucketName, 'remove', args.ObjectPath)
    # Gets an object from the bucket
    elif args.Operation == 'get' or args.Operation == 'GetObject':
        object_operations(args.BucketName, 'get', args.ObjectPath, args.ObjectPath)
    # Prints the list of the objects in the bucket
    elif args.Operation == 'ls' or args.Operation == 'ListObjects':
        object_operations(args.BucketName)
    else:
        print('Unknown operation!!')


if __name__ == '__main__':
    args = flags_init()
    config = read_config(args.ConfigPath)

    # Initializes the credentials and creates an S3 service client
    if verify_flags():
        s3_resource = boto3.resource(
            's3',
            endpoint_url=config["endpoint_url"],
            aws_access_key_id=config["access_key"],
            aws_secret_access_key=config["secret_key"],
            region_name=config["region_name"],
        )

        s3_client = boto3.client(
            's3',
            endpoint_url=config["endpoint_url"],
            aws_access_key_id=config["access_key"],
            aws_secret_access_key=config["secret_key"],
            region_name=config["region_name"],
        )

        main()
