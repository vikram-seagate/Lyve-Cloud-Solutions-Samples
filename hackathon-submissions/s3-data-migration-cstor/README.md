# CSTOR S3 Data Migration

![CSTOR_UI](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/ui_1.PNG)

[Demo Video](https://4pqfyjuvjh.vmaker.com/record/7cYOqhUSba0EjQSU)

For signing off

## Introduction
CSTOR S3 Data Migration solution consists of a dashboard frontend, webserver backend by Django and background workers powered by Dramatiq.

## Changelog

## Requirements

### Minimum Specs
- Ubuntu 20.04
- 2 vCPUs
- 4 GB Ram
- 80GB NVMe SSD
- 1gb/s Ethernet


### Software

- Docker 20.10.5
- Docker Compose v2.5.0

#### For Development

- Python 3.10.1
- Pip 21.2.3
- Python Global Packages
   - nox==2022.1.7
   - poetry==1.1.3

- Nodejs v16.15.0
- NPM 8.5.5
- RocksDB Dependencies
   - sudo apt-get install -y librocksdb-dev liblz4-dev libsnappy-dev

### Credentials

- Required to have the following for testing and administration purposes

|CLOUD|AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|S3 ENDPOINT |PERMISSIONS REQUIRED|USER
|---|---|---|---|---|---|
|AWS|Required|Required|Optional|S3FullAccess| End-User
|LyveCloud|Required|Required|Required|S3FullAccess| End-User
|AWS|Required|Required|N/A|SecretsManager Read and Write| Worker Process

## Known Limitations
### UI Bugs
- Navigation bar at the top of the UI does not change after the user has signed-in
  - To fix, click on the cstor icon on the top left to view the Migrations, Buckets and Connections tab or reload the page after signing in.
- After adding a bucket from the `Scan Bucket` button , the page does not redirect to the Buckets page.
  - To fix, wait for a few seconds after adding the bucket and then click on the Buckets tab on the Navigation Bar to see the newly created bucket.
### Performance
- During the demo, we are running the application and workers on a single host on Digitalocean where network I/O is the bottleneck.
   - In future, we should run the workers across different machines deal with the network bottleneck.
- Task retries and error handling needs to be more robust
   - End-users should receive notifications on migration errors and failures
   - Create logic for handling dead-letters, idle items in IN_PROGRESS queues.
- Pausing the migration will only prevent new files from being queued, existing files in progress are allowed to complete

## Key areas to address during the challenge
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

Videos are available for the setup

Part 1: Dramatiq Backend Worker and Frontend Setup

[Part 1](https://4pqfyjuvjh.vmaker.com/record/0f0gsAWJXuVp7eZO/)

Part 2: New user account setup and new migration demo

[Part 2](https://4pqfyjuvjh.vmaker.com/record/nUVomsnKdq52Mwi2)


### Step 1. Retrieve required credentials for AWS and Lyvecloud S3 Buckets

Credentials must have the required permissions and endpoints as per the **Credentials** section above.

### Step 2. Create the AWS Credentials for reading and writing to AWS Secrets Manager
1. Login to AWS and go over to [IAM](https://console.aws.amazon.com/iamv2/home).

![AWS_1](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/aws_1.PNG)

2. Click on `Users` on the left sidebar and then `Add User`

![AWS_2](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/aws_2.PNG)

![AWS_3](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/aws_3.PNG)

3. Fill in the username and select `AccessKey - Programmatic Access` for the AWS Access Type

![AWS_4](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/aws_4.PNG)

4. On Set Permissions, Click `Attach Existing Policies Directly` and tick `SecretsManagerReadWrite`

![AWS_5](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/aws_5.PNG)

![AWS_6](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/aws_6.PNG)

5. Review the created details and click on `Create user` button

![AWS_7](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/aws_7.PNG)

6. Save the generated `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

![AWS_8](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/aws_8_censored.jpg)


Please note that you will not be able to see the secret key again after leaving the page.

### Step 3. Install Git

```bash
$ sudo apt-get update -y; sudo apt-get install git
```

### Step 4. Clone the project repo and populate .env file

```bash
$ mkdir ~/hackathon
$ cd ~/hackathon
$ git clone https://github.com/Segate/Lyve-Cloud-Solutions-Samples.git
$ cd Lyve-Cloud-Solutions-Sample/hackathon-submissions/s3-data-migration-cstor
```

Create a new file `.env` in the project folder. Please use `example.env` for reference, only change values enclosed with `<>` and remove the `<>`.

To generate strong passwords, users can use the [Lastpass](https://www.lastpass.com/features/password-generator) website.
Passwords should be at least 15 characters long and alpha-numeric.

Use different generated passwords for the following variables in `.env` file, using the site above.

- REDIS_PASS
- SECRET_KEY
- DJANGO_SUPERUSER_PASSWORD

Please **re-use** the REDIS_PASS password for the following:
- WORKER_REDIS_PASSWD

For the example below, replace the placeholder `<>` with your value.
For example, replace `REDIS_PASS=<GENERATED PASSWORD HERE>` with `REDIS_PASS=YourStrongPassword123456`

The solution is expected to be deployed in VM, load balancer, Kubernetes environment with its own IP.

In the example below, we assume the VM IP address is `192.168.1.2`, with port `8082`.


```bash
REDIS_PASS=<GENERATED PASSWORD HERE>
SECRET_KEY=<GENERATED PASSWORD HERE>
ALLOWED_HOSTS=127.0.0.1,localhost,192.168.1.2:8082
CSRF_TRUSTED_ORIGINS=http://192.168.1.2:8082
REDIS_CONN=redis://:<REDIS PASS HERE>@msgbroker:6379  # 6379 is the default port that Redis listens on

WEB_API_PORT=8082
WEB_API=http://192.168.1.2:8082
WEB_WS=ws://192.168.1.2:8082/ws/

DJANGO_SUPERUSER_USER=<DJANGO USERNAME> # Username to authenticate for Django
DJANGO_SUPERUSER_EMAIL=<DJANGO SUPER USER EMAIL> # Email to use for Django super user.
DJANGO_SUPERUSER_PASSWORD=<DJANGO SUPER USER PASSWORD> # Randomly generated, user-supplied alphanumeric password for the Django Superuser

WORKER_AWS_USER=<AWS Access Key Id> # AWS Credential that can read and write to AWS Secrets Manager
WORKER_AWS_SECRET=<AWS Secret Access Key> # AWS Credential that can read and write to AWS Secrets Manager
WORKER_WEBAPP_HOST=http://web-backend:8000
WORKER_WEBAPP_TOKEN=<LEAVE BLANK FOR NOW, GENERATED LATER IN STEP 6>
WORKER_CSTOR_DATA_DIR=/mnt/cstor_cache
WORKER_REDIS_HOST=msgbroker
WORKER_REDIS_PORT=6379 # Default port that Redis listens on.
WORKER_REDIS_PASSWD=<REDIS_PASS HERE> # Randomly generated, user-supplied alphanumeric password to use for authenticating to Redis
```

From now on we will refer to `~/hackathon/Lyve-Cloud-Solutions-Sample/hackathon-submissions/s3-data-migration-cstor` as `$PROJ`

### Step 5. Setting up Docker and Docker Compose

1. Install dependencies for docker

```bash
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release -y
```

2. Add Docker's Official Keyring

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

3. Setup stable apt repository for docker

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

4. Fetch and install latest packages from docker

```bash
sudo apt-get update -y
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y
```

5. Test installation of Docker

```bash
sudo docker --version

sudo docker run hello-world

sudo docker compose
```

6. Setup all components
```bash
cd $PROJ/main
sudo docker compose up -d
sudo docker ps
```

### Step 6. Create djoser user and token for background worker

The background worker running the S3 bucket migrations require access to the Django REST API to update progress and task status.
We will need to create a new user and token for the background worker using the `siteadmin` superuser account we created in the previous step

1. Login with the superuser account at `http://192.168.1.2:8082/admin`

2. Click on `Users` tab on the left, followed by `Add User Button`

![DB_2](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/dashboard_2.PNG)

![DB_3](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/dashboard_3.PNG)

3. Fill in username and password and click `save` button

![DB_4](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/dashboard_4.PNG)

4. Scroll to the bottom and add the following permissions to the user.

![DB_5](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/dashboard_5_b.PNG)

5. Next, we need to create the token. Click on `Tokens` on the left Sidebar

![DB_6](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/dashboard_6.PNG)

6. Select `dramatiq_worker` in the dropdown and click `Save` button

![DB_7](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/dashboard_7.PNG)

7. Save the generated token somewhere safe

![DB_8](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/dashboard_8.PNG)

### Step 7. Setup and run the Dramatiq background worker

Before we start Step 7, kindly ensure the following is working.
- We have the AWS Credentials for accessing AWS Secrets manager from **Step 2**
- We have the djoser token generated in **Step 6**
- Redis Server is running with docker compose from **Step 5**


3. Setup the environment for the Dramatiq background worker

Update the `.env` file with the generated token from Step 6.

```bash
---SNIPPET---
WORKER_WEBAPP_TOKEN=<REPLACE WITH GENERATED TOKEN IN STEP 6>
---SNIPPET---
```

Then run the following commands,

```bash
$ cd Lyve-Cloud-Solutions-Samples/hackathon-submissions/s3-data-migration-cstor
$ docker compose up -d web-worker-1
```


## Tested by

### `/core`
This folder contains all the cstor-s3 core libraries and is responsible for worker tasks; spawning worker process, updating dashboard API

### `/webapp`
This folder contains the frontend and backend for the web application.

### `/webapp/src/cstor/frontend`
This folder contains the frontend VueJS Application

### `/webapp/src/cstor/dashboard`
This folder contains the backend Django application

