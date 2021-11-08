#!/usr/bin/env bash
docker-compose exec django python manage.py "$@"
