CSTOR Dashboard
==========

CSTOR Dashboard for end-users


Deployment for Dashboard (Backend)
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

Configure pypi private repository, add these into `~/.pypirc`

.. code-block:: bash
   :linenos:
   [gitlab]
   repository = https://gitlab.com/api/v4/projects/35836634/packages/pypi
   username = __token__
   password = glpat-TdruBFf9oWM8bgfGMyz8


Then, setup the project dependencies

.. code-block:: bash
   :linenos:
   $ nox -s venv -- init
   $ source .nox/venv/bin/activate

Change `src/cstor/dashboard/settings.py`

ALLOWED_HOSTS = ["<ip of webhost / load balancer>"]

Environment Variables to set:

.. code-block:: bash
   :linenos:
   $ export REDIS_CHANNEL_URL="redis://:<password>@<host>:<port>"


Run migrations

.. code-block:: bash
   :linenos:
   $ cd src/cstor/dasbhoard
   $ python manage.py makemigrations
   # Creates a db.sqlite3 file at the application root
   $ python manage.py migrate


Run server

.. code-block:: bash
   :linenos:
   $ cd src/cstor/dasbhoard
   $ python manage.py runserver 0.0.0.0:8000


Deployment for Frontend
-----------------------

Install npm and nodejs with nvm

.. code-block:: bash
   :linenos:
   $ cd src/cstor/frontend
   $ nvm install 16.15.0
   $ nvm use 16.15.0
   $ npm install

Change settings in `src/cstor/frontend/src/main.js`

.. code-block:: javascript
   :linenos:
   axios.defaults.baseURL = "http://<dashboard_host>:<dashboard_port>";

.. code-block:: javascript
   :linenos:
   createApp(App)
	 .use(store)
	 .use(router, axios)
	 .use(
	   wsService,
	   {
		 store,
		 url: "ws://<dashboard_host>:<dashboard_port>/ws/",
	   })
	 .mount("#app");


Run the frontend server


.. code-block:: bash
   :linenos:
   $ cd src/cstor/frontend
   $ npm run serve
