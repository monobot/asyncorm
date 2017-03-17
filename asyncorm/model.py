from .log import logger
from .fields import Field, PkField, ManyToMany  # , ForeignKey
from .manager import ModelManager
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
        )()

        defined_meta = clsdict.pop('Meta', None)

        base_class.fields = base_class._get_fields()

        pk_needed = False
        if PkField not in [f.__class__ for f in base_class.fields.values()]:
            pk_needed = True

        if pk_needed:
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

        base_class._ordering = None
        base_class._unique_together = []
        if defined_meta:
            if hasattr(defined_meta, 'ordering'):
                base_class._ordering = base_class.check_ordering(
                    getattr(defined_meta, 'ordering')
                )
            if hasattr(defined_meta, 'unique_together'):
                base_class._unique_together = getattr(
                    defined_meta, 'unique_together'
                )

        return base_class


class BaseModel(object, metaclass=ModelMeta):
    table_name = ''

    objects = None
    deleted = False

    def __init__(self, **kwargs):
        logger.debug('initiating model {}'.format(self.__class__.__name__))
        self.objects.model = self.__class__

        if not self.table_name:
            self.table_name = self.__class__.__name__
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

        logger.debug('... initiated')

    @classmethod
    def _set_reverse_foreignkey(cls, model_name, field_name):
        async def fk_set(self):
            model = get_model(model_name)

            return await model.objects.filter(
                **{field_name: getattr(self, self._orm_pk)}
            )

        setattr(cls, '{}_set'.format(model_name.lower()), fk_set)

    @classmethod
    def _set_manytomany(cls, table_name, my_column, other_column):
        from .manager import Queryset

        queryset = Queryset()
        queryset._set_orm(cls.objects.orm)
        queryset._model_tablename = table_name
        queryset._return_modelname = other_column

        async def m2m_set(self):
            m2m_filter = {my_column: getattr(self, self._orm_pk)}
            return await queryset.filter(**m2m_filter)

        setattr(cls, '{}_set'.format(other_column.lower()), m2m_set)

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
                    setattr(
                        field,
                        'table_name',
                        '{my_model}_{foreign_key}'.format(
                            my_model=cls.table_name,
                            foreign_key=field.foreign_key,
                        )
                    )

                if not isinstance(field.__class__, PkField):
                    cls._attr_names.append((f, field.field_name))

                fields[f] = field

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
        # external delete method
        self.deleted = True
        return await self.objects.delete(self)

    def __str__(self):
        return '< {} object >'.format(self.__class__.__name__)

    def __repr__(self):
        return '< {} object >'.format(self.__class__.__name__)
