from model import Model
from fields import (CharField, DateField, IntegerField, ForeignKey,
    ManyToMany, PkField
)

__all__ = ('Publisher', 'Book', 'Author')

BOOK_CHOICES = (
    ('tapa dura', 'libro de tapa dura'),
    ('tapa blanda', 'libro de tapa blanda')
)


class Publisher(Model):
    name = CharField(max_length=50)


class Book(Model):
    table_name = 'library'
    name = CharField(max_length=50)
    content = CharField(max_length=255, choices=BOOK_CHOICES)
    date_created = DateField(auto_now=True)
    author = ForeignKey(foreign_key='Author', null=True)

    def mi_nombre(self):
        return ('es mi nombre: {}'.format(self.name)) * 20


class Author(Model):
    na = PkField(field_name='uid')
    name = CharField(max_length=50)
    age = IntegerField()
    publisher = ManyToMany(foreign_key='Publisher')
