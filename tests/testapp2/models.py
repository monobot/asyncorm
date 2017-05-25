from asyncorm.fields import (
    CharField, DateField, ForeignKey, IntegerField, ManyToMany, BooleanField,
)
from asyncorm import models


class Organization(models.Model):
    name = CharField(max_length=50)
    active = BooleanField(default=False)


class Developer(models.Model):
    name = CharField(max_length=50, unique=True)
    age = IntegerField(default=25)
    org = ManyToMany(foreign_key='Organization')


class Client(models.Model):
    name = CharField(max_length=10)
    dev = ForeignKey(foreign_key='Developer')


class Appointment(models.Model):
    name = CharField(max_length=50)
    date = DateField()
