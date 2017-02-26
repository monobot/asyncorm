from fields import Field, PkField, ManyToMany
from manager import ModelManager

from exceptions import ModelError, FieldError
from log import logger

__all__ = ['Model', ]


class ModelMeta(type):

    def __new__(cls, clsname, bases, clsdict):
        base_class = super().__new__(cls, clsname, bases, clsdict)

        base_class.objects = type(
            "{}Manager".format(base_class.__name__),
            (ModelManager, ),
            {"model": base_class}
        )()

        fields = base_class._get_fields()

        for f in fields.values():
            if f.choices:
                setattr(
                    base_class,
                    '{}_display'.format(f.orm_field_name),
                    'choices_placeholder'
                )

        return base_class


class BaseModel(object, metaclass=ModelMeta):
    table_name = ''

    objects = None
    deleted = False

    def __init__(self, **kwargs):
        logger.debug('initiating model {}'.format(self.__class__.__name__))
        # test done
        self.objects.model = self.__class__

        if not self.table_name:
            self.table_name = self.__class__.__name__.lower()
            self.__class__.table_name = self.table_name

        manager = getattr(self, 'objects')
        manager.model = self.__class__

        self.__class__.fields = self.__class__._get_fields()

        # resolve method for posible display methods
        for k, v in self.__class__.__dict__.items():
            if v == 'choices_placeholder':
                field_name = k.split('_display')[0]
                field = getattr(self.__class__, field_name)

                def new_func(field=field, field_name=field_name):
                    value = getattr(self, field_name)
                    for a, b in field.choices.items():
                        if a == value:
                            return b

                setattr(self, k, new_func)

        pk_needed = False
        if PkField not in [f.__class__ for f in self.fields.values()]:
            pk_needed = True

        if pk_needed:
            self.__class__.id = PkField()
            setattr(self.__class__.id, 'orm_field_name', 'id')
            self.fk_field = self.__class__.id

            self.fields['id'] = self.__class__.id
        else:
            pk_fields = [
                f for f in self.fields.values() if isinstance(f, PkField)
            ]
            self.fk_field = pk_fields[0]

        self._validate_kwargs(kwargs)

        for field_name in self.fields.keys():
            setattr(
                self,
                field_name,
                kwargs.get(
                    field_name,
                    getattr(self.__class__, field_name).default
                )
            )

        self.data = kwargs
        logger.debug('... initiated')

    @classmethod
    def _get_fields(cls):
        # test done
        fields = {}

        attr_names = []
        for f in cls.__dict__.keys():
            field = getattr(cls, f)
            if isinstance(field, Field):
                field.orm_field_name = f

                if not field.field_name:
                    field._set_field_name(f)

                if not field.table_name:
                    field.table_name = cls.table_name

                if isinstance(field, ManyToMany):
                    setattr(field, 'foreign_model', cls.table_name)
                    setattr(field, 'table_name',
                        '{my_model}_{foreign_key}'.format(
                            my_model=cls.table_name,
                            foreign_key=field.field_name,

                        )
                    )

                fields[f] = field
                attr_names.append(field.field_name)

        if len(attr_names) != len(set(attr_names)):
            raise ModelError(
                'Models should have unique attribute names and '
                'field_name if explicitly edited!'
            )

        return fields

    def _validate_kwargs(self, kwargs):
        '''validate the kwargs on object instantiation only'''
        # test done
        attr_errors = [k for k in kwargs.keys() if k not in self.fields.keys()]

        if attr_errors:
            err_string = '"{}" is not an attribute for {}'
            error_list = [
                err_string.format(k, self.__class__.__name__)
                for k in attr_errors
            ]
            raise ModelError(error_list)

        for k, v in kwargs.items():
            att_class = getattr(self.__class__, k).__class__
            att_class._validate(v)
            if att_class is PkField and v:
                raise FieldError('Models can not be generated with forced id')

    @property
    def _fk_db_fieldname(self):
        '''model foreign_key database fieldname'''
        return self.fk_field.field_name

    @property
    def _fk_orm_fieldname(self):
        '''model foreign_key orm fieldname'''
        return self.fk_field.orm_field_name

    def _creation_query(self):
        constraints = self._get_field_constraints()

        query = (
            'CREATE TABLE {table_name} ({field_queries});{constraints}{ending}'
        ).format(
            table_name=self.table_name,
            field_queries=self._get_field_queries(),
            constraints=constraints,
            ending=constraints and ';' or '',
        )
        return query

    def _get_field_queries(self):
        # builds the table with all its fields definition
        return ', '.join([f._creation_query() for f in self.fields.values()
            if not isinstance(f, ManyToMany)])

    def _get_field_constraints(self):
        # builds the table with all its fields definition
        return '; '.join(
            [f._field_constraints() for f in self.fields.values()]
        )

    def _get_m2m_field_queries(self):
        # builds the relational 1_to_1 table
        return '; '.join([f._creation_query() for f in self.fields.values()
            if isinstance(f, ManyToMany)]
            )

    def __str__(self):
        return '< {} object >'.format(self.__class__.__name__)

    def __repr__(self):
        return '< {} object >'.format(self.__class__.__name__)


class Model(BaseModel):

    def _construct(self, data, deleted=False):
        # poblates the model with the data
        for k, v in data.items():
            setattr(self, k, v)
        self.deleted = deleted
        return self

    async def save(self):
        # external save method
        if not self.deleted:
            return await self.objects.save(self)
        else:
            raise ModelError(
                'That {model_name} has already been deleted!'.format(
                    model_name=self.__class__.__name__
                )
            )

    async def delete(self):
        # external delete method
        self.deleted = True
        return await self.objects.delete(self)
