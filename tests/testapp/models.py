from asyncorm import fields
from asyncorm import models

BOOK_CHOICES = (
    ('hard cover', 'hard cover book'),
    ('paperback', 'paperback book')
)


SIZE_CHOICES = (
    ('XS', 'XS'),
    ('S', 'S'),
    ('M', 'M'),
    ('L', 'L'),
    ('XL', 'XL'),
)
POWER_CHOICES = {
    'neo': 'feo',
    'pow': 'dow',
    'saw': 'mao',
}


def weight():
    return 85


class Publisher(models.Model):
    name = fields.CharField(max_length=50)
    json = fields.JsonField(max_length=50, null=True)


class Author(models.Model):
    na = fields.PkField(db_column='uid')
    name = fields.CharField(max_length=50, unique=True)
    email = fields.EmailField(max_length=100, null=True)
    age = fields.IntegerField()
    publisher = fields.ManyToManyField(foreign_key='Publisher')


class Book(models.Model):
    name = fields.CharField(max_length=50)
    content = fields.CharField(max_length=255, choices=BOOK_CHOICES)
    date_created = fields.DateField(auto_now=True)
    author = fields.ForeignKey(foreign_key='Author', null=True)
    price = fields.DecimalField(default=25)
    quantity = fields.IntegerField(default=1)

    def its_a_2(self):
        return 2

    class Meta():
        table_name = 'library'
        ordering = ['-id', ]
        unique_together = ['name', 'content']


class Reader(models.Model):
    name = fields.CharField(max_length=15, default='pepito')
    size = fields.CharField(choices=SIZE_CHOICES, max_length=2)
    power = fields.CharField(choices=POWER_CHOICES, max_length=2, null=True)
    weight = fields.IntegerField(default=weight)
