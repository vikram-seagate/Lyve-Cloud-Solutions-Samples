FROM python:3.8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ADD requirements.txt .
RUN python -m pip install -r requirements.txt
VOLUME [ "/data" ]
WORKDIR /app
ADD . /app
