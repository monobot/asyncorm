from asyncorm.models.app_migrator import MigrationBase
from asyncorm.orm_migrations.migration_actions import *


class Migration(MigrationBase):
    initial = True
    depends = [""]
    actions = [
        CreateModel(
            "AsyncormMigrations",
            fields={
                "app_name": {
                    "field_type": "asyncorm.models.fields.CharField",
                    "choices": None,
                    "db_column": "app_name",
                    "db_index": False,
                    "default": None,
                    "max_length": 75,
                    "null": False,
                    "unique": False,
                },
                "name": {
                    "field_type": "asyncorm.models.fields.CharField",
                    "choices": None,
                    "db_column": "name",
                    "db_index": False,
                    "default": None,
                    "max_length": 75,
                    "null": False,
                    "unique": False,
                },
                "applied": {
                    "field_type": "asyncorm.models.fields.DateTimeField",
                    "auto_now": True,
                    "choices": None,
                    "db_column": "applied",
                    "db_index": False,
                    "default": None,
                    "null": False,
                    "format": "%Y-%m-%d  %H:%s",
                    "unique": False,
                },
                "id": {
                    "field_type": "asyncorm.models.fields.AutoField",
                    "choices": None,
                    "db_column": "id",
                    "db_index": False,
                    "default": None,
                    "null": False,
                    "unique": True,
                },
            },
            meta={"ordering": None, "unique_together": [], "table_name": "asyncorm_migrations"},
        )
    ]
