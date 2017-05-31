from ..models import Model
from ..fields import CharField, DateField


class AsyncormMigrations(Model):
    app = CharField(max_length=75)
    name = CharField(max_length=75)
    applied = DateField(auto_now=True)

    class Meta():
        ordering = ('-id', )
        table_name = 'asyncorm_migrations'
