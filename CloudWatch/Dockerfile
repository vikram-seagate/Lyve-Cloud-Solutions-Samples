# Use the Python3.8 image
FROM python:3.8-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install cron
RUN apt-get -y update && apt-get -y upgrade
RUN apt-get install -y cron

# Install the dependencies
RUN pip3.8 install -r requirements.txt


# Create & Configure Crontab
COPY bubble-cron /etc/cron.d/bubble-cron
RUN service cron start
RUN chmod +x /etc/cron.d/bubble-cron
RUN apt-get -y install vim
RUN crontab /etc/cron.d/bubble-cron
RUN touch /var/log/cron.log

CMD cron && tail -f /var/log/cron.log

# Initial run
CMD ["python", "engine.py"]