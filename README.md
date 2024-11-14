# django-mdb
Django project example using multiple databases

Apply migrations to all databases 
```bash
python manage.py migrate_all
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