
class JAssetsRouter:

    def get_db(self, model, **hints):
        if model._meta.app_label == 'jassets_admin':
            return 'jassets'
        return 'default'

    def db_for_read(self, model, **hints):
        return self.get_db(model, **hints)

    def db_for_write(self, model, **hints):
        return self.get_db(model, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        if (obj1._meta.app_label == 'jassets_admin' or
                obj2._meta.app_label == 'jassets_admin'):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'jassets_admin':
            return db == 'jassets'
        return None
