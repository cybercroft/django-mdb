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

Import data from CSV files for all databases
```bash
python manage.py import_products
```

Import data from CSV files per database
```bash
python manage.py import_products --ver 1.0.0
```

List data for all databases
```bash
python manage.py list_products
```

List data per database
```bash
python manage.py list_products --ver 1.0.0
```