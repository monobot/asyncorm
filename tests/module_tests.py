from asyncorm.application import get_model, orm_app, configure_orm
from asyncorm.exceptions import ModelError, ModuleError

from .test_helper import AioTestCase

Book = get_model('Book')

db_config = {
    'database': 'asyncorm',
    'host': 'localhost',
    'user': 'ormdbuser',
    'password': 'ormDbPass',
}


class ModuleTests(AioTestCase):

    def test_ormconfigure(self):
        orm = configure_orm({
            'db_config': db_config,
            'modules': None,
        })
        with self.assertRaises(ModuleError) as exc:
            orm.get_model('here.there.what')
        self.assertTrue(
            'There are no modules declared in the orm' == exc.exception.args[0]
        )
        with self.assertRaises(ModuleError) as exc:
            configure_orm({
                # 'db_config': db_config,
                'modules': ['tests.testapp', 'tests.testapp2'],
            })
        self.assertTrue(
            'Imposible to configure without database' in exc.exception.args[0]
        )

        orm = configure_orm({
            'db_config': db_config,
            'modules': ['tests.testapp', 'tests.testapp2'],
        })
        with self.assertRaises(ModelError) as exc:
            orm.get_model('here.there.what')
        self.assertTrue(
            'The string declared should be in format ' in exc.exception.args[0]
        )

    def test_configuration(self):
        with self.assertRaises(ModuleError) as exc:
            get_model('Tato')
        self.assertTrue('The model does not exists' in exc.exception.args[0])

        # the orm is configure on the start of tests, but the data is kept
        self.assertEqual(
            orm_app.db_manager.conn_data['password'],
            db_config['password']
        )
        self.assertEqual(
            orm_app.db_manager.conn_data['database'],
            db_config['database']
        )

        # every model declared has the same db_manager
        self.assertTrue(orm_app.db_manager is Book.objects.db_manager)
