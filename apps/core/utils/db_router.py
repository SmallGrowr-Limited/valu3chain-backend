class CustomDatabaseRouter:
    """
    A router to control all database operations on models.
    """

    def db_for_read(self, model, **hints):
        """
        Direct read operations to the appropriate database.
        """
        if model._meta.app_label in ["data"]:
            return "msdat"
        return "default"

    def db_for_write(self, model, **hints):
        """
        Direct write operations to the appropriate database.
        """
        if model._meta.app_label in ["data"]:
            return "msdat"
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relationships if both models are in the same database.
        """
        db_set = {"default", "msdat"}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Allow migrations for specific apps in their respective databases.
        """
        if app_label in ["data"]:
            return db == "msdat"
        return db == "default"
