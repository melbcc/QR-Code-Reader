#!/usr/bin/env bash
# Environment script for setting up production environment.
# Intended to be used from .. like this:
#   $ source env/prod.sh

export COMPOSE_FILE=.dc.prod.yml
