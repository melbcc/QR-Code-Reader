# Event Attendance Frontend

This is the front-end of the MelbPC event attendance scanner (previously
the "QR-Code Reader")

In development, this app' runs in its own docker container.
To start it, follow in instructions from the [project readme](../README.md).

## Working with vue-cli or npm

All libs and vue CLI commands should be done from within the docker container.
To do so, from the project directory:

```bash
docker-compose exec frontend sh
```

This will open a shell from inside the already running container.

Note: the `/code` directory in the container is this `<repo>/frontend` directory.

### NPM add dependency
```
npm install <lib> --save
```
