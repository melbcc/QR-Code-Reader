#!/usr/bin/env bash

# create data folder
if [ ! -d data ] ; then mkdir -p data ; fi

docker run \
    --volume ${PWD}/data:/var/lib/postgresql/data \
    -e POSTGRES_PASSWORD=secret \
    -e POSTGRES_DB=mydb \
    -p 5432:5432 \
    --rm -it postgres
