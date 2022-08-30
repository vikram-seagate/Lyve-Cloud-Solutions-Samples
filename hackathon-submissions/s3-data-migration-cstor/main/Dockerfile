FROM python:3.10.4-buster as cstor_core
ARG DEBIAN_FRONTEND=noninteractive
ARG CORE_VERSION=0.4.6

RUN apt-get update -y
RUN apt-get install -y librocksdb-dev liblz4-dev libsnappy-dev

RUN mkdir /app
WORKDIR /app

RUN python3 -m venv .venv
ENV PATH="/app/.venv/bin:$PATH"

RUN pip install nox==2022.1.7 poetry==1.1.13 wheel --no-cache-dir

ADD core/src /app/src
ADD core/poetry.lock /app/poetry.lock
ADD core/pyproject.toml /app/pyproject.toml

RUN poetry config virtualenvs.create false
RUN poetry config virtualenvs.in-project true

ADD core/noxfile.py /app/noxfile.py

RUN nox -s venv -- init

# Builds to /app/dist/cstor_s3-<version>-py3-none-any.whl
RUN poetry build -f wheel

# CSTOR Worker Image
FROM python:3.10.4-buster as cstor-worker
ARG CORE_VERSION=0.4.6
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y
RUN apt-get install -y librocksdb-dev liblz4-dev libsnappy-dev

RUN mkdir -p /app
WORKDIR /app

RUN python3 -m venv .venv
ENV PATH="/app/.venv/bin:$PATH"

COPY --from=cstor_core /app/dist/cstor_s3-$CORE_VERSION-py3-none-any.whl /app/cstor_s3-$CORE_VERSION-py3-none-any.whl

RUN pip install /app/cstor_s3-$CORE_VERSION-py3-none-any.whl

ENV DRAMATIQ_PROCESSES=4
ENV DRAMATIQ_THREADS=4

ADD worker-entrypoint.sh /app/entrypoint.sh
RUN chmod 0700 /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]

# CSTOR Web Backend Essentials (Django)
FROM python:3.10.4-buster as cstor-web-essentials
ARG CORE_VERSION=0.4.6
RUN apt-get update -y
RUN apt-get install -y librocksdb-dev liblz4-dev libsnappy-dev

RUN mkdir -p /app/deps
WORKDIR /app

RUN python3 -m venv .venv
ENV PATH="/app/.venv/bin:$PATH"

RUN pip install nox==2022.1.7 poetry==1.1.13 wheel --no-cache-dir

ADD webapp/src /app/src
ADD webapp/poetry.lock /app/poetry.lock
ADD webapp/pyproject.toml /app/pyproject.toml

COPY --from=cstor_core /app/dist/cstor_s3-$CORE_VERSION-py3-none-any.whl /app/deps/cstor_s3-$CORE_VERSION-py3-none-any.whl

RUN poetry config virtualenvs.create false
RUN poetry config virtualenvs.in-project true

ADD webapp/noxfile.py /app/noxfile.py

RUN nox -s venv -- init

RUN mkdir -p /mnt/data
RUN mkdir -p /var/www/webapp/static

# For hosting Django Server
FROM cstor-web-essentials as cstor-web-backend

ADD web-backend-entrypoint.sh /app/entrypoint.sh
RUN chmod 0700 /app/entrypoint.sh

WORKDIR /app/src/cstor/dashboard

CMD ["/app/entrypoint.sh"]

# For creating Django migrations
FROM cstor-web-essentials as cstor-web-backend-migrate

ADD web-backend-migrate-entrypoint.sh /app/entrypoint.sh
RUN chmod 0700 /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]

FROM node:lts-alpine as frontend-build
RUN mkdir -p /var/www/webapp/frontend

WORKDIR /app
ADD webapp/src/cstor/frontend /app

RUN npm install

#RUN npm run build

#RUN cp -R /app/dist/* /var/www/webapp/frontend/

ADD web-frontend-entrypoint.sh /app/entrypoint.sh
RUN chmod 0700 /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
