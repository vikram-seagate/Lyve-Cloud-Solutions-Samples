CSTOR Core
==========

CSTOR Core Library for spawning workers

Deployment
----------
0. Install dependencies

First, we need to install nox and poetry in the root Python package

.. code-block:: bash
   :linenos:
   $ pip install nox poetry

Next, we install the dependencies for rocksdb

.. code-block:: bash
   :linenos:
   $ sudo apt-get install -y librocksdb-dev liblz4-dev libsnappy-dev

Then, setup the project dependencies

.. code-block:: bash
   :linenos:
   $ nox -s venv -- init
   $ source .nox/venv/bin/activate

Then set the required environment variables

.. code-block:: bash
   :linenos:
   # Used for retrieving secrets from AWS Secrets
   export AWS_ACCESS_KEY_ID="xxx"
   export AWS_SECRET_ACCESS_KEY="yyy"
   # Dashboard Host information and token
   export WEBAPP_HOST="http://<dashboard_host>:<dashboard_port>"
   export WEBAPP_TOKEN="xxx"
   # Local filepath for the job cache
   export CSTOR_DATA_DIR="/opt/cstor_cache"
   export REDIS_HOST = "<redis_host>"
   export REDIS_PORT = "<redis_port>"
   export REDIS_PASSWD = "<redis_passwd>"

Spawning a worker on the host

.. code-block:: bash
   :linenos:
   $ dramatiq-gevent cstor.s3.tasks.main -p 4 -t 10
