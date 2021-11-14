#!/usr/bin/env bash
set -e
rsa_key_size=4096
path=$(dirname $0)

openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1 \
    -keyout "$path/privkey.pem" \
    -out "$path/fullchain.pem" \
    -subj "/CN=localhost"
