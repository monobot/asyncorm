from asyncorm.fields import *
from asyncorm.model import Model

BOOK_CHOICES = (
    ('hard cover', 'hard cover book'),
    ('paperback', 'paperback book')
)


class Publisher(Model):
    name = CharField(max_length=50)


class Book(Model):
    table_name = 'library'
    name = CharField(max_length=50)
    content = CharField(max_length=255, choices=BOOK_CHOICES)
    date_created = DateField(auto_now=True)
    author = ForeignKey(foreign_key='Author', null=True)

    class Meta():
        ordering = ['-id']
        unique_together = ['name', 'content']


class Author(Model):
    na = PkField(field_name='uid')
    name = CharField(max_length=50, unique=True)
    age = IntegerField()
    publisher = ManyToMany(foreign_key='Publisher')
