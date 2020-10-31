#!/usr/bin/env sh

celery -A monolith.background worker --loglevel=INFO &
celery -A monolith.background beat --loglevel=INFO &
