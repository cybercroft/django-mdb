#!/bin/bash
set -e

# Read DB_VERSIONS environment variable and split by comma
IFS=',' read -ra DB_NAMES <<< "$DB_VERSIONS"

# Prefix for the databases
DB_PREFIX="db_"

# Create each database with the prefix
for DB_NAME in "${DB_NAMES[@]}"; do
    FULL_DB_NAME="${DB_PREFIX}${DB_NAME}"
    echo "Creating database: $FULL_DB_NAME"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<-EOSQL
        CREATE DATABASE "$FULL_DB_NAME";
EOSQL
done
