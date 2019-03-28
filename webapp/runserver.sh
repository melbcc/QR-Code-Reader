#!/usr/bin/env bash

# ref: https://stackoverflow.com/questions/59895/#246128
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd ${DIR}
./manage.py runserver
