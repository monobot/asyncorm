from asyncorm.fields import (
    CharField, DateField, ForeignKey, IntegerField, ManyToMany,
)
from asyncorm.model import Model


class Organization(Model):
    name = CharField(max_length=50)


class Developer(Model):
    name = CharField(max_length=50, unique=True)
    age = IntegerField(default=25)
    org = ManyToMany(foreign_key='Organization')


class Client(Model):
    name = CharField(max_length=10)
    dev = ForeignKey(foreign_key='Developer')


class Appointment(Model):
    name = CharField(max_length=50)
    date = DateField()
