#!/bin/sh
set -u

# TODO: Ideally should be a kubernetes cronjob, but this is a simple workaround for now.
while true; do
  app cron || echo "app cron exited with status $?" >&2
  sleep 1800
done
