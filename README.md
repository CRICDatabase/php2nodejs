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

## Steps

1. Clone the submodules.
2. Download the database dump from the PHP version and save into `php/mysql/initial_data`.
3. Build the containers.

   ```
   $ docker-compose up
   ```
4. Create the database used by Node.js version. 

   ```
   $ docker-compose exec node npx sequelize db:create
   $ docker-compose exec node npx sequelize db:migrate
   ```
5. Check that databas used by PHP version exists.

   ```
   $ docker-compose exec db /bin/bash
   # mysql -p
   > show databases;
   ```

   If database doesn't exist,
   create it.

   ```
   > source DUMP_FILENAME;
   ```
6. Convert database

   ```
   $ docker-compose exec node node src/management/php2node.js
   ```