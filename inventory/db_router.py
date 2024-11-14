# inventory/db_router.py

class VersionDatabaseRouter:
    def db_for_read(self, model, **hints):
        return hints.get('database')

    def db_for_write(self, model, **hints):
        return hints.get('database')

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if hints.get('database') == db:
            return True
        return None
