FROM python:3.10.4-buster as cstor_core
ARG DEBIAN_FRONTEND=noninteractive

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

#RUN poetry install -vvv
# Builds to /app/dist/cstor_s3-<version>-py3-none-any.whl
RUN poetry build -f wheel

FROM python:3.10.4-buster as cstor-worker
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y
RUN apt-get install -y librocksdb-dev liblz4-dev libsnappy-dev

RUN mkdir -p /app
WORKDIR /app

RUN python3 -m venv .venv
ENV PATH="/app/.venv/bin:$PATH"

COPY --from=cstor_core /app/dist/cstor_s3-0.4.5-py3-none-any.whl /app/cstor_s3-0.4.5-py3-none-any.whl

RUN pip install /app/cstor_s3-0.4.5-py3-none-any.whl

ENV DRAMATIQ_PROCESSES=4
ENV DRAMATIQ_THREADS=4

ADD worker-entrypoint.sh /app/entrypoint.sh
RUN chmod 0700 /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
