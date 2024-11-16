# django-mdb
Django project example using multiple databases.
Docker engine is required.

Generate the env files (and modify where necessary)
```bash
python envs/generate_envs.py
```

Generate the docker-compose.yml file
```bash
python docker/generate_compose.py
```

Start the app in docker:
```bash
docker compose up -d --build
```

Create subfolders in the `media/import` folder with names of versions and add the databases.
```bash
docker compose exec web python manage.py create_databases --migrate
```

List the database versions.
```bash
docker compose exec web python manage.py list_versions
```


Import data from CSV files to different databases
```bash
python manage.py import_products --file csv/products_default.csv # default
python manage.py import_products --ver 1.1.0  --file csv/products_v_1_1_0.csv
python manage.py import_products --ver 1.0.0  --file csv/products_v_1_0_0.csv
```

List data for each database
```bash
python manage.py list_products
python manage.py list_products --ver 1.1.0
python manage.py list_products --ver 1.0.0
```