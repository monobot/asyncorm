from fields import Field, PkField, CharField, ManyToMany, DateField
from exceptions import ModelError

__all__ = ['Model', 'ModelManager']


class ModelManager(object):
    model = None

    @classmethod
    def queryset(cls):
        pass


class Model(object):
    table_name = ''

    objects = ModelManager()

    def __init__(self, **kwargs):
        # test done
        self.objects.model = self.__class__
        if not self.table_name:
            self.table_name = self.__class__.__name__.lower()
        self.fields, self.field_names, pk_needed = self._get_fields()

        if pk_needed:
            self.__class__.id = PkField()
            self.fk_field = self.__class__.id

            self.fields = [self.id] + self.fields
            self.field_names = ['id'] + self.field_names
        else:
            pk_fields = [f for f in self.fields if isinstance(f, PkField)]
            self.fk_field = pk_fields[0]

        self._validate(kwargs)

        for field_name in self.field_names:
            setattr(
                self,
                field_name,
                kwargs.get(
                    field_name,
                    getattr(self.__class__, field_name).default
                )
            )

        self.kwargs = kwargs

    @classmethod
    def _get_fields(cls):
        # test done
        fields = []
        field_names = []
        for f in cls.__dict__.keys():
            field = getattr(cls, f)
            if isinstance(field, Field):
                field.orm_field_name = f

                if not field.field_name:
                    setattr(field, 'field_name', f)

                if isinstance(field, ManyToMany):
                    setattr(
                        field,
                        'foreign_model',
                        cls.table_name or cls.__name__.lower()
                    )
                    setattr(
                        field,
                        'table_name',
                        '{my_model}_{foreign_key}'.format(
                            my_model=cls.table_name or cls.__name__.lower(),
                            foreign_key=field.field_name,

                        )
                    )

                fields.append(field)
                field_names.append(f)

        pk_needed = False
        if PkField not in [f.__class__ for f in fields]:
            pk_needed = True

        return fields, field_names, pk_needed

    def _validate(self, kwargs):
        '''validate the kwargs on object instantiation only'''
        # test done
        attr_errors = [k for k in kwargs.keys() if k not in self.field_names]

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

    @property
    def _fk_db_fieldname(self):
        '''model foreign_key database fieldname'''
        return self.fk_field.field_name

    @property
    def _fk_orm_fieldname(self):
        '''model foreign_key orm fieldname'''
        return self.fk_field.orm_field_name

    def _creation_query(self):
        return 'CREATE TABLE {table_name} ({field_queries});'.format(
            table_name=self.table_name,
            field_queries=self._get_field_queries(),
        )

    def _get_field_queries(self):
        # builds the table with all its fields definition
        return ', '.join([f._creation_query() for f in self.fields
            if not isinstance(f, ManyToMany)])

    def _get_m2m_field_queries(self):
        # builds the relational 1_to_1 table
        return '; '.join([f._creation_query() for f in self.fields
            if isinstance(f, ManyToMany)]
            )

    def _create_save_string(self, fields, field_data):
        interpolate = ','.join(['{}'] * len(fields))
        save_string = '''
            INSERT INTO {table_name} ({interpolate}) VALUES ({interpolate});
        '''.format(
            table_name=self.__class__.table_name,
            interpolate=interpolate,
        )
        save_string = save_string.format(*tuple(fields + field_data))
        return save_string

    def _update_save_string(self, fields, field_data):
        interpolate = ','.join(['{}'] * len(fields))
        save_string = '''
            UPDATE ONLY {table_name} SET ({interpolate}) VALUES ({interpolate})
            WHERE {_fk_db_fieldname}={model_id};
        '''.format(
            table_name=self.__class__.table_name,
            interpolate=interpolate,
            _fk_db_fieldname=self._fk_db_fieldname,
            model_id=getattr(self, self._fk_orm_fieldname)
        )
        save_string = save_string.format(*tuple(fields + field_data))
        print(save_string)

    def _db_save(self):
        # performs the database save
        fields, field_data = [], []
        for k, data in self.kwargs.items():
            f_class = getattr(self.__class__, k)

            # we add the field_name in db
            fields.append(f_class.field_name or k)
            field_data.append(f_class._sanitize_data(data))

        self._update_save_string(fields, field_data)
        if getattr(self, self._fk_db_fieldname):
            return self._update_save_string(fields, field_data)
        return self._create_save_string(fields, field_data)
