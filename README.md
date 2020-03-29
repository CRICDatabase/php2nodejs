# Migrate database from PHP to Node.js

https://github.com/CRICDatabase/searchable-image-database-php
and
https://github.com/CRICDatabase/searchable-image-database-nodejs
have different database schema.

This repository has scripts to do the migration
from
https://github.com/CRICDatabase/searchable-image-database-php
to
https://github.com/CRICDatabase/searchable-image-database-nodejs.

## Setup

1. Clone the submodules.
2. Download the database dump from the PHP version and save into `php/mysql/initial_data`.
3. Build the containers.

   ```
   $ docker-compose up
   ```

   After the containers been created,
   they will be running.
   To stop the containers,

   ```
   $ docker-compose stop
   ```
4. Create the database used by Node.js version. 

   ```
   $ docker-compose exec node npx sequelize db:create
   $ docker-compose exec node npx sequelize db:migrate
   ```
5. Check that database `cric_ufop` used by PHP version exists.

   ```
   $ docker-compose exec db /bin/bash
   # mysql -p
   > show databases;
   ```

   If database doesn't exist,
   create it.

   ```
   > source DUMP_FILENAME;
6. Install Python dependencies

   ```
   $ python -m pip install -r requirements.txt
   ```

## Steps

1. Launch the containers.

   ```
   $ docker-compose start
   ```
2. Convert database

   ```
   $ python php2node.py --all
   ```

   This will take a couple of hours.
   Instead of access both database directly,
   we access the database used by PHP
   and use the Node.js REST API
   to recreate the database.
   Use HTTP makes the migration very slow
   but allow us to test the Node.js REST API
   and ensure us that our data is in a good state.

## Tips for Developers

1. Add new instructions to `php2node.py`.

   We use the REST API to access the database.
   The documentation of the REST API is available at https://cric-database.readthedocs.io/.
2. If you need to delete existing information,
   run

   ```
   $ docker-compose exec node npx sequelize db:drop
   ```