from asyncorm.fields import *
from asyncorm.model import Model


class Organization(Model):
    name = CharField(max_length=50)


class Program(Model):
    name = CharField(max_length=50)
    content = CharField(max_length=255)
    date_created = DateField(auto_now=True)
    developer = ForeignKey(foreign_key='Developer', null=True)

    class Meta():
        ordering = ['-id']
        unique_together = ['name', 'content']


class Developer(Model):
    na = PkField(field_name='uid')
    name = CharField(max_length=50, unique=True)
    age = IntegerField()
    publisher = ManyToMany(foreign_key='Organization')
