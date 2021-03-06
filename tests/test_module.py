from asyncorm.application.configure import configure_orm, get_model, orm_app
from asyncorm.exceptions import AsyncOrmAppError, AsyncOrmModelError, AsyncOrmModelNotDefined
from asyncorm.test_case import AsyncormTestCase

Book = get_model("Book")

db_config = {"database": "asyncorm", "host": "localhost", "user": "ormdbuser", "password": "ormDbPass"}


class ModuleTests(AsyncormTestCase):
    def test_ormconfigure_no_models(self):
        orm = configure_orm({"db_config": db_config, "apps": None})

        with self.assertRaises(AsyncOrmAppError) as exc:
            orm.get_model("here.what")

        self.assertTrue("There are no apps declared in the orm" == exc.exception.args[0])

    def test_ormconfigure_no_db_config(self):
        with self.assertRaises(AsyncOrmAppError) as exc:
            configure_orm({"apps": ["tests.app_1", "tests.app_2"]})

        self.assertIn("Imposible to configure without database", exc.exception.args[0])

    def test_get_model_not_correct_format(self):
        orm = configure_orm({"db_config": db_config, "apps": ["tests.app_1", "tests.app_2"]})

        with self.assertRaises(AsyncOrmModelError) as exc:
            orm.get_model("here.there.what")

        self.assertIn("The string declared should be in format ", exc.exception.args[0])

    def test_get_model_model_does_not_exist(self):
        with self.assertRaises(AsyncOrmModelNotDefined) as exc:
            get_model("Tato")

        self.assertIn("The model does not exists", exc.exception.args[0])

    def test_the_data_is_persistent_db_backend(self):
        # the orm is configure on the start of tests, but the data is kept
        self.assertEqual(orm_app.db_backend._connection_data["password"], db_config["password"])

    def test_the_data_is_persistent_database(self):
        self.assertEqual(orm_app.db_backend._connection_data["database"], db_config["database"])

    def test_the_data_is_persistent_orm_model(self):
        configure_orm({"db_config": db_config, "apps": ["tests.app_1.appo", "tests.app_2"]})
        # every model declared has the same db_backend
        self.assertTrue(orm_app.db_backend is Book.objects.db_backend)
