Field
-----

The field object
~~~~~~~~~~~~~~~~
The fields define each of the columns for the `Model`_ object.

You can define your own Field types, they should in that case subclass ``asyncorm.fields.Field``

There are a number of already existing FieldTypes:

PkField
~~~~~~~

BooleanField
~~~~~~~~~~~~

CharField
~~~~~~~~~

EmailField
~~~~~~~~~~

JsonField
~~~~~~~~~

NumberField
~~~~~~~~~~~

IntegerField
~~~~~~~~~~~~

DecimalField
~~~~~~~~~~~~

DateField
~~~~~~~~~

ForeignKey
~~~~~~~~~~

ManyToManyField
~~~~~~~~~~~~~~~
