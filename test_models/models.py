from model import Model
from field import CharField, DateField, IntegerField, ForeignKey, ManyToMany


class Book(Model):
    name = CharField(max_length=50)
    content = CharField(max_length=255, field_name='hhuhuhuh', )
    silvia = CharField(max_length=25)
    date_created = DateField(auto_now=True)
    room = ForeignKey(foreign_key='Room', null=True)


class Room(Model):
    name = CharField(max_length=50)
    windows = IntegerField()
    puertas = IntegerField()
    book = ManyToMany(foreign_key='room')
