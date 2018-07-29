from asyncorm.application.configure import get_model, orm_app, configure_orm
from asyncorm.exceptions import ModelError, AppError

from tests.test_helper import AioTestCase

Book = get_model("Book")

db_config = {
    "database": "asyncorm",
    "host": "localhost",
    "user": "ormdbuser",
    "password": "ormDbPass",
}


class ModuleTests(AioTestCase):
    def test_ormconfigure_no_models(self):
        orm = configure_orm({"db_config": db_config, "apps": None})

        with self.assertRaises(AppError) as exc:
            orm.get_model("here.what")

        self.assertTrue(
            "There are no apps declared in the orm" == exc.exception.args[0]
        )

    def test_ormconfigure_no_db_config(self):
        with self.assertRaises(AppError) as exc:
            configure_orm({"apps": ["tests.testapp", "tests.testapp2"]})

        self.assertIn("Imposible to configure without database", exc.exception.args[0])

    def test_get_model_not_correct_format(self):
        orm = configure_orm(
            {"db_config": db_config, "apps": ["tests.testapp", "tests.testapp2"]}
        )

        with self.assertRaises(ModelError) as exc:
            orm.get_model("here.there.what")

        self.assertIn("The string declared should be in format ", exc.exception.args[0])

    def test_get_model_model_does_not_exist(self):
        with self.assertRaises(AppError) as exc:
            get_model("Tato")

        self.assertIn("The model does not exists", exc.exception.args[0])

    def test_the_data_is_persistent_db_manager(self):
        # the orm is configure on the start of tests, but the data is kept
        self.assertEqual(
            orm_app.db_manager._conn_data["password"], db_config["password"]
        )

    def test_the_data_is_persistent_database(self):
        self.assertEqual(
            orm_app.db_manager._conn_data["database"], db_config["database"]
        )

    def test_the_data_is_persistent_orm_model(self):
        configure_orm(
            {"db_config": db_config, "apps": ["tests.testapp.appo", "tests.testapp2"]}
        )
        # every model declared has the same db_manager
        self.assertTrue(orm_app.db_manager is Book.objects.db_manager)
