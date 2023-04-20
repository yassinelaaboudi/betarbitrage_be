# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Define working directory in container
WORKDIR /app

# Download necessary Linux libraries
RUN apt-get update && apt-get install -y wget sudo gnupg curl
# from https://nander.cc/using-selenium-within-a-docker-container
# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
# Adding Google Chrome to the repositories
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
# Updating apt to see and install Google Chrome
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# Installing Unzip
RUN apt-get install -yqq unzip
# Download the Chrome Driver
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
# Unzip the Chrome Driver into /usr/local/bin directory
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
# Set display port as an environment variable
ENV DISPLAY=:99


# Copy all python files
COPY /bet_arbitrages/* /app/bet_arbitrages/
COPY teams_correspondancy.csv /app/teams_correspondancy.csv
COPY config.json /app/config.json
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "./bet_arbitrages/main.py"]