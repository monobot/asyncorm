from asyncorm.fields import *
from asyncorm.model import Model


class RefPublisher(Model):
    name = CharField(max_length=50)


class Disc(Model):
    name = CharField(max_length=50)
    content = CharField(max_length=255)
    date_created = DateField(auto_now=True)
    band = ForeignKey(foreign_key='Band', null=True)

    class Meta():
        ordering = ['-id']
        unique_together = ['name', 'content']


class Band(Model):
    na = PkField(field_name='uid')
    name = CharField(max_length=50, unique=True)
    age = IntegerField()
    publisher = ManyToMany(foreign_key='RefPublisher')
