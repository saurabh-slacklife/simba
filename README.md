# Simba - A Flask wireframe for OAuth 2.0 implementation backed by Redis and Elasticsearch

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg?style=plastic&color=brightgreen)](https://www.python.org/) [![Version 3.8.2](https://img.shields.io/badge/python-3.8.2-blue.svg?style=plastic&color=brightgreen)](https://www.python.org/downloads/release/python-382//)

![Docker Build](https://github.com/saurabh-slacklife/simba/workflows/Docker%20Build/badge.svg)

## Table of contents
* [Installation](#Installation)
    * [OS X & Linux](#os-x-&-linux)
        *  [With Pipenv](#with-pipenv)
* [Build and run](#Build-and-run)
    * [Using Docker](#Using-Docker)
    * [Using shell script](#Using-shell-script)
* [Logs](#logs)
    * [Local system](#local-system)
    * [Docker](#docker)
* [Release History](#Release-History)
* [Issue List](#issue-list)
* [Contribute](#Contribute)

## Installation

### Setup virtual env

####OS X & Linux:

##### With Pipenv

```shell script
# Update Pip
pip install --upgrade pip --no-cache

# Install pipenv
pip install pipenv

# Install dependencies and Virtualenv based on Pipfile
pipenv install --deploy --ignore-pipfile
```

## Build and run

### Using Docker

The service is Docker'zed. Below are the steps to build and run the Docker image.

```shell script
# Below command builds the Docker image.
docker build . -f container/Dockerfile-dev -t simba:v1

# Below command runs the docker image on port 5000.
# Sets the SERVICE_ENV environment variable in Docker container.
# The value "dev" is used to take Development configuration.
docker run -p 5000:5000 --env-file ./env.dev PORT=5000 ripple.io:v1

```

env.dev Sample
```.env
SERVICE_ENV=dev
```

### Using shell script

Run below commands to run the Microservice from shell script in background.

```shell script
export SERVICE_ENV="dev" # Runs the application in Development configuration. Change to "qa" or "prod" based on environment.
chmod +x start.sh
nohup ./scripts/start.sh ${SERVICE_ENV} &
```

## Logs

### Local system
```shell script
# Navigate to path /var/log/simba
cd /var/log/simba

# Gunicorn access logs path
tail -f /var/log/simba/access.log

# Application log path
tail -f /var/log/simba/application.log
```

### Docker
```shell script
# Find the docker CONTAINER_ID based on the Image tag: ripple.io:v1
docker ps | grep "simba:v1" | cut -d" " -f1

# Access the docker shell
docker exec -it <CONTAINER_ID> /bin/sh

# Navigate to path /var/log/ripple
cd /var/log/simba

# Gunicorn access logs path
tail -f /var/log/simba/access.log

# Application log path
tail -f /var/log/simba/application.log
```

## Release History
//TODO
* 1.0.0
[[Unreleased]]

## Issue List
[Current Issues](https://github.com/saurabh-slacklife/simba/issues)

## Contribute

If you want to be a contributor please follow the below steps.

1. Fork it (<https://github.com/saurabh-slacklife/simba/fork>)
2. Create your feature branch (`git checkout -b feature/add-feature-xyz`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/add-feature-xyz`)
5. Create a new Pull Request