#!/bin/bash


. /app/.venv/bin/activate


dramatiq-gevent cstor.s3.tasks.main -p ${DRAMATIQ_PROCESSES} -t ${DRAMATIQ_THREADS}
