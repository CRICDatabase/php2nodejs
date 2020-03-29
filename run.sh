#!/bin/bash
# Clean image files
sudo rm -rf nodejs/src/assets/imagens/base_externa/*
sudo rm -rf nodejs/src/assets/imagens/base_interna/*
sudo rm -rf nodejs/src/assets/imagens/base_thumbnail/*
# Clean database
docker-compose exec node npx sequelize db:drop
docker-compose exec node npx sequelize db:create
docker-compose exec node npx sequelize db:migrate
# Add required seeders
docker-compose exec node npx sequelize db:seed --seed 20200325200000-lesion.js
docker-compose exec node npx sequelize db:seed --seed 20200325220000-description.js
# Add special user for migration
docker-compose exec node npx sequelize db:seed --seed 20200501000000-php2nodejs-user.js
docker-compose exec node npx sequelize db:seed --seed 20200501010000-php2nodejs-admin.js
docker-compose exec node npx sequelize db:seed --seed 20200501020000-php2nodejs-cytopathologist.js
docker-compose exec node npx sequelize db:seed --seed 20200501030000-php2nodejs-analyst.js
# Run migration.
python php2nodejs.py --all
