# Database

At this time the service runs `postgres` inside a docker container.

accessible via the connection address:

## Install & Run

### Run Locally

This implementation used `docker`, so first install docker, then start it up.

```
sudo apt install docker-ce-cli
./run.sh
```

This will start a `postgres` database service accessibe with URI:

```
postgresql+psycopg2://postgres:secret@localhost/mydb?port=5432
```

### Run as Service: `qrcode-db`

To set up permenantly on a system (ie: the intended target):

```bash
./install-service.sh
```

If installation of the service worked, you should be able to run

```bash
# check status
service qrcode-db status

# and control
service qrcode-db start
service qrcode-db stop
service qrcode-db restart
```

The service should also start automatically on boot.

## Deleting Persistent Data

If you want to start again with a fresh database, you can delete the existing
one by running the `wipe-data.sh` command

```bash
./wipe-data.sh
```

This will simply remove the `data` folder in this directory.


## Direct Database Access

Sometimes direct access to the database is required for low-level debugging.

**Install `psql` command**

```bash
sudo apt install postgresql
```

**Open a PostgreSQL console:**

```
PGPASSWORD=secret psql -h localhost -U postgres -d mydb
```
