# S3 Actions Code Sample - Python

## Prerequisites
* [Python3](https://www.python.org/downloads/)

## Running the CLI Tool
1. Enter your credentials in [config.json file](config.json):
   * access key
   * secret key
   * region name
   * endpoint URL
2. Install all required packages: `pip3 install -r requirements.txt`.
3. Run the s3-actions.py --help to see all options: `python3 s3-actions.py --help`
```
[bari ~]$ python3 s3-actions.py -h    
usage: s3-actions.py [-h] [-B BUCKETNAME] [-C CONFIGPATH] [-Path OBJECTPATH] -Op OPERATION

python3 s3-actions.py --Operation=put --BucketName=bari-test --ObjectPath=example.txt

optional arguments:
  -h, --help            show this help message and exit
  -B BUCKETNAME, --BucketName BUCKETNAME
                        The bucket name
  -C CONFIGPATH, --ConfigPath CONFIGPATH
                        The config file path
  -Path OBJECTPATH, --ObjectPath OBJECTPATH
                        The object path for delete, put, and get object
  -Op OPERATION, --Operation OPERATION
                        mb[MakeBucket]/rb[RemoveBucket]/lb[ListBuckets]/put[PutObject]/rm[RemoveObject]/get[GetObject]/ls[ListObjects]
```

### Sessions Setup
```python
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
```

### Make Bucket
```python
s3_client.create_bucket(Bucket=bucket_name)
```

### Remove Bucket
```python
s3_client.delete_bucket(Bucket=bucket_name)
```

### List Buckets
```python
buckets = s3_client.list_buckets()
print("List Buckets:")
if buckets['Buckets']:
   for bucket in buckets['Buckets']:
      print('* %s' % bucket['Name'])
```

### Put Object
```python
s3_resource.Bucket(bucket_name).upload_file(object_location, objectname)
```

### Remove Object
```python
s3_client.delete_object(Bucket=bucket_name, Key=objectname)
```

### Get Object
```python
s3_resource.Bucket(bucket_name).download_file(objectname, object_location) 
```

### List Objects
```python
current_bucket = s3_resource.Bucket(bucket_name)
for obj in current_bucket.objects.all():
   print('Object Name: %s, Object Size: %d, Last modified: %s' % (obj.key, obj.size, str(obj.last_modified)))
```

## Tested By:
* March 13, 2022: Bari Arviv (bari.arviv@seagate.com) on macOS
