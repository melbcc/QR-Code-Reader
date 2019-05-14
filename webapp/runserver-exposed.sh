#!/usr/bin/env bash

# ref: https://stackoverflow.com/questions/59895/#246128
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
IP=$(ip route get 8.8.8.8 | awk '{print $NF; exit}')

cd ${DIR}
./manage.py runserver $IP:8000
