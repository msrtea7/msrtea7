---
title: '7DB - PostgreSQL - code'
pubDate: 2025-07-06
author: 'Walbaaco'
tags: ["DB"]
---

# **7DB - PostgreSQL - code**

## **Day 1**

### **Running postgres in my pc**

|Software/Service|Comments|
|---|---|
|[Podman](https://docs.podman.io/en/latest/)|Daemonless container engine|
|[Docker hub](https://hub.docker.com/_/postgres)|Container image registry|
|[libpq](https://www.postgresql.org/docs/current/libpq.html)|PostgreSQL C library, as client|
|[Homebrew](https://brew.sh)|Package manager|

Setup reference as following

```zsh
# Install podman & libpq. 
brew install podman
brew install libpq

# Adding executable to PATH(zsh as example)
echo 'export PATH="/opt/homebrew/bin:$PATH"'  ~/.zshrc
source ~/.zshrc

# Find the postgres image
podman search postgres --filter=is-official

# Pull it
podman pull docker.io/library/postgres

# Run it(full docs at Docker hub)
podman run -d \
	--name postgres-db \
	-e POSTGRES_DB=my_pg_db \
	-e POSTGRES_USER=user \
	-e POSTGRES_PASSWORD=pwd \
	-p 5432:5432 \
postgres

# Connect it
psql -h localhost -p 5432 -d my_pg_db 
```

## **Day 2**

### **Container backup and restore**

Here the following are the steps

```zsh
# Stop old db
podman stop postgres-db

# Back it up
pg_dump -h localhost -p 5432 -d my_pg_db  backup_my_pg_db.sql

# Remove old db
podman rm postgres-db

# Restart the container and mount the directory with your .sql file (no persistence selected here)
podman run -d \
	--name postgres-db \
	-e POSTGRES_DB=my_pg_db \
	-e POSTGRES_USER=msrtea7 \
	-e POSTGRES_PASSWORD=123 \
	-p 5432:5432 \
	-v /Users/msrtea7/Private/ARCHIVE_/ENV_postgres/pg_disk:/sql \
postgres

# Restore the data
psql -h localhost -p 5432 -d my_pg_db < backup_my_pg_db.sq

```


For **pg_dump** backup options, you can choose different formats with command:

```
pg_dump -h localhost -p 5432 -U username -d my_pg_db -Fc  backup_my_pg_db.dump
```

Example options:
- -Fc: custom format, compressed - smaller size and supports parallel restore
- -Ft: tar format
- -Fp: plain text, generates .sql by default

In such cases, use **pg_restore** to restore:
```
pg_restore -h localhost -p 5432 -d my_pg_db backup.dump
```

> Detail with PostgreSQL Client-Server Architecture [PostgreSQL Client-Server Architecture](https://msrtea7.com/posts/academic/7db_pg_file_access/)

### **Homework**

Q1: Create a rule that captures DELETEs on venues and instead sets the active flag (created in the Day 1 homework) to FALSE.

```sql
CREATE RULE venues_soft_delete AS 
ON DELETE TO venues 
DO INSTEAD 
UPDATE venues SET active = FALSE WHERE venue_id = OLD.venue_id;
```

Q2: A temporary table was not the best way to implement our event calendar pivot table. The generate_series(a, b) function returns a set of records, from a to b. Replace the month_count table SELECT with this.

```sql
-- Remove the temporary table creation
-- No need for: CREATE TEMPORARY TABLE month_count...
-- Use generate_series instead

SELECT * FROM crosstab(
'SELECT extract(year from starts) as year,
extract(month from starts) as month, count(*)
FROM events
GROUP BY year, month ORDER BY year, month',
'SELECT generate_series(1, 12)'
) AS (
year int,
jan int, feb int, mar int, apr int, may int, jun int, jul int, aug int, sep int, oct int, nov int, dec int
) ORDER BY YEAR;
```

Q3: Build a pivot table that displays every day in a single month, where each week of the month is a row and each day name forms a column across the top (seven days, starting with Sunday and ending with Saturday) like a standard month calendar. Each day should contain a count of the number of events for that date or should remain blank if no event occurs.

```sql
CREATE OR REPLACE FUNCTION get_monthly_calendar(month_param TEXT)
RETURNS TABLE(
    week_num INT,
    sun INT, mon INT, tue INT, wed INT, thu INT, fri INT, sat INT
) AS $$
DECLARE
    start_date DATE;
    end_date DATE;
    query_text TEXT;
BEGIN
    -- Parse the month parameter (format: 'YYYY-MM')
    start_date := (month_param || '-01')::DATE;
    end_date := (DATE_TRUNC('month', start_date) + INTERVAL '1 month - 1 day')::DATE;
    
    -- Build the query string with properly escaped casting
    query_text := format('SELECT 
        CEIL(EXTRACT(day FROM all_days.day_date) / 7.0) as week_num,
        EXTRACT(dow FROM all_days.day_date) as day_of_week,
        COALESCE(COUNT(e.event_id), 0) as event_count
    FROM generate_series(%L, %L, ''1 day''::interval) as all_days(day_date)
    LEFT JOIN events e ON DATE(e.starts) = all_days.day_date
    GROUP BY week_num, day_of_week
    ORDER BY week_num, day_of_week', 
    start_date, end_date);
    
    -- Return the crosstab result
    RETURN QUERY
    SELECT * FROM crosstab(
        query_text,
        'SELECT generate_series(0, 6)'
    ) AS calendar_result(
        week_num INT,
        sun INT, mon INT, tue INT, wed INT, thu INT, fri INT, sat INT
    );
END;
$$ LANGUAGE plpgsql;
```

## **Day 3**

`SET search_path` to change default schema

Some PostgreSQL Shell Commands:

|Command|Description|
|---|---|
|\l| List all databases |
|\c database_name| Switch/connect to database|
|\dt| List tables in current database|
|\d table_name| Describe table structure|
|\i filename.sql| Execute SQL file|
|\dn| List schemas in current database|
|\dx| List installed extensions|
