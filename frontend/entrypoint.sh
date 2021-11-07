#!/bin/sh
if [ -d "$VUE_OUTPUT_DIR" ] ; then
    # Set output directory to all access
    # Why?: because vue build runs with host's user id (`id -u`)
    #   who does not have write access.
    chmod -R 777 "$VUE_OUTPUT_DIR"
    # FIXME: I'm sure there's a better way to do this.
fi
npm install
exec "$@"
