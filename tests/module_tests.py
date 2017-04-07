import asyncio
import unittest

from asyncorm.application import get_model, orm_app
from asyncorm.exceptions import *
from asyncorm.fields import *

from .test_helper import AioTestCase

Book = get_model('Book')

db_config = {
    'database': 'asyncorm',
    'host': 'localhost',
    'user': 'sanicdbuser',
    'password': 'sanicDbPass',
}


class ModuleTests(AioTestCase):

    def test_configuration(self):
        with self.assertRaises(ModuleError) as exc:
            get_model('Tato')
        self.assertTrue(
            'The model does not exists' in exc.exception.args[0]
        )

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
