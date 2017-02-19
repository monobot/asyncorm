from model import Model
from fields import (CharField, DateField, IntegerField, ForeignKey, ManyToMany,
    PkField
)


class Book(Model):
    name = CharField(max_length=50)
    content = CharField(max_length=255, field_name='hhuhuhuh', )
    silvia = CharField(max_length=25)
    date_created = DateField(auto_now=True)
    room = ForeignKey(foreign_key='Room', null=True)


class Room(Model):
    ok = PkField(field_name='ok')
    name = CharField(max_length=50)
    windows = IntegerField()
    puertas = IntegerField()
    book = ManyToMany(foreign_key='room')
