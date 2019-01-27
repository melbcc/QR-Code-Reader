#!/usr/bin/env bash

# ref: https://stackoverflow.com/questions/59895/#246128
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# create data folder
if [ ! -d ${DIR}/data ] ; then mkdir -p ${DIR}/data ; fi

docker run \
    --volume ${DIR}/data:/var/lib/postgresql/data \
    -e POSTGRES_PASSWORD=secret \
    -e POSTGRES_DB=mydb \
    -p 5432:5432 \
    --rm -it postgres
