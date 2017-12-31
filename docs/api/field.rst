Field
-----

The field object
~~~~~~~~~~~~~~~~
The fields define each of the columns for the `Model`_ object.

You can define your own Field types, they should in that case subclass ``asyncorm.fields.Field``

There are a number of already existing FieldTypes:

BooleanField
~~~~~~~~~~~~~~~

CharField
~~~~~~~~~~~~~~~

EmailField
~~~~~~~~~~~~~~~

TextField
~~~~~~~~~~~~~~~

NumberField
~~~~~~~~~~~~~~~

IntegerField
~~~~~~~~~~~~~~~

DecimalField
~~~~~~~~~~~~~~~

AutoField
~~~~~~~~~~~~~~~

DateTimeField
~~~~~~~~~~~~~~~

DateField
~~~~~~~~~~~~~~~

TimeField
~~~~~~~~~~~~~~~

ForeignKey
~~~~~~~~~~~~~~~

ManyToManyField
~~~~~~~~~~~~~~~

JsonField
~~~~~~~~~~~~~~~

Uuid4Field
~~~~~~~~~~~~~~~

ArrayField
~~~~~~~~~~~~~~~

GenericIPAddressField
~~~~~~~~~~~~~~~

MACAdressField
~~~~~~~~~~~~~~~

