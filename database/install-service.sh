#!/usr/bin/env bash

SERVICE_NAME="qrcode-db"
SERVICE_LINK="/etc/init.d/${SERVICE_NAME}"

# ref: https://stackoverflow.com/questions/59895/#246128
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Add as service
if [ ! -e "${SERVICE_LINK}" ] ; then
    sudo ln -s "${DIR}/service.sh" "${SERVICE_LINK}"
    sudo update-rc.d "$SERVICE_NAME" defaults
fi
