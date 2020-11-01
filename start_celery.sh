#!/usr/bin/env sh

pkill celery
sleep 1
celery -A monolith.background worker --loglevel=INFO &
celery -A monolith.background beat --loglevel=INFO &
