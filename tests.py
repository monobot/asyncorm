import unittest

from exceptions import ModelError, FieldError
from test_models.models import Book, Author


class ModelTests(unittest.TestCase):

    def test__init__(self):
        # classmethods tests
        # self.assertEqual(Book().table_name, 'library')
        # self.assertEqual(Author().table_name, 'author')

        fields, field_names, pk_needed = Book._get_fields()

        self.assertEqual(len(fields), 4)
        self.assertEqual(len(field_names), 4)

        self.assertEqual(
            field_names.sort(),
            ['id', 'content', 'name', 'author', 'date_created'].sort()
        )

    def test_instantiated__init__(self):
        # classmethods tests
        book = Book()

        self.assertEqual(book._fk_db_fieldname, 'id')
        self.assertEqual(book._fk_orm_fieldname, 'id')

        author = Author()

        self.assertEqual(author._fk_db_fieldname, 'uid')
        self.assertEqual(author._fk_orm_fieldname, 'na')

    def test__validate_kwargs(self):
        kwargs = {
            'id': 34,
            'name': 'name',
            'content': 3,
        }

        # raises the validate content has an incorrect value
        with self.assertRaises(FieldError):
            book = Book()
            book._validate(kwargs)
        kwargs['content'] = 'correct content'

        # also raises fielderror because you can not pre-set the object's id
        with self.assertRaises(FieldError):
            book = Book()
            book._validate(kwargs)
        kwargs.pop('id')

        kwargs['volume'] = 23
        # raises the validate error because volume is not a correct attrib
        with self.assertRaises(ModelError):
            book = Book()
            book._validate(kwargs)
        kwargs.pop('volume')

        # now it correctly validates
        book._validate(kwargs)

    # def test__db_save(self):
    #     from datetime import datetime

    #     book = Book(**{
    #         'name': 'name asigned',
    #         'content': 'content asigned',
    #         'date_created': datetime.now(),
    #         # 'author': 1
    #     })
    #     book._db_save()


if __name__ == '__main__':
    unittest.main()
