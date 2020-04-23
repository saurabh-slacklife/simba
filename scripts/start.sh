#!/bin/bash

if [[ -n ${1} ]]; then
  # Start Gunicorn processes
  echo "Starting Gunicorn."
  echo "Application log path: /var/log/simba/application.log"
  echo "Access log path: /var/log/simba/access.log"
  echo "Environment: ${1}"
  export SERVICE_ENV="${1}"
  mkdir -p /var/log/simba
  touch /var/log/simba/access.log
  touch /var/log/simba/application.log
  touch /var/log/simba/error.log
  exec gunicorn --bind "0.0.0.0:5000" app.manage:simba_flask_app \
    --disable-redirect-access-to-syslog \
    --capture-output \
    --error-logfile /var/log/simba/error.log \
    --log-file /var/log/simba/application.log \
    --access-logfile /var/log/simba/access.log \
    --log-level info
else
  echo "#############################################"
  echo "Service Env not specified process will exit"
  echo "Usage: ./scripts/start.zsh dev"
  echo "#############################################"
  exit 1
fi
