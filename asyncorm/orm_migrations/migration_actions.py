class MigrationAction:
    pass


class FieldMigration(MigrationAction):
    def __init__(self, field_name, field_kwargs, state=None):
        self.current_state = self._get_current_state(state)

        self.field_name = field_name
        self.field_kwargs = field_kwargs

        self.state = state or dict()

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
    def __init__(self, model_name="", fields="", meta=""):
        self.model_name = model_name
        self.fields = fields
        self.meta = meta


class CreateModel(ModelMigration):
    pass


class RemoveModel(ModelMigration):
    def __init__(self, model_name):
        self.model_name = model_name
