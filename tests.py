import unittest

from exceptions import ModelError, FieldError
from test_models.models import Book


class ModelTests(unittest.TestCase):

    def test_init(self):
        # self.assertEqual(Book().table_name, 'library')
        # self.assertEqual(Author().table_name, 'author')

        fields, field_names = Book.get_fields()

        self.assertEqual(len(fields), 5)
        self.assertEqual(len(field_names), 5)

        self.assertEqual(
            field_names.sort(),
            ['id', 'content', 'name', 'author', 'date_created'].sort()
        )

    def test_validate_kwargs(self):
        kwargs = {
            'name': 'name',
            'content': 3,
        }

        # raises the validate content has an incorrect value
        with self.assertRaises(FieldError):
            book = Book()
            book.validate(kwargs)
        kwargs['content'] = 'correct content'

        kwargs['volume'] = 23
        # raises the validate error because volume is not a correct attrib
        with self.assertRaises(ModelError):
            book = Book()
            book.validate(kwargs)
        kwargs.pop('volume')

        # now it correctly validates
        book.validate(kwargs)


if __name__ == '__main__':
    unittest.main()
