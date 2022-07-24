FROM python:3.10.0-buster

RUN apt-get update -y
RUN apt-get install librocksdb-dev liblz4-dev libsnappy-dev -y
