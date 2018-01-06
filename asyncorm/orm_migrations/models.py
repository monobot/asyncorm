from asyncorm import models


class AsyncormMigrations(models.Model):
    app = models.CharField(max_length=75)
    name = models.CharField(max_length=75)
    applied = models.DateField(auto_now=True)

    class Meta():
        ordering = ('-id', )
        table_name = 'asyncorm_migrations'
