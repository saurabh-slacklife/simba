#!/bin/bash

if [[ -n ${1} ]]; then
  # Start Gunicorn processes
  echo "Starting Gunicorn."
  echo "Application log path: /tmp/log/simba/application.log"
  echo "Access log path: /tmp/log/simba/access.log"
  echo "Environment: ${1}"
  export SERVICE_ENV="${1}"
  mkdir -p /tmp/log/simba
  touch /tmp/log/simba/access.log
  touch /tmp/log/simba/application.log
  exec gunicorn --bind "0.0.0.0:5000" main.app:flask_app
else
  echo "#############################################"
  echo "Service Env not specified process will exit"
  echo "Usage: ./scripts/start.zsh dev"
  echo "#############################################"
  exit 1
fi



