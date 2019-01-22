#!/usr/bin/env bash

docker run \
    -e POSTGRES_PASSWORD=secret \
    -e POSTGRES_DB=mydb \
    -p 5432:5432 \
    --rm -it postgres
