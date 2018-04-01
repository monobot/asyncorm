class MigrationAction:
    pass


class FieldMigration(MigrationAction):
    def __init__(self, field_name, field_kwargs, state={}):
        self.renamed = False
        self.current_state = self._get_current_state(state)

        self.field_name = field_name
        self.field_kwargs = field_kwargs

    def _migrate_kwargs(self, migration_action):
        self.current_state.update(migration_action.field_kwargs)

    def _migrate_name(self, migration_action):
        current_field_name = self.field_name
        new_field_name = migration_action.field_name
        self.renamed = new_field_name != current_field_name
        self.field_name = new_field_name

    def _migrate_to(self, migration_action):
        self._migrate_kwargs(migration_action)
        self._migrate_name(migration_action)

    def _get_current_state(self, state):
        return state.update(self.field_kwargs)


class CreateField(FieldMigration):
    pass


class AlterField(FieldMigration):
    pass


class RenameField(FieldMigration):
    pass


class RemoveField(FieldMigration):
    def __init__(self, field_name):
        self.field_name = field_name
        self.field_kwargs = {}


class ModelMigration(MigrationAction):
    def __init__(self, model_name, fields, meta):
        self.renamed = False
        self.model_name = model_name
        self.fields = fields
        self.meta = meta


class CreateModel(ModelMigration):
    pass


class AlterModel(ModelMigration):
    pass


class RemoveModel(ModelMigration):
    def __ini__(self, model_name):
        self.model_name = model_name
        self.fields = {}
        self.meta = {}


class MigrationBase:
    initial = False
    depends = []
    actions = []
