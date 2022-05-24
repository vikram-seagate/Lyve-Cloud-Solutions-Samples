# CSTOR S3 Data Migration

![CSTOR_UI](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/ui_1.PNG)

[Demo Video](https://4pqfyjuvjh.vmaker.com/record/7cYOqhUSba0EjQSU)

## Introduction
CSTOR S3 Data Migration solution consists of a dashboard frontend, webserver backend by Django and background workers powered by Dramatiq.Signed


## Requirements

### Minimum Specs
- Ubuntu 20.04
- 2 vCPUs
- 4 GB Ram
- 80GB NVMe SSD
- 1gb/s Ethernet

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

### Step 1. Retrieve required credentials for AWS and Lyvecloud S3 Buckets

Credentials must have the required permissions and endpoints as per the **Credentials** section above.

### Step 2. Create the AWS Credentials for reading and writing to AWS Secrets Manager
1. Login to AWS and go over to [IAM](https://console.aws.amazon.com/iamv2/home).

![AWS_1](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/aws_1.PNG)

2. Click on `Users` on the left sidebar and then `Add User`

![AWS_2](https://github.com/codewitholi/lyc-hackathon-pages/blob/main/aws_2.PNG)

![AWS_3](https://github.com/codewitholi/lyc-hackathon-pages/blob/main/aws_3.PNG)

3. Fill in the username and select `AccessKey - Programmatic Access` for the AWS Access Type

![AWS_4](https://github.com/codewitholi/lyc-hackathon-pages/blob/main/aws_4.PNG)

4. On Set Permissions, Click `Attach Existing Policies Directly` and tick `SecretsManagerReadWrite`

![AWS_5](https://github.com/codewitholi/lyc-hackathon-pages/blob/main/aws_5.PNG)

![AWS_6](https://github.com/codewitholi/lyc-hackathon-pages/blob/main/aws_6.PNG)

5. Review the created details and click on `Create user` button

![AWS_7](https://github.com/codewitholi/lyc-hackathon-pages/blob/main/aws_7.PNG)

6. Save the generated `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

![AWS_8](https://github.com/codewitholi/lyc-hackathon-pages/blob/main/aws_8_censored.jpg)


Please note that you will not be able to see the secret key again after leaving the page.

### Step 3. Install Git

```bash
$ sudo apt-get update -y; sudo apt-get install git
```

### Step 4. Clone the project repo

```bash
$ mkdir ~/hackathon
$ cd ~/hackathon
$ git clone https://github.com/codewitholi/Lyve-Cloud-Solutions-Samples.git
$ cd Lyve-Cloud-Solutions-Sample/integration-template
```

From now on we will refer to `~/hackathon/Lyve-Cloud-Solutions-Sample/integration-template` as `$PROJ`

### Step 5. Setting up Docker and Docker Compose for Redis Server

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

6. Setup Redis Instance with docker compose

```bash
cd $PROJ/core
sudo docker compose up -d
sudo docker ps

CONTAINER ID   IMAGE              COMMAND                  CREATED         STATUS         PORTS                                         NAMES
27a1fe55f168   redis:6.2-alpine   "docker-entrypoint.s…"   7 seconds ago   Up 6 seconds   0.0.0.0:16379->6379/tcp, :::16379->6379/tcp   core-broker-1
```

7. Test connecting to Redis Instance

```bash
telnet 127.0.0.1 16379

> keys *
-NOAUTH Authentication required.
```

Redis Instance setup is completed.

### Step 6. Installing Python 3.10.1 and setting up Django Dashboard REST API Server

We recommend using pyenv to install Python on the system, instructions below.

1. Install python build dependencies

```bash
sudo apt-get -y install make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

2. Install pyenv with the setup script

```bash
curl https://pyenv.run | bash
```

3. Add the following line to ~/.bashrc

```bash
eval "$(pyenv virtualenv-init -)"
```

4. Add the following line to ~/.profile and ~/.bash_profile

```bash
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

5. Load the new environment with `bash` and test pyenv

```bash
$ bash
$ which pyenv
```

6. Install Python 3.10.1

```bash
pyenv install 3.10.1
pyenv global 3.10.1

which python
> /home/<user>/.pyenv/shims/python

python --version
> Python 3.10.1
```

7. Install nox (script automation) and poetry (package manager)

```bash
pip install nox poetry
```

8. Install rocksdb dependencies

```bash
sudo apt-get install -y librocksdb-dev liblz4-dev libsnappy-dev
```

9. Add private repo dependencies to Poetry

Add the following lines to `~/.pypirc`

```bash
[gitlab]
repository = https://gitlab.com/api/v4/projects/35836634/packages/pypi
username = __token__
password = glpat-sexaxPLC88ed3AXs7_oV
```

Run the following commands

```bash
poetry config repositories.gitlab https://gitlab.com/api/v4/projects/35836634/packages/pypi/simple
poetry config http-basic.gitlab __token__  glpat-sexaxPLC88ed3AXs7_oV
```

11. Install Django and other dependencies for **Dashboard Backend**

This will create a new Python virtualenv at `$PROJ/webapp/.nox/venv`

```bash
cd $PROJ/webapp
nox -s venv -- init

# Load the virtual environment
source .nox/venv/bin/activate

(venv)$
```

12. Create the local sqlite3 database for Django

```bash
(venv)$ cd $PROJ/webapp/src/cstor/dashboard

(venv)$ python manage.py migrate
```

13. Create a new superuser for Django Admin

```bash
(venv)$ python manage.py createsuperuser

Username (leave blank to use 'kirito'): siteadmin
Email address:
Password:
Password (again):
Superuser created successfully.
```

14. Edit the ALLOWED_HOSTS variable in `$PROJ/webapp/src/cstor/dashboard/dashboard/settings.py`

```python
# Change this
ALLOWED_HOSTS = ["<server_public_ip>"]
```

15. Start the dashboard backend with the following command:

```bash
(venv)$ python manage.py runserver 0.0.0.0:8000
```

Check that we are able to access the admin dashboard at `http://<server_public_ip>:8000/admin`

![DB_1](https://github.com/codewitholi/lyc-hackathon-pages/raw/main/dashboard_1.PNG)

### Step 7. Create djoser user and token for background worker

The background worker running the S3 bucket migrations require access to the Django REST API to update progress and task status.
We will need to create a new user and token for the background worker using the `siteadmin` superuser account we created in the previous step

1. Login with the superuser account at `http://<server_public_ip>:8000/admin`

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

### Step 8. Setup and run the Dramatiq background worker

Before we start Step 8, kindly ensure the following is working.
- Django REST API is up and running at http://<server_public_up>:8000
- We have the AWS Credentials for accessing AWS Secrets manager from **Step 2**
- We have the djoser token generated in **Step 7**
- Redis Server is running with docker compose from **Step 5**
- Python 3.10.1 and RocksDB dependencies is installed from **Step 6**

1. Create the data directory for the Dramatiq background worker

```bash
sudo mkdir -p /opt/cstor_cache
sudo chown <user>: -R /opt/cstor_cache
```

2. Install python dependencies for the background worker

This will create a new virtualenv in $PROJ/core/.nox/venv

```bash
# IMPORTANT! Run deactivate if we are still in the previous virtualenv
(venv)$ deactivate
$
#
cd $PROJ/core

nox -s venv -- init

source .nox/venv/bin/activate

(venv)$
```

3. Setup the environment for the Dramatiq background worker

Place the following lines in `worker.env`

```bash
# AWS Credentials to access AWS Secrets Manager from Step 2
export AWS_ACCESS_KEY_ID="xxx"
export AWS_SECRET_ACCESS_KEY="yyy"
# Dashboard Backend Host
export WEBAPP_HOST="http://<server_public_ip>:8000"
# Dashboard Backend Token for Dramatiq Worker from Step 7
export WEBAPP_TOKEN="<token>"
# Local filepath for the job cache
export CSTOR_DATA_DIR="/opt/cstor_cache"
export REDIS_HOST="127.0.0.1"
export REDIS_PORT="16379"
export REDIS_PASSWD="Test123!"
```

Then run the following command

```bash
(venv)$ source worker.env
```

4. Start the Dramatiq background worker with 4 processes and 10 threads each

```bash
dramatiq-gevent cstor.s3.tasks.main -p 4 -t 10
```

The Dramatiq background worker is now running!

### Step 9. Setup the Frontend (VueJS)

We recommend installing using the nvm (Node Version Manager) tool

1. Use the nvm installer script

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
```

2. Enter into a new bash session to have `nvm` in PATH

```bash
bash
```

3. Install NodeJS v16.15.0

```bash
nvm install 16.15.0
nvm use 16.15.0
```

4. Install frontend dependencies

```bash
cd $PROJ/webapp/src/cstor/frontend

npm i
```

5. Edit the server ip in `$PROJ/webapp/src/cstor/frontend/src/main.js`

```javascript
// Change this!
axios.defaults.baseURL = "http://<server_public_ip>:8000";

createApp(App)
  .use(store)
  .use(router, axios)
  .use(
    wsService,
    {
      store,
      url: "ws://<server_public_ip>:8000/ws/",  // Change this!
    })
  .mount("#app");
```

6. Start the frontend service

```bash
cd $PROJ/webapp/src/cstor/frontend

npm run serve
```

The frontend is now serving at `http://<server_public_ip>:8080`


## Tested by

### `/core`
This folder contains all the cstor-s3 core libraries and is responsible for worker tasks; spawning worker process, updating dashboard API

### `/webapp`
This folder contains the frontend and backend for the web application.

### `/webapp/src/cstor/frontend`
This folder contains the frontend VueJS Application

### `/webapp/src/cstor/dashboard`
This folder contains the backend Django application

