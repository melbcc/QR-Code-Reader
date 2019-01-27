# Database

At this time the service runs `postgres` inside a docker container.

accessible via the connection address:

## Install & Start

This implementation used `docker`, so first install docker, then start it up.

```
sudo apt install docker-ce-cli
./start.sh
```

This will start a `postgres` database service accessibe with URI:

```
postgresql+psycopg2://postgres:secret@localhost/mydb?port=5432
```

## Deleting Persistent Data

If you want to start again with a fresh database, you can delete the existing
one by running the `wipe-data.sh` command

```bash
./wipe-data.sh
```

This will simply remove the `data` folder in this directory.


## Example Commands

**pre-requisite**

```bash
sudo apt install postgresql
```

**List Members**

To list members in the database:

```
PGPASSWORD=secret psql -h localhost -U postgres -d mydb -c 'SELECT * FROM members;'
```
