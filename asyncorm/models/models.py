import inspect
import os
from pprint import pprint

from .fields import Field, PkField, ManyToManyField, ForeignKey
from ..manager import ModelManager
from ..exceptions import ModelError, FieldError, ModelDoesNotExist
from ..application import get_model

from ..serializers import ModelSerializer, SerializerMethod

__all__ = ['Model', 'ModelSerializer', 'SerializerMethod']


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
        base_class.table_name = ''
        base_class.DoesNotExist = ModelDoesNotExist

        if defined_meta:
            if hasattr(defined_meta, 'ordering'):
                base_class.ordering = getattr(defined_meta, 'ordering')
            if hasattr(defined_meta, 'unique_together'):
                base_class.unique_together = getattr(
                    defined_meta, 'unique_together'
                )
            if hasattr(defined_meta, 'table_name'):
                base_class.table_name = getattr(
                    defined_meta, 'table_name'
                )

        base_class.fields = base_class.get_fields()

        if PkField not in [f.__class__ for f in base_class.fields.values()]:
            base_class.id = PkField()
            base_class.fields['id'] = base_class.id

            base_class.db_pk = 'id'
            base_class.orm_pk = 'id'
        else:
            pk_fields = [
                f for f in base_class.fields.values() if isinstance(f, PkField)
            ]
            base_class.db_pk = pk_fields[0].db_column
            base_class.orm_pk = pk_fields[0].orm_field_name

        for f in base_class.fields.values():
            if hasattr(f, 'choices'):
                if f.choices:
                    setattr(base_class,
                            '{}_display'.format(f.orm_field_name),
                            'choices_placeholder'
                            )
        return base_class


class BaseModel(object, metaclass=ModelMeta):
    table_name = ''

    objects = None
    deleted = False

    def __init__(self, **kwargs):
        dir_name = os.path.dirname(inspect.getmodule(self).__file__)
        self.app_name = dir_name.split(os.path.sep)[-1]
        self.migrations_dir = os.path.join(dir_name, 'migrations')
        os.makedirs(self.migrations_dir, exist_ok=True)

        self.table_name = ''

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

        self.validate_kwargs(kwargs)

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

    @classmethod
    def cls_tablename(cls):
        return cls.table_name or cls.__name__

    @classmethod
    def set_reverse_foreignkey(cls, model_name, field_name):
        def fk_set(self):
            model = get_model(model_name)

            return model.objects.filter(
                **{field_name: getattr(self, self.orm_pk)}
            )

        setattr(cls, '{}_set'.format(model_name.lower()), fk_set)

    @classmethod
    def set_many2many(cls, field, table_name, my_column, other_column,
                      direct=False):
        other_model = get_model(other_column)
        queryset = ModelManager(other_model, field=field)
        queryset.set_orm(cls.objects.orm)

        def m2m_set(self):
            queryset.query = [{
                'action': 'db__select_m2m',
                'select': '*',
                'm2m_tablename': table_name,
                'other_tablename': other_column,
                'otherdb_pk': other_model.db_pk,
                'id_data': '{}={}'.format(
                    my_column, getattr(self, self.orm_pk)
                ),
            }]
            return queryset

        method_name = (
            direct and field.field_name or
            '{}_set'.format(other_column.lower())
        )
        setattr(cls, method_name, m2m_set)

    @classmethod
    def set_orm(cls, orm):
        cls.objects.set_orm(orm)

    @property
    def data(self):
        d = {}
        created = bool(self.orm_pk)

        for orm, db in self.__class__.attr_names.items():
            class__orm = getattr(self.__class__, orm)
            self__orm = getattr(self, orm)

            has_pk = self.orm_pk == orm
            many2many = isinstance(class__orm, ManyToManyField)

            if not has_pk and not many2many:
                d[db] = self__orm

                default = self__orm == class__orm.default
                if created and default:
                    d.pop(db)

        return d

    @property
    def m2m_data(self):
        d = {}

        for orm, db in self.__class__.attr_names.items():
            class__orm = getattr(self.__class__, orm)
            if isinstance(class__orm, ManyToManyField):
                self__orm = getattr(self, orm)
                d[db] = self__orm

                default = self__orm == class__orm.default
                if bool(self.orm_pk) and default:
                    d.pop(db)
        return d

    @classmethod
    def get_fields(cls):
        fields = {}

        cls.attr_names = {}
        for f_n, field in cls.__dict__.items():
            if isinstance(field, Field):
                field.orm_field_name = f_n

                if not field.db_column:
                    field.set_field_name(f_n)

                if not field.table_name:
                    field.table_name = cls.cls_tablename()

                if isinstance(field, ManyToManyField):
                    field.own_model = cls.cls_tablename()
                    field.table_name = '{my_model}_{foreign_key}'.format(
                        my_model=cls.cls_tablename(),
                        foreign_key=field.foreign_key,
                    )

                if not isinstance(field.__class__, PkField):
                    cls.attr_names.update({f_n: field.db_column})

                fields[f_n] = field

        if len(cls.attr_names) != len(set(cls.attr_names)):
            raise ModelError(
                'Models should have unique attribute names and '
                'field_name if explicitly edited!'
            )

        return fields

    @classmethod
    def get_db_columns(cls):
        db_columns = []

        for f_n, field in cls.__dict__.items():
            is_many2many = isinstance(field, ManyToManyField)
            is_field = isinstance(field, Field)

            if is_field and not is_many2many:
                db_columns.append(field.db_column and field.db_column or f_n)

        return db_columns

    def validate_kwargs(self, kwargs):
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
            att_field = getattr(self.__class__, k)
            att_field.validate(v)

            if att_field.__class__ is PkField and v:
                raise FieldError('Models can not be generated with forced id')

    def migration_queries(self):
        migration_queries = [self.objects.create_table_builder(), ]

        for f in self.fields.values():
            if isinstance(f, ForeignKey):
                migration_queries.append(
                    self.objects.add_fk_field_builder(f)
                )

        for f in self.fields.values():
            if isinstance(f, ManyToManyField):
                migration_queries.append(
                    self.objects.add_m2m_columns_builder(f)
                )

        migration_queries.append(self.objects.unique_together_builder())
        return migration_queries

    async def check_migration(self):
        index = 1
        filenames = next(os.walk(self.migrations_dir))[2]

        if filenames:
            prev_migration = (sorted(filenames))[-1]
        else:
            prev_migration = None

        if prev_migration is not None:
            try:
                index = int(prev_migration.split('.')[0])
            except AttributeError:
                raise ModelError(
                    'Wrong filename for migration {}'.format(prev_migration)
                )

        # here i can get the latest migration name for this app
        db_migration = await self.objects.latest_migration()

        if db_migration is not None and int(db_migration) > index:
            return

        return os.path.join(
            self.migrations_dir,
            ('0000{}.py'.format(index + 1)[-7:])
        )

    async def make_migration(self):
        migration_file = await self.check_migration()
        with open(migration_file, 'w+') as file:
            pprint(
                {
                    'migrations': self.migration_queries(),
                    'state': self.__class__.current_state(),
                },
                stream=file,
                width=79
            )

    @classmethod
    def current_state(cls):
        from copy import deepcopy

        fields = deepcopy(cls.get_fields())
        for f_n, field in fields.items():
            fields[f_n] = field.current_state()

        return {
            'fields': fields,
            'meta': {}
        }


class Model(BaseModel):

    def construct(self, data, deleted=False, subitems=None):
        # poblates the model with the data
        internal_objects = {}
        for k, v in data.items():
            k_splitted = k.split('€$$€')
            if len(k_splitted) == 1:
                # check if its named different in the database than the orm
                if k not in self.__class__.attr_names.keys():
                    for orm, db in self.__class__.attr_names.items():
                        if k == db:
                            k = orm
                            break
                # get the recomposed value
                field_class = getattr(self.__class__, k)
                v = field_class.recompose(v)

                if field_class in [ForeignKey, ManyToManyField]:
                    pass
                setattr(self, k, v)
            else:
                # itself or empty dict
                internal_objects[k_splitted[0]] = internal_objects.get(
                    k_splitted[0],
                    {}
                )

                # update the new value
                internal_objects[k_splitted[0]].update({k_splitted[1]: v})

        if internal_objects:
            for attr_name, data in internal_objects.items():
                if hasattr(self, attr_name):
                    if getattr(self, attr_name):
                        field = getattr(self.__class__, attr_name)
                        model = get_model(field.foreign_key)

                        setattr(self, attr_name, model().construct(data))
                else:
                    for join in subitems[0]['fields']:
                        if join['right_table'] == attr_name:
                            field = getattr(
                                self.__class__,
                                join['orm_fieldname']
                            )
                            model = get_model(field.foreign_key)

                            setattr(
                                self, join['orm_fieldname'],
                                model().construct(data)
                            )
                            break

        self.deleted = deleted
        return self

    async def save(self, **kwargs):
        # external save method
        if self.deleted:
            raise ModelError(
                'That {model_name} has already been deleted!'.format(
                    model_name=self.__class__.__name__
                )
            )
        await self.objects.save(self)

    async def delete(self):
        # object delete method
        self.deleted = True
        return await self.objects.delete(self)

    def __str__(self):
        return '< {} object >'.format(self.__class__.__name__)

    def __repr__(self):
        return self.__str__
