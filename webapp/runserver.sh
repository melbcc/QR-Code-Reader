#!/usr/bin/env sh

# ref: https://stackoverflow.com/questions/59895/#246128
#DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
DIR=$(dirname $0)

cd ${DIR}
./manage.py runserver
