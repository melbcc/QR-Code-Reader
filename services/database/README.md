# Database

At this time the service runs `postgres` inside a docker container.

accessible via the connection address:

## Function
  [temporary] serves local database
  
  
```
postgresql+psycopg2://postgres:secret@localhost/mydb?port=5432
```

## Example Commands

**List Members**

To list members in the database:

```
PGPASSWORD=secret psql -h localhost -U postgres -d mydb -c 'SELECT * FROM members;'
```
