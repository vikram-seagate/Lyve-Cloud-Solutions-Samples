FROM python:3.10.4-buster

RUN apt-get update -y

RUN apt-get install -y librocksdb-dev liblz4-dev libsnappy-dev

RUN pip install poetry==1.1.13

RUN mkdir /app

WORKDIR /app

ADD src /app/src
ADD poetry.lock /app/poetry.lock
ADD pyproject.toml /app/pyproject.toml

RUN poetry install

ENV DRAMATIQ_PROCESSES=4
ENV DRAMATIQ_THREADS=4

ENTRYPOINT ["dramatiq-gevent", "cstor.s3.tasks.main", "-p", ${DRAMATIQ_PROCESSES}, "-t", ${DRAMATIQ_THREADS}]
