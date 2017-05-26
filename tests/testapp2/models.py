from asyncorm import fields
from asyncorm import models


class Organization(models.Model):
    name = fields.CharField(max_length=50)
    active = fields.BooleanField(default=False)


class Developer(models.Model):
    name = fields.CharField(max_length=50, unique=True)
    age = fields.IntegerField(default=25)
    org = fields.ManyToManyField(foreign_key='Organization')


class Client(models.Model):
    name = fields.CharField(max_length=10)
    dev = fields.ForeignKey(foreign_key='Developer')


class Appointment(models.Model):
    name = fields.CharField(max_length=50)
    date = fields.DateField()
