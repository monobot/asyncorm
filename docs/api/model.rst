Model
-----

The model object
~~~~~~~~~~~~~~~~
The model object is the key stone of the orm, it has to reside in the models.py file in each of the modules declared in the orm definition as you already know.

- Each model represents a table in the database (and all the relational tables that asyncOrm will create for them when needed like the ManyToMany relations)
- They should subclass ``asyncorm.models.Model``
- Each column of the model is declared as a separated `Field`_ object (explained later)

Quick example

This example model defines an Author, which has a first_name, last_name and age

.. code-block:: python

    from asyncorm import models
    from asyncorm import fields

    class Author(models.Model):
        first_name = fields.CharField(max_length=30)
        last_name = fields.CharField(max_length=30)
        age = fields.IntegerField()

Someone coming from django will definetly detect a pattern, this is one of the core ideas of asyncOrm, be for those developers with django background.
