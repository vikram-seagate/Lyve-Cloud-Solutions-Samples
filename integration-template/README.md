# CSTOR S3 Data Migration

[Video Link](https://4pqfyjuvjh.vmaker.com/record/7cYOqhUSba0EjQSU)

## Introduction
CSTOR S3 Data Migration solution consists of a dashboard frontend, webserver backend by Django and background workers powered by Dramatiq.Signed


## Requirements

OS: Ubuntu 20.04 and above

Please see the `README.rst` in the `core` and `webapp` folders respectively.

## Known Limitations 
- During the demo, we are running the application and workers on a single host on Digitalocean where network I/O is the bottleneck.
   - In future, we should run the workers across different machines deal with the network bottleneck.
- Task retries and error handling needs to be more robust

##### Key areas to address during the challenge
* Security
    - AWS Access Key and Secret Key are both stored in AWS Secrets Manager
    - Credentials to access AWS Secrets Manager are read from the environment.
* Performance
    - Each worker is run with 4 processes and 10 greenlets for a total of 40 parallel task handlers.
* Resiliency 
    - Each migration task has a built-in auto-retry mechanism if there are errors during the download / upload phase
       - It will retry up to 2 times before being left in the Fail Queue
   - For other errors, the task will retry itself with increasing gaps between retries
* Scalability
   - Workers can be distributed across different machines and connect to the same Redis instance
      - Each worker needs to access the migration cache at the same NFS dir / EFS volume for consistency.
   - For large files, every 100mb spawns 2 worker sub-threads up to a maximum of 30
      - Because the transfer process is lightweight, there can be hundreds of sub-threads without issue
      - Usually, network I/O is the bottleneck
* Recovery
   - Workers can fail / error-out at any point and another worker will pick up the remaining tasks
   - Each task "packet" is about 200mb in size and can consist of multiple files.
   - File status updates like completion and errors are committed in a single atomic transaction so that migration data is consistent.

## Running Steps

Please see the `README.rst` in the `core` and `webapp` folders respectively.


## Results 
Show the results using images or a short paragraph.

## Tested by

### `/core`
This folder contains all the cstor-s3 core libraries and is responsible for worker tasks; spawning worker process, updating dashboard API

### `/webapp`
This folder contains the frontend and backend for the web application.
