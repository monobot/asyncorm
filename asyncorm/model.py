from .log import logger
from .fields import Field, PkField, ManyToMany  # , ForeignKey
from .manager import ModelManager, FieldQueryset
from .exceptions import ModelError, FieldError
from .application import get_model

__all__ = ['Model', ]


class ModelMeta(type):

    def __new__(cls, clsname, bases, clsdict):
        base_class = super().__new__(cls, clsname, bases, clsdict)

        base_class.objects = type(
            "{}Manager".format(base_class.__name__),
            (ModelManager, ),
            {"model": base_class}
        )(base_class)

        defined_meta = clsdict.pop('Meta', None)

        base_class.ordering = None
        base_class.unique_together = []
        base_class._table_name = ''

        if defined_meta:
            if hasattr(defined_meta, 'ordering'):
                base_class.ordering = base_class.check_ordering(
                    getattr(defined_meta, 'ordering')
                )
            if hasattr(defined_meta, 'unique_together'):
                base_class.unique_together = getattr(
                    defined_meta, 'unique_together'
                )
            if hasattr(defined_meta, 'table_name'):
                base_class._table_name = getattr(
                    defined_meta, 'table_name'
                )

        base_class.fields = base_class._get_fields()

        if PkField not in [f.__class__ for f in base_class.fields.values()]:
            base_class.id = PkField()
            base_class.fields['id'] = base_class.id

            base_class._db_pk = 'id'
            base_class._orm_pk = 'id'
        else:
            pk_fields = [
                f for f in base_class.fields.values() if isinstance(f, PkField)
            ]
            base_class._db_pk = pk_fields[0].field_name
            base_class._orm_pk = pk_fields[0].orm_field_name

        for f in base_class.fields.values():
            if f.choices:
                setattr(
                    base_class,
                    '{}_display'.format(f.orm_field_name),
                    'choices_placeholder'
                )

        return base_class

    # @property
    # def var(cls):
    #     return cls._var

    # @var.setter
    # def var(cls, value):
    #     cls._var = value

class BaseModel(object, metaclass=ModelMeta):
    _table_name = ''

    objects = None
    deleted = False

    def __init__(self, **kwargs):
        self._table_name = ''

        logger.debug('initiating model {}'.format(self.__class__.__name__))
        self.objects.model = self.__class__

        manager = getattr(self, 'objects')
        manager.model = self.__class__

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

        self._validate_kwargs(kwargs)

        for field_name in self.fields.keys():
            if hasattr(getattr(self.__class__, field_name), 'default'):
                setattr(
                    self,
                    field_name,
                    kwargs.get(
                        field_name,
                        getattr(self.__class__, field_name).default
                    )
                )
            else:
                setattr(self, field_name, None)

        logger.debug('... initiated')

    @classmethod
    def table_name(cls):
        return cls._table_name or cls.__name__

    @classmethod
    def _set_reverse_foreignkey(cls, model_name, field_name):
        async def fk_set(self):
            model = get_model(model_name)

            return await model.objects.filter(
                **{field_name: getattr(self, self._orm_pk)}
            )

        setattr(cls, '{}_set'.format(model_name.lower()), fk_set)

    @classmethod
    def _set_many2many(cls, field, table_name, my_column, other_column,
                       direct=False):
        other_model = cls.objects.orm.get_model(other_column)
        queryset = FieldQueryset(field, other_model)
        queryset._set_orm(cls.objects.orm)

        async def m2m_set(self):
            m2m_filter = {
                'm2m_tablename': table_name,
                'other_tablename': other_column,
                'other_db_pk': other_model._db_pk,
                'id_data': '{}={}'.format(
                    my_column, getattr(self, self._orm_pk)
                ),
            }
            return await queryset.filter_m2m(m2m_filter)

        method_name = (
            direct and field.field_name or
            '{}_set'.format(other_column.lower())
        )
        setattr(cls, method_name, m2m_set)

    @classmethod
    def _set_orm(cls, orm):
        cls.objects._set_orm(orm)

    @property
    def data(self):
        d = {}
        created = bool(self._orm_pk)

        for orm, db in self.__class__._attr_names:
            class__orm = getattr(self.__class__, orm)
            self__orm = getattr(self, orm)

            has_pk = self._orm_pk == orm
            many2many = isinstance(class__orm, ManyToMany)

            if not has_pk and not many2many:
                d[db] = self__orm

                default = self__orm == class__orm.default
                if created and default:
                    d.pop(db)

        return d

    @property
    def m2m_data(self):
        d = {}

        for orm, db in self.__class__._attr_names:
            class__orm = getattr(self.__class__, orm)
            if isinstance(class__orm, ManyToMany):
                self__orm = getattr(self, orm)
                d[db] = self__orm

                default = self__orm == class__orm.default
                if bool(self._orm_pk) and default:
                    d.pop(db)
        return d

    @classmethod
    def _get_fields(cls):
        fields = {}

        cls._attr_names = []
        for f_n, field in cls.__dict__.items():
            if isinstance(field, Field):
                field.orm_field_name = f_n

                if not field.field_name:
                    field._set_field_name(f_n)

                if not field.table_name:
                    field.table_name = cls.table_name()

                if isinstance(field, ManyToMany):
                    field.own_model = cls.table_name()
                    field.table_name = '{my_model}_{foreign_key}'.format(
                        my_model=cls.table_name(),
                        foreign_key=field.foreign_key,
                    )

                if not isinstance(field.__class__, PkField):
                    cls._attr_names.append((f_n, field.field_name))

                fields[f_n] = field
            # elif callable(field):
            #     if hasattr(field, 'field'):
            #         print('##############', f_n, field.__class__)

        if len(cls._attr_names) != len(set(cls._attr_names)):
            raise ModelError(
                'Models should have unique attribute names and '
                'field_name if explicitly edited!'
            )

        return fields

    def _validate_kwargs(self, kwargs):
        '''validate the kwargs on object instantiation only'''
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

    @classmethod
    def check_ordering(cls, ordering):
        for f in ordering:
            if f.startswith('-'):
                f = f[1:]
            if f not in cls.fields.keys():
                raise ModelError(
                    'Meta\'s ordering refers to a field '
                    '{} not defined in the model'.format(f)
                )
        return ordering


class Model(BaseModel):

    # def __init__(self):
    #     self.table_name = self.__class__._table_name or self.__class__.__name__

    def _construct(self, data, deleted=False):
        # poblates the model with the data
        for k, v in data.items():
            setattr(self, k, v)
        self.deleted = deleted
        return self

    async def save(self):
        # external save method
        if not self.deleted:
            await self.objects.save(self)
        else:
            raise ModelError(
                'That {model_name} has already been deleted!'.format(
                    model_name=self.__class__.__name__
                )
            )

    async def delete(self):
        # object delete method
        self.deleted = True
        return await self.objects.delete(self)

    def __str__(self):
        return '< {} object >'.format(self.__class__.__name__)

    def __repr__(self):
        return '< {} object >'.format(self.__class__.__name__)
