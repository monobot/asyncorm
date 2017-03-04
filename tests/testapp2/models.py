from asyncorm.fields import *
from asyncorm.model import Model


class Organization(Model):
    name = CharField(max_length=50)


class Developer(Model):
    na = PkField(field_name='uid')
    name = CharField(max_length=50, unique=True)
    age = IntegerField()
    # org = ManyToMany(foreign_key='Organization')
