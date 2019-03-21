from asyncorm import models


class Organization(models.Model):
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(null=True)
    uuid = models.Uuid4Field(uuid_type="v1", db_index=True)


class Developer(models.Model):
    name = models.CharField(max_length=50, unique=True)
    age = models.IntegerField(default=25)
    org = models.ManyToManyField(foreign_key="Organization")


class Client(models.Model):
    name = models.CharField(max_length=10)
    dev = models.ForeignKey(foreign_key="Developer")
    appointment = models.ForeignKey(foreign_key="Appointment", null=True)


class Appointment(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateField()
    time = models.TimeField(null=True)
    uuid = models.Uuid4Field()


class Skill(models.Model):
    dev = models.ForeignKey(foreign_key="Developer")
    name = models.CharField(max_length=64)
    specialization = models.ArrayField(null=True, value_type="text", db_index=True)
    notes = models.TextField(null=True)
