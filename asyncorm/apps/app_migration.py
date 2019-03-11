import hashlib
import importlib
import logging
import os
import re
import types
from datetime import datetime

from asyncorm.exceptions import AsyncOrmMigrationError
from asyncorm.orm_migrations.migration_actions import CreateModel

logger = logging.getLogger("asyncorm")


class AppMigration:
    def _check_migration_dir(self, initial=True):
        self.migrations_dir = os.path.join(self.abs_path, "migrations")

        if initial:
            os.makedirs(self.migrations_dir, exist_ok=True)

    async def _construct_migrations_status(self):
        fs_declared = self._fs_migration_list()
        db_migrated = await self._app_db_applied_migrations()

        migrations_status = {}
        for migration in fs_declared:
            migrations_status.update(
                {
                    migration: {
                        "migrated": True if migration in db_migrated else False,
                        "initial": True if "__initial_" in migration else False,
                    }
                }
            )

        try:
            _latest_db_migrated = migrations_status[db_migrated[-1]] if db_migrated else {}
        except KeyError:
            raise AsyncOrmMigrationError(
                'Something went wrong, migration "{}" does not exist in the filesystem.'.format(db_migrated[-1])
            )

        migrations_status.update(
            {
                "_latest_db_migrated": _latest_db_migrated,
                "_latest_fs_declared": migrations_status[fs_declared[-1]] if fs_declared else {},
            }
        )

        return migrations_status

    async def _check_makemigrations_status(self):
        """
        Checks that the migration is correcly synced and everything is fine
        returns the latest migration applied file_name
        """
        _migration_status = await self._construct_migrations_status()
        _latest_db_migrated = _migration_status["_latest_db_migrated"]
        _latest_db_migrated_number = self._migration_integer_number(_latest_db_migrated)
        _latest_fs_declared = _migration_status["_latest_fs_declared"]
        _latest_fs_declared_number = self._migration_integer_number(_latest_fs_declared)

        self._migration_integer_number(_latest_fs_declared)
        # the database doesn't have any migration
        if not _latest_db_migrated:
            if _latest_fs_declared:
                raise AsyncOrmMigrationError(
                    "The model is not in the latest filesystem status, so the migration created will "
                    'not be consistent.\nPlease "migrate" the database before "makemigrations" again.'
                )
        else:
            if not _latest_fs_declared:
                raise AsyncOrmMigrationError(
                    "Severe inconsistence detected, the database has at least one migration applied and no "
                    "migration described in the filesystem."
                )
            if _latest_db_migrated_number > _latest_fs_declared_number:
                raise AsyncOrmMigrationError(
                    'There is an inconsistency, the database has a migration named "{}" '
                    'more advanced than the filesystem "{}"'.format(_latest_db_migrated, _latest_fs_declared)
                )

            elif _latest_db_migrated_number < _latest_fs_declared_number:
                raise AsyncOrmMigrationError(
                    "The model is not in the latest filesystem status, so the migration created will "
                    'not be consistent.\nPlease "migrate" the database before "makemigrations" again.'
                )
            elif _latest_fs_declared != _latest_db_migrated:
                raise AsyncOrmMigrationError(
                    'The migration in the filesystem "{}" is not the same migration '
                    'applied in the database "{}" .'.format(_latest_fs_declared, _latest_db_migrated)
                )

    async def _check_current_migrations_status(self, target):
        self._check_migration_dir()
        _latest_db_migration = self._migration_integer_number(await self._latest_db_migration())

        forward = False
        if target is None:
            target_fs_migration = self._migration_integer_number(self._latest_fs_migration())
        else:
            target_fs_migration = [fn for fn in next(os.walk(self.migrations_dir))[2] if fn.startswith(target)]
        if not target_fs_migration:
            raise AsyncOrmMigrationError("the migration {} does not exist for app {}".format(target, self.name))

        if _latest_db_migration is not None and target_fs_migration is not None:
            if _latest_db_migration > target_fs_migration:
                raise AsyncOrmMigrationError(
                    'There is an inconsistency, the database has a migration named "{}" '
                    'more advanced than the filesystem "{}"'.format(_latest_db_migration, target_fs_migration)
                )
            if _latest_db_migration < target_fs_migration:
                forward = True
        return forward

    def _get_migration(self, migration_name):
        migration_name += ".py"
        migration_path = os.path.join(self.relative_name, "migrations", migration_name)
        _loader = importlib.machinery.SourceFileLoader("Migration", migration_path)
        migration = types.ModuleType(_loader.name)
        _loader.exec_module(migration)
        return migration

    @staticmethod
    def _migration_integer_number(migration_name):
        match = re.search(r"^(?P<m_number>[\d]{4})", migration_name)

        if match:
            return migration_name and int(match.groups("m_number")[0]) or 0
        return 0

    async def _app_db_applied_migrations(self):
        AsyncormMigrations = self.orm.get_model("AsyncormMigrations")
        results = []
        async for res in AsyncormMigrations.objects.filter(app_name=self.name):
            results.append(res)

        return [r.name for r in results] if results else []

    async def _latest_db_migration(self):
        kwargs = {
            "select": "name",
            "table_name": "asyncorm_migrations",
            "join": "",
            "ordering": "ORDER BY -id",
            "condition": "app_name = '{}'".format(self.name),
        }

        result = await self.db_backend.request(self.db_backend._db__select.format(**kwargs))
        return result and result["name"] or ""

    async def _check_migration_applied(self, migration_name):
        kwargs = {
            "select": "*",
            "table_name": "asyncorm_migrations",
            "join": "",
            "ordering": "",
            "condition": "app_name = '{}' AND name = '{}'".format(self.name, migration_name),
        }
        result = await self.db_backend.request(self.db_backend._db__select.format(**kwargs))
        return result

    def _fs_migration_list(self):
        py_ext = ".py"
        self._check_migration_dir()
        return sorted([fn.rstrip(py_ext) for fn in next(os.walk(self.migrations_dir))[2] if fn[-3:] == py_ext])

    def _latest_fs_migration(self):
        filenames = self._fs_migration_list()
        return filenames and filenames[-1] or ""

    def _next_fs_migration_name(self, stage="auto"):
        if stage not in ("auto", "data", "initial"):
            raise AsyncOrmMigrationError("that migration stage is not supported")
        target_fs_migration = self._migration_integer_number(self._latest_fs_migration())
        random_hash = hashlib.sha3_512("{}{}".format(target_fs_migration, str(datetime.now())).encode("utf-8"))
        return "{}__{}_{}".format("0000{}".format(target_fs_migration + 1)[-5:], stage, random_hash.hexdigest()[:20])

    def _get_absolute_migration(self, migration_name):
        return os.path.join(self.abs_path, "migrations", migration_name)

    def _get_migration_actions(self):
        actions = []
        for model_name, model in self.models.items():
            final_migration_state = {}
            current_state = model.current_state()
            if current_state != final_migration_state:
                fields, meta = {}, {}
                if not final_migration_state:
                    action_type = CreateModel
                    fields = current_state["fields"]
                    meta = current_state["meta"]
                else:
                    # not create here
                    action_type = CreateModel
                    for k, value in current_state["fields"].items():
                        if final_migration_state["fields"][k] != value:
                            fields.update({k: value})
                    meta = current_state["meta"]
                actions.append(action_type(model_name, fields, meta))
        return actions

    def _get_migration_depends(self):
        from asyncorm.models import ForeignKey, ManyToManyField

        depends = []
        for _, model in self.models.items():
            if isinstance(model.fields, (ForeignKey, ManyToManyField)):
                pass
        return depends
