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

## Tips for Developers

1. Add new instructions to `src/management/php2node.js`.
2. Before re-run `src/management/php2node.js`,
   you must delete the existing information.

   ```
   $ docker-compose exec node npx sequelize db:drop
   ```

   If you do **not** do it,
   you will duplicate part of the information.