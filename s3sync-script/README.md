# Local directory data sync with Lyve Cloud Bucket 

## Introduction
This script will copy contents from Linux based computer over S3 only when trigger file is created
There are some scenarios when the user wants to keep the local directory and s3 bucket in sync, the expectation is local data and s3 data should be the same.
If the user adds or removes any file or directory from the local directory then it should also get added or removed from the S3 bucket.

## Problem Statment
In a normal scenario ‘aws s3 sync’ command would do the job but when a user would modify the data how the script would know that if data is modified and need to sync the directory with S3 bucket
There is a service in AWS Cloud through which we can create a trigger in Lambda using Cloudwatch but in Lyve Cloud we do not have Lambda functions.

## Requirements
Before you start, please make sure you have these requirements and information in place:
- Lyve Cloud account with privilage to create service account.
- Compute instance with 
  - Linux operating system installed.
  - Enough storage space to hold the data.
  - AWS CLI utility installed.


## Setup Instructions
### Step 1: Get Lyve Cloud credentials and endpoints
Login to Lyve Cloud console, create a Service Account with appropriate permissions and extract the following:
- Access Key
- Secret key
- Endpoint URL

### Step 2: Configure Lyve Cloud S3API CLI utility account
1. Login to Linux compute instance
2. run following command to configure Lyve Cloud Profile
   aws configure --profile <profile-name>
Provide the access key ID and secreate access key of Lyve Cloud Service account

### Step 3: Create s3 bucket for data replication
1.  Create Lyve Cloud S3 bucket to sync data between local directory and Lyve Cloud S3
    use below command (replace name of bucket as you like)
    aws –-profile <profile_name> --endpoint <endpoint> s3api create-bucket –bucket <bucket_name>
2.  Varify the bucket is created
    aws –-profile <profile_name> --endpoint <endpoint> s3api list-buckets
 
### Step 4: Copy the script to compute instance
1.  Create a local directory 's3script'
    mkdir s3script
    cd s3script
    cp ~s3sync .
    chmod +x s3sync
2.  create a directory which you want to sync with s3 bucket
    mkdir dist
3. Copy the data that needs to be sync with S3
4. Create the trigger file
    touch dist/trigger

### Step 5: Add the crontab entry to run the script every 5 mins
 sudo crontab -e
*/5 * * * * /home/user/s3script/s3sync.sh


## Results 
The script will check if the trigger file is exist inside dist directory if it exist then data will copied to S3 bucket and trigger file will be removed.
