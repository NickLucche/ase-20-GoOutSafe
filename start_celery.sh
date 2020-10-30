#!/usr/bin/env sh

celery -A monolith.background worker --loglevel=INFO
