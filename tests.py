import unittest

from exceptions import ModelError, FieldError
from test_models.models import Book


class ModelTests(unittest.TestCase):

    def test_init(self):
        # self.assertEqual(Book().table_name, 'library')
        # self.assertEqual(Author().table_name, 'author')

        fields, field_names, pk_needed = Book._get_fields()

        self.assertEqual(len(fields), 4)
        self.assertEqual(len(field_names), 4)

        self.assertEqual(
            field_names.sort(),
            ['id', 'content', 'name', 'author', 'date_created'].sort()
        )

    def test__validate_kwargs(self):
        kwargs = {
            'name': 'name',
            'content': 3,
        }

        # raises the validate content has an incorrect value
        with self.assertRaises(FieldError):
            book = Book()
            book._validate(kwargs)
        kwargs['content'] = 'correct content'

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
