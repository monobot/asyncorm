from asyncorm import models


class AsyncormMigrations(models.Model):
    app_name = models.CharField(max_length=75)
    name = models.CharField(max_length=75)
    applied = models.DateTimeField(auto_now=True)

    class Meta:
        table_name = "asyncorm_migrations"
