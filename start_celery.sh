#!/usr/bin/env sh

killall celery
sleep 1
celery -A monolith.background worker --loglevel=INFO -B
#celery -A monolith.background beat --loglevel=INFO &
